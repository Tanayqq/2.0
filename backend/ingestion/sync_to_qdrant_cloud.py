import os, sys, glob
from qdrant_client import QdrantClient

# Ensure root backend dir is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import ingestion_config
from pipeline.adapters.dailymed_adapter import DailyMedAdapter
from pipeline.parser import MedicalParser
from pipeline.chunker import MedicalSectionChunker
from pipeline.embedder import MedicalEmbedder
from pipeline.uploader import MedicalUploader

def main():
    print("==================================================")
    print("  QDRANT CLOUD DIRECT SYNC (CORPUS v4.0 - 500 DRUGS)")
    print(f"  Target Cluster: {ingestion_config.QDRANT_URL}")
    print("==================================================")

    uploader = MedicalUploader()
    uploader.create_collection_if_not_exists(dimension=ingestion_config.EMBEDDING_DIMENSION)
    
    parser = MedicalParser()
    chunker = MedicalSectionChunker()
    embedder = MedicalEmbedder()
    
    # Load all drug names from drugs_500.txt
    drugs_file = os.path.join(ingestion_config.BASE_DIR, "drugs_500.txt")
    with open(drugs_file, "r", encoding="utf-8") as f:
        drugs = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
    print(f"Found {len(drugs)} drugs in Corpus v4.0 list.")
    
    all_chunks = []
    total_uploaded = 0

    for idx, drug in enumerate(drugs, 1):
        xml_path = os.path.join(ingestion_config.RAW_DATA_DIR, f"dailymed_{drug.lower().replace(' ', '_')}.xml")
        if not os.path.exists(xml_path):
            continue

        try:
            with open(xml_path, "r", encoding="utf-8") as f:
                xml_content = f.read()

            raw_doc = DailyMedAdapter.to_normalized(xml_content, drug)
            if not raw_doc or not raw_doc.sections:
                continue

            clean_doc = parser.parse(raw_doc)
            if not clean_doc.sections:
                continue

            chunks = chunker.chunk_document(clean_doc)
            if chunks:
                embedded = embedder.embed_chunks(chunks)
                all_chunks.extend(embedded)

            if len(all_chunks) >= 500 or idx == len(drugs):
                s, f_cnt = uploader.upload_chunks(all_chunks, batch_size=50)
                total_uploaded += s
                print(f"[{idx}/{len(drugs)}] Uploaded {len(all_chunks)} chunks to Qdrant Cloud. Total points: {total_uploaded}")
                all_chunks.clear()

        except Exception as e:
            print(f"[{idx}/{len(drugs)}] Error processing {drug}: {e}")

    if all_chunks:
        s, f_cnt = uploader.upload_chunks(all_chunks, batch_size=50)
        total_uploaded += s
        print(f"Final Batch: Uploaded {len(all_chunks)} chunks to Qdrant Cloud. Total points: {total_uploaded}")

    print("==================================================")
    print(f"  QDRANT CLOUD SYNC COMPLETED: {total_uploaded} VECTORS UPLOADED!")
    print("==================================================")

if __name__ == "__main__":
    main()
