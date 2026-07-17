import hashlib
import uuid
import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct, VectorParams, Distance
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = structlog.get_logger()

class StructuredProfileStore:
    """
    Manages Qdrant collections for Structured Entity Profiles, Entity Registry, and Brand Aliases.
    """
    def __init__(self, client: Optional[QdrantClient] = None, mode: Optional[str] = None, path: Optional[str] = None, url: Optional[str] = None, api_key: Optional[str] = None):
        self.mode = mode or settings.VECTOR_DB_MODE
        self.path = path or settings.QDRANT_PATH
        self.url = url or settings.QDRANT_URL
        self.api_key = api_key or settings.QDRANT_API_KEY
        
        if client:
            self.client = client
        elif self.mode == "local":
            self.client = QdrantClient(path=self.path)
        else:
            if self.api_key:
                self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=60.0)
            else:
                self.client = QdrantClient(url=self.url, timeout=60.0)
            
        self.registry_col = "entity_registry"
        self.profiles_col = "drug_profiles"
        self.aliases_col = "drug_aliases"
        
        # In-process cache for O(1) brand-to-generic lookup
        self.aliases_cache: Dict[str, str] = {}
        
    def initialize_collections(self):
        """
        Ensures registry, profile, and alias collections exist in Qdrant.
        To maintain compatibility across all Qdrant versions, we use a tiny dummy vector size of 1.
        """
        logger.info("initializing_profile_store_collections")
        for col in [self.registry_col, self.profiles_col, self.aliases_col]:
            try:
                if not self.client.collection_exists(col):
                    self.client.create_collection(
                        collection_name=col,
                        vectors_config=VectorParams(size=1, distance=Distance.COSINE)
                    )
                    logger.info("created_qdrant_collection", collection=col)
            except Exception as e:
                logger.error("failed_creating_collection", collection=col, error=str(e))
                
    def get_deterministic_uuid(self, key_str: str) -> str:
        """
        Generate a stable UUID5 based on a string key.
        """
        namespace = uuid.NAMESPACE_DNS
        return str(uuid.uuid5(namespace, key_str))
        
    def upsert_registry_entry(self, entity_id: str, generic_name: str, preferred_authority: str = "FDA", version: int = 1, aliases: List[str] = []):
        """
        Upsert entry into entity_registry.
        """
        uid = self.get_deterministic_uuid(entity_id)
        payload = {
            "entity_id": entity_id,
            "entity_type": "drug",
            "generic_name": generic_name,
            "preferred_authority": preferred_authority,
            "active_profile_version": version,
            "aliases": aliases
        }
        try:
            self.client.upsert(
                collection_name=self.registry_col,
                points=[PointStruct(id=uid, vector=[0.0], payload=payload)]
            )
            logger.info("upserted_registry_entry", entity_id=entity_id, version=version)
        except Exception as e:
            logger.error("failed_upserting_registry_entry", entity_id=entity_id, error=str(e))
            
    def upsert_profile(self, entity_id: str, profile_type: str, authority: str, data: Dict[str, Any], checksum: str, version: int):
        """
        Upsert entry into drug_profiles (separated by type and authority).
        """
        key_str = f"{entity_id}_{profile_type}_{authority}".lower()
        uid = self.get_deterministic_uuid(key_str)
        payload = {
            "entity_id": entity_id,
            "profile_type": profile_type,
            "authority": authority,
            "checksum": checksum,
            "version": version,
            "data": data
        }
        try:
            self.client.upsert(
                collection_name=self.profiles_col,
                points=[PointStruct(id=uid, vector=[0.0], payload=payload)]
            )
            logger.info("upserted_drug_profile", entity_id=entity_id, profile_type=profile_type, authority=authority, version=version)
        except Exception as e:
            logger.error("failed_upserting_drug_profile", entity_id=entity_id, profile_type=profile_type, error=str(e))
            
    def upsert_alias(
        self, 
        alias: str, 
        entity_id: str, 
        generic: str = "", 
        country: str = "US", 
        authority: str = "FDA", 
        source: str = "OpenFDA", 
        alias_type: str = "brand"
    ):
        """
        Upsert entry into drug_aliases with rich metadata.
        """
        key_str = f"alias_{alias}".lower()
        uid = self.get_deterministic_uuid(key_str)
        payload = {
            "alias": alias,
            "entity_id": entity_id,
            "generic": generic or entity_id.replace("drug:", "").capitalize(),
            "country": country,
            "authority": authority,
            "source": source,
            "type": alias_type
        }
        # Check for conflicts before upserting
        try:
            res = self.client.retrieve(
                collection_name=self.aliases_col,
                ids=[uid],
                with_payload=True
            )
            if res:
                existing_payload = res[0].payload
                existing_entity = existing_payload.get("entity_id")
                if existing_entity and existing_entity != entity_id:
                    existing_generic = existing_payload.get("generic", existing_entity)
                    logger.warning(
                        "alias_conflict_detected",
                        alias=alias,
                        existing_entity=existing_entity,
                        incoming_entity=entity_id,
                        existing_generic=existing_generic,
                        incoming_generic=generic
                    )
                    # Write to docs/ALIAS_CONFLICTS.md
                    import os
                    os.makedirs("docs", exist_ok=True)
                    conflict_file = "docs/ALIAS_CONFLICTS.md"
                    entry = f"\n| `{alias}` | `{existing_generic}` (`{existing_entity}`) | `{generic}` (`{entity_id}`) | `{authority}` / `{source}` |"
                    if not os.path.exists(conflict_file):
                        with open(conflict_file, "w", encoding="utf-8") as f:
                            f.write("# Alias Conflicts Report\n\n| Conflicting Alias | Existing Generic | Incoming Generic | Authority / Source |\n| --- | --- | --- | --- |\n")
                    
                    # Read to verify if entry is already logged
                    with open(conflict_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    if entry.strip() not in content:
                        with open(conflict_file, "a", encoding="utf-8") as f:
                            f.write(entry)
        except Exception as e:
            logger.error("failed_checking_alias_conflict", alias=alias, error=str(e))

        try:
            self.client.upsert(
                collection_name=self.aliases_col,
                points=[PointStruct(id=uid, vector=[0.0], payload=payload)]
            )
            # Update local cache
            self.aliases_cache[alias.lower()] = entity_id
        except Exception as e:
            logger.error("failed_upserting_alias", alias=alias, entity_id=entity_id, error=str(e))
            
    def load_aliases_cache(self):
        """
        Retrieves all brand aliases from Qdrant and caches them in memory.
        """
        logger.info("loading_aliases_cache")
        try:
            self.aliases_cache.clear()
            limit = 1000
            offset = None
            
            while True:
                scroll_res = self.client.scroll(
                    collection_name=self.aliases_col,
                    limit=limit,
                    with_payload=True,
                    offset=offset
                )
                points, next_page = scroll_res
                for p in points:
                    payload = p.payload or {}
                    alias = payload.get("alias", "")
                    entity_id = payload.get("entity_id", "")
                    if alias and entity_id:
                        self.aliases_cache[alias.lower()] = entity_id
                        
                if not next_page:
                    break
                offset = next_page
                
            logger.info("aliases_cache_loaded", total_aliases=len(self.aliases_cache))
        except Exception as e:
            logger.error("failed_loading_aliases_cache", error=str(e))
            
    def get_entity_by_alias(self, name: str) -> Optional[str]:
        """
        Resolve a query name to its entity_id.
        If cache is empty, we load it first.
        """
        if not self.aliases_cache:
            self.load_aliases_cache()
        
        # Check direct lowercase generic/alias matches
        name_lower = name.lower().strip()
        if name_lower in self.aliases_cache:
            return self.aliases_cache[name_lower]
            
        # Try direct mapping checks (e.g. "metformin" -> "drug:metformin")
        # Check registry direct lookup
        registry_uid = self.get_deterministic_uuid(f"drug:{name_lower}")
        try:
            res = self.client.retrieve(collection_name=self.registry_col, ids=[registry_uid])
            if res:
                return f"drug:{name_lower}"
        except Exception:
            pass
            
        return None
        
    def get_profile(self, entity_id: str, profile_type: str, authority: str = "FDA") -> Optional[Dict[str, Any]]:
        """
        Fetch a structured profile from Qdrant.
        """
        key_str = f"{entity_id}_{profile_type}_{authority}".lower()
        uid = self.get_deterministic_uuid(key_str)
        try:
            res = self.client.retrieve(collection_name=self.profiles_col, ids=[uid])
            if res:
                return res[0].payload
        except Exception as e:
            logger.error("failed_fetching_profile", entity_id=entity_id, profile_type=profile_type, error=str(e))
        return None
        
    def get_registry_entry(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a registry entry from Qdrant.
        """
        uid = self.get_deterministic_uuid(entity_id)
        try:
            res = self.client.retrieve(collection_name=self.registry_col, ids=[uid])
            if res:
                return res[0].payload
        except Exception as e:
            logger.error("failed_fetching_registry_entry", entity_id=entity_id, error=str(e))
        return None

    def get_profile_checksum(self, entity_id: str, profile_type: str, authority: str = "FDA") -> Optional[str]:
        """
        Fetch the stored checksum for incremental update checks.
        """
        profile = self.get_profile(entity_id, profile_type, authority)
        if profile:
            return profile.get("checksum")
        return None
