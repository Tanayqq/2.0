import os
import glob
import sys

# Ensure backend package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.pipeline.orchestrator import IngestionOrchestrator

def main():
    raw_dir = "backend/ingestion/data/raw"
    files = glob.glob(os.path.join(raw_dir, "openfda_*.json"))
    drugs = []
    for f in files:
        basename = os.path.basename(f)
        drug = basename.replace("openfda_", "").replace(".json", "")
        drugs.append(drug)
        
    drugs = sorted(list(set(drugs)))
    print(f"Found {len(drugs)} cached drugs to ingest.")
    
    orchestrator = IngestionOrchestrator()
    orchestrator.ingest_drugs(drugs)

if __name__ == "__main__":
    main()
