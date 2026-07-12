from typing import Dict, Optional
from pydantic import BaseModel

class CitationSource(BaseModel):
    uuid: str
    citation_number: str
    source: str
    drug: str
    section: str
    similarity: Optional[float] = None
    text: str

class CitationMap:
    def __init__(self):
        self.entries: Dict[str, CitationSource] = {}

    def add_entry(self, uuid: str, citation_number: str, source: str, drug: str, section: str, text: str, similarity: Optional[float] = None) -> CitationSource:
        entry = CitationSource(
            uuid=uuid,
            citation_number=citation_number,
            source=source,
            drug=drug,
            section=section,
            similarity=similarity,
            text=text
        )
        self.entries[citation_number] = entry
        return entry

    def get_entry(self, citation_number: str) -> Optional[CitationSource]:
        return self.entries.get(citation_number)

    def to_dict(self) -> Dict[str, dict]:
        return {k: v.model_dump() for k, v in self.entries.items()}
