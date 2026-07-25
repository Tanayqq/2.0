"""
MedRef Clinical Intelligence Platform CI/CD Automated Quality Gate.
Runs Pytest Regression -> Benchmark Suite -> Coverage Analyzer.
Deploys ONLY if all quality gates pass!
"""
import sys
import os
import subprocess

def run_step(cmd, name):
    print(f"\n================================================================================")
    print(f"  [CI/CD QUALITY GATE STEP] : {name}")
    print(f"================================================================================")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[CI/CD FAILURE] Step '{name}' failed with exit code {result.returncode}!")
        sys.exit(result.returncode)
    print(f"[CI/CD PASS] Step '{name}' passed cleanly.")

def main():
    print("STARTING MEDREF CLINICAL QUALITY PIPELINE...")
    
    # 1. Pytest Unit & Integration Regression Suite
    run_step("pytest backend/tests -v", "Pytest 67/67 Regression Suite")
    
    # 2. Clinical Benchmark Evaluation Harness
    run_step("python phase3/evaluation/clinical_eval_suite.py --specialty all", "Phase 3 Clinical Benchmark Suite")
    
    # 3. Multi-Dimension Coverage Analyzer
    run_step("python phase3/corpus/coverage_analyzer.py", "Multi-Dimensional Coverage Analyzer")
    
    print("\n================================================================================")
    print("ALL CLINICAL QUALITY GATES PASSED CLEANLY -- PROCEEDING TO DEPLOYMENT!")
    print("================================================================================\n")

if __name__ == "__main__":
    main()
