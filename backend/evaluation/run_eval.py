import os
import sys
import json
import statistics
import structlog

# Allow running directly from command line
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from ingestion.pipeline.embedder import MedicalEmbedder
from app.infrastructure.vector_db import QdrantAdapter

import math

logger = structlog.get_logger()

def calculate_dcg(relevances, p):
    dcg = 0.0
    for idx, rel in enumerate(relevances[:p]):
        dcg += rel / math.log2(idx + 2)
    return dcg

def calculate_ndcg(relevances, p):
    dcg = calculate_dcg(relevances, p)
    idcg = calculate_dcg(sorted(relevances, reverse=True), p)
    if idcg == 0.0:
        return 0.0
    return dcg / idcg

def run_evaluation():
    print("==================================================")
    print("Starting Retrieval Quality Evaluation (Recall/MRR)")
    print("==================================================")
    
    # Load dataset
    dataset_path = "evaluation/eval_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"Error: dataset file not found at {dataset_path}")
        sys.exit(1)
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)
        
    embedder = MedicalEmbedder()
    db_adapter = QdrantAdapter(
        mode=settings.VECTOR_DB_MODE,
        path=settings.QDRANT_PATH,
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY
    )
    
    total_cases = len(test_cases)
    recall_at_5_hits = 0
    recall_at_10_hits = 0
    reciprocal_ranks = []
    section_accuracies = []
    
    detailed_results = []
    
    for case_idx, case in enumerate(test_cases):
        query = case["query"]
        expected_drug = case["expected_drug"].lower()
        expected_section = case["expected_section"].lower()
        
        # 1. Embed query
        try:
            q_vec = embedder.provider.embed_texts([query])[0]
        except Exception as e:
            print(f"Failed to embed query '{query}': {e}")
            continue
            
        # 2. Search Qdrant
        try:
            hits = db_adapter.search(query_vector=q_vec, top_k=10)
        except Exception as e:
            print(f"Failed Qdrant search for query '{query}': {e}")
            continue
            
        # 3. Analyze ranking
        found_rank = None
        drug_found_rank = None
        
        for rank_idx, hit in enumerate(hits):
            drug_name = hit.metadata.get("drug_name", "").lower()
            section = hit.metadata.get("section", "").lower()
            canonical_section = hit.metadata.get("canonical_section", "").lower()
            
            # Drug-Only Match
            if drug_name == expected_drug and drug_found_rank is None:
                drug_found_rank = rank_idx + 1
            
            # Full Match (Drug & Section)
            if drug_name == expected_drug and (section == expected_section or canonical_section == expected_section) and found_rank is None:
                found_rank = rank_idx + 1
                
        # Calculate metrics for this case
        r_at_5 = 1 if (found_rank is not None and found_rank <= 5) else 0
        r_at_10 = 1 if (found_rank is not None and found_rank <= 10) else 0
        rr = 1.0 / found_rank if found_rank is not None else 0.0
        
        drug_r_at_5 = 1 if (drug_found_rank is not None and drug_found_rank <= 5) else 0
        drug_r_at_10 = 1 if (drug_found_rank is not None and drug_found_rank <= 10) else 0
        drug_rr = 1.0 / drug_found_rank if drug_found_rank is not None else 0.0
        
        recall_at_5_hits += r_at_5
        recall_at_10_hits += r_at_10
        reciprocal_ranks.append(rr)
        
        # Drug-only accumulators
        if 'drug_recall_at_5_hits' not in locals():
            drug_recall_at_5_hits = 0
            drug_recall_at_10_hits = 0
            drug_reciprocal_ranks = []
            ndcg_5_scores = []
            ndcg_10_scores = []
            
        drug_recall_at_5_hits += drug_r_at_5
        drug_recall_at_10_hits += drug_r_at_10
        drug_reciprocal_ranks.append(drug_rr)
        
        # Calculate NDCG Relevances (2=full, 1=drug only, 0=none)
        relevances = []
        for hit in hits:
            drug_name = hit.metadata.get("drug_name", "").lower()
            section = hit.metadata.get("section", "").lower()
            canonical_section = hit.metadata.get("canonical_section", "").lower()
            
            if drug_name == expected_drug:
                if section == expected_section or canonical_section == expected_section:
                    relevances.append(2)
                else:
                    relevances.append(1)
            else:
                relevances.append(0)
        while len(relevances) < 10:
            relevances.append(0)
            
        n5 = calculate_ndcg(relevances, 5)
        n10 = calculate_ndcg(relevances, 10)
        ndcg_5_scores.append(n5)
        ndcg_10_scores.append(n10)
        
        # Section accuracy for top retrieved chunk
        top_section_match = 0
        top_drug = "None"
        top_section = "None"
        if hits:
            top_drug = hits[0].metadata.get("drug_name", "None")
            top_section = hits[0].metadata.get("section", "None")
            if top_drug.lower() == expected_drug and top_section.lower() == expected_section:
                top_section_match = 1
        section_accuracies.append(top_section_match)
        
        detailed_results.append({
            "query": query,
            "expected_drug": expected_drug.capitalize(),
            "expected_section": expected_section,
            "top_drug_retrieved": top_drug,
            "top_section_retrieved": top_section,
            "found_at_rank": found_rank if found_rank else "Not in top 10",
            "drug_found_at_rank": drug_found_rank if drug_found_rank else "Not in top 10",
            "recall_at_5": r_at_5,
            "recall_at_10": r_at_10,
            "reciprocal_rank": rr,
            "drug_recall_at_5": drug_r_at_5,
            "drug_reciprocal_rank": drug_rr,
            "ndcg_5": n5,
            "ndcg_10": n10
        })
        
        print(f"[{case_idx+1}/{total_cases}] Query: '{query}' -> Full Rank: {found_rank if found_rank else 'N/A'} | Drug Rank: {drug_found_rank if drug_found_rank else 'N/A'} | NDCG@5: {n5:.4f}")

    # Aggregate metrics
    mean_recall_at_5 = recall_at_5_hits / total_cases if total_cases > 0 else 0.0
    mean_recall_at_10 = recall_at_10_hits / total_cases if total_cases > 0 else 0.0
    mrr = statistics.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
    
    mean_drug_recall_at_5 = drug_recall_at_5_hits / total_cases if total_cases > 0 else 0.0
    mean_drug_recall_at_10 = drug_recall_at_10_hits / total_cases if total_cases > 0 else 0.0
    drug_mrr = statistics.mean(drug_reciprocal_ranks) if drug_reciprocal_ranks else 0.0
    
    mean_ndcg_5 = statistics.mean(ndcg_5_scores) if ndcg_5_scores else 0.0
    mean_ndcg_10 = statistics.mean(ndcg_10_scores) if ndcg_10_scores else 0.0
    
    section_accuracy = statistics.mean(section_accuracies) if section_accuracies else 0.0
    
    print("\n==================================================")
    print("EVALUATION METRICS SUMMARY")
    print("==================================================")
    print(f"Total Test Cases:    {total_cases}")
    print(f"--- Full-Match Metrics (Drug & Section) ---")
    print(f"Mean Recall@5:       {mean_recall_at_5:.2%}")
    print(f"Mean Recall@10:      {mean_recall_at_10:.2%}")
    print(f"MRR:                 {mrr:.4f}")
    print(f"Top-1 Match Acc:     {section_accuracy:.2%}")
    print(f"--- NDCG Metrics ---")
    print(f"Mean NDCG@5:         {mean_ndcg_5:.4f}")
    print(f"Mean NDCG@10:        {mean_ndcg_10:.4f}")
    print(f"--- Drug-Only Metrics ---")
    print(f"Mean Recall@5:       {mean_drug_recall_at_5:.2%}")
    print(f"Mean Recall@10:      {mean_drug_recall_at_10:.2%}")
    print(f"MRR:                 {drug_mrr:.4f}")
    print("==================================================")
    
    # Save Report to docs/RETRIEVAL_EVAL_REPORT.md
    report_file = "docs/RETRIEVAL_EVAL_REPORT.md"
    os.makedirs("docs", exist_ok=True)
    
    markdown_lines = [
        "# Retrieval Quality Evaluation Report",
        "",
        "## Summary Metrics",
        f"- **Total Test Cases**: {total_cases}",
        "",
        "### Full-Match Metrics (Drug & Section)",
        f"- **Mean Recall@5**: {mean_recall_at_5:.2%}",
        f"- **Mean Recall@10**: {mean_recall_at_10:.2%}",
        f"- **MRR (Mean Reciprocal Rank)**: {mrr:.4f}",
        f"- **Top-1 Match Accuracy**: {section_accuracy:.2%}",
        "",
        "### NDCG Metrics",
        f"- **Mean NDCG@5**: {mean_ndcg_5:.4f}",
        f"- **Mean NDCG@10**: {mean_ndcg_10:.4f}",
        "",
        "### Drug-Only Metrics",
        f"- **Mean Recall@5**: {mean_drug_recall_at_5:.2%}",
        f"- **Mean Recall@10**: {mean_drug_recall_at_10:.2%}",
        f"- **MRR**: {drug_mrr:.4f}",
        "",
        "## Detailed Query Analysis",
        "| Query | Expected Drug | Expected Section | Full Match Rank | Drug Match Rank | Top Retrieved Drug / Section | NDCG@5 | MRR |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |"
    ]
    
    for r in detailed_results:
        full_rank_str = f"Rank {r['found_at_rank']}" if isinstance(r['found_at_rank'], int) else r['found_at_rank']
        drug_rank_str = f"Rank {r['drug_found_at_rank']}" if isinstance(r['drug_found_at_rank'], int) else r['drug_found_at_rank']
        top_retrieved = f"{r['top_drug_retrieved']} / {r['top_section_retrieved']}"
        markdown_lines.append(
            f"| `{r['query']}` | {r['expected_drug']} | `{r['expected_section']}` | {full_rank_str} | {drug_rank_str} | {top_retrieved} | {r['ndcg_5']:.4f} | {r['reciprocal_rank']:.4f} |"
        )
        
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))
        
    print(f"Evaluation report successfully written to {report_file}")

if __name__ == '__main__':
    run_evaluation()
