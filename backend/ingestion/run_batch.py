import os
import sys
import argparse
import structlog

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.pipeline.orchestrator import IngestionOrchestrator

logger = structlog.get_logger()

BATCH_TARGETS = {
    1: 200,
    2: 350,
    3: 500
}

def run_batch(batch_num: int, force: bool = False, incremental: bool = False):
    if batch_num not in BATCH_TARGETS:
        print(f"Error: Invalid batch number {batch_num}. Choose 1, 2, or 3.")
        sys.exit(1)

    target_count = BATCH_TARGETS[batch_num]
    drugs_file = os.path.join(os.path.dirname(__file__), "drugs_500.txt")

    if not os.path.exists(drugs_file):
        print(f"Error: {drugs_file} not found. Running curate_500_drugs.py first...")
        from ingestion.curate_500_drugs import curate_500_drugs
        curate_500_drugs()

    with open(drugs_file, "r", encoding="utf-8") as f:
        all_500 = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    batch_drugs = all_500[:target_count]
    print(f"\n==================================================")
    print(f"  STARTING INGESTION BATCH {batch_num} ({len(batch_drugs)} DRUGS)")
    print(f"==================================================\n")

    orchestrator = IngestionOrchestrator(force_reingest=force, incremental=incremental)
    orchestrator.ingest_drugs(batch_drugs)

    print(f"\n==================================================")
    print(f"  BATCH {batch_num} ({len(batch_drugs)} DRUGS) INGESTION COMPLETED")
    print(f"==================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corpus v4.0 Batch Ingestion Runner")
    parser.add_argument("--batch", type=int, required=True, choices=[1, 2, 3], help="Batch number to run (1: 200 drugs, 2: 350 drugs, 3: 500 drugs)")
    parser.add_argument("--force", action="store_true", help="Force re-ingestion by bypassing checksums")
    parser.add_argument("--incremental", action="store_true", help="Enable chunk-level diffing")
    args = parser.parse_args()

    run_batch(args.batch, force=args.force, incremental=args.incremental)
