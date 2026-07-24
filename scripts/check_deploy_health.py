"""
MedRef Deployment Health Checker
---------------------------------
Automated single-command diagnostic script that verifies:
1. Local git vs GitHub remotes (Tanayqq/2.0 and Tanayqq/medref)
2. Branch consistency (master vs main)
3. Render Backend Live Health Endpoint (medref-38hx.onrender.com)
4. Vercel Frontend Live Health Status (medref-pearl.vercel.app)
5. Pipeline synchronization & SHA alignment
"""

import subprocess
import urllib.request
import time
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# ANSI Color formatting
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def run_cmd(cmd: str) -> str:
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        return ""

def print_header(title: str):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN} 🔍 {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def check_git_status():
    print_header("1. GIT & REMOTE SYNCHRONIZATION")
    
    local_sha = run_cmd("git rev-parse --short HEAD")
    branch = run_cmd("git branch --show-current")
    print(f"• Local Branch: {BOLD}{branch}{RESET} (SHA: {BOLD}{local_sha}{RESET})")
    
    remotes = run_cmd("git remote -v")
    print(f"• Configured Remotes:\n{remotes}\n")
    
    print("• Fetching latest remote branches...")
    run_cmd("git fetch --all")
    
    origin_master = run_cmd("git rev-parse --short origin/master 2>nul || git rev-parse --short origin/master")
    origin_main = run_cmd("git rev-parse --short origin/main 2>nul || git rev-parse --short origin/main")
    render_master = run_cmd("git rev-parse --short render-repo/master 2>nul || git rev-parse --short render-repo/master")
    render_main = run_cmd("git rev-parse --short render-repo/main 2>nul || git rev-parse --short render-repo/main")
    
    print(f"  - origin/master:      {BOLD}{origin_master}{RESET}")
    print(f"  - origin/main:        {BOLD}{origin_main}{RESET}")
    print(f"  - render-repo/master: {BOLD}{render_master}{RESET}")
    print(f"  - render-repo/main:   {BOLD}{render_main}{RESET}")
    
    # Check alignment
    if origin_master == origin_main:
        print(f"{GREEN}✓ origin/master and origin/main are synchronized.{RESET}")
    else:
        print(f"{YELLOW}⚠️ origin/master ({origin_master}) and origin/main ({origin_main}) have diverged!{RESET}")
        
    if render_master == origin_master:
        print(f"{GREEN}✓ render-repo (Tanayqq/medref) is in sync with origin (Tanayqq/2.0).{RESET}")
    else:
        print(f"{YELLOW}⚠️ render-repo ({render_master}) differs from origin ({origin_master}). Run sync command to align.{RESET}")

def check_backend_health():
    print_header("2. RENDER BACKEND HEALTH (medref-38hx.onrender.com)")
    url = "https://medref-38hx.onrender.com/api/v1/health"
    print(f"• Pinging endpoint: {url}")
    
    start_time = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MedRefHealthChecker/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            latency = round((time.time() - start_time) * 1000, 2)
            body = resp.read().decode("utf-8")
            if resp.status == 200:
                print(f"{GREEN}✓ Backend LIVE (HTTP 200 OK) in {latency} ms{RESET}")
                print(f"  Response: {body}")
            else:
                print(f"{RED}❌ Backend returned HTTP {resp.status}{RESET}")
    except Exception as e:
        latency = round((time.time() - start_time) * 1000, 2)
        print(f"{RED}❌ Backend Ping Failed after {latency} ms: {e}{RESET}")
        print(f"{YELLOW}  (Note: Render free instances spin down on inactivity and may take ~30s on cold start){RESET}")

def check_frontend_health():
    print_header("3. VERCEL FRONTEND HEALTH (medref-pearl.vercel.app)")
    url = "https://medref-pearl.vercel.app"
    print(f"• Pinging Production UI: {url}")
    
    start_time = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MedRefHealthChecker/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            latency = round((time.time() - start_time) * 1000, 2)
            if resp.status == 200:
                print(f"{GREEN}✓ Vercel Frontend LIVE (HTTP 200 OK) in {latency} ms{RESET}")
            else:
                print(f"{RED}❌ Vercel Frontend returned HTTP {resp.status}{RESET}")
    except Exception as e:
        latency = round((time.time() - start_time) * 1000, 2)
        print(f"{RED}❌ Vercel Frontend Ping Failed: {e}{RESET}")

def main():
    print(f"{BOLD}{GREEN}============================================================{RESET}")
    print(f"{BOLD}{GREEN} 🩺 MEDREF DEPLOYMENT HEALTH CHECKER v1.0 {RESET}")
    print(f"{BOLD}{GREEN}============================================================{RESET}")
    
    check_git_status()
    check_backend_health()
    check_frontend_health()
    
    print_header("SUMMARY & RECOMMENDED ACTIONS")
    print(f"• To sync all remotes (GitHub 2.0 + GitHub MedRef + GitLab) run:")
    print(f"  {BOLD}git push origin master:master master:main && git push -f render-repo master:master master:main{RESET}\n")

if __name__ == "__main__":
    main()
