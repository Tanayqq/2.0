import os

log_file = r"C:\Users\Tanay Kumar\.gemini\antigravity\brain\12945e83-f715-4873-a0a4-73bb399bb4cb\.system_generated\logs\transcript.jsonl"
if os.path.exists(log_file):
    print("Found log file, searching...")
    with open(log_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if "deploy" in line.lower() or "render" in line.lower() or "hook" in line.lower():
                # Print matching snippets
                idx = line.lower().find("deploy")
                if idx == -1:
                    idx = line.lower().find("render")
                start = max(0, idx - 50)
                end = min(len(line), idx + 150)
                snippet = line[start:end].encode('ascii', errors='ignore').decode('ascii')
                print(f"Line {i}: ... {snippet} ...")
else:
    print("Log file not found.")
