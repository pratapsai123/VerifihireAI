import requests
import time
import concurrent.futures

EXECUTOR_URL = "http://localhost:4000/execute"

def warmup(lang, code, name):
    print(f"[{name}] Warming up ({lang})... This triggers a one-time build.")
    start = time.time()
    try:
        resp = requests.post(EXECUTOR_URL, json={
            "language": lang,
            "source_code": code,
            "time_limit_ms": 30000, # Increased timeout for warmup
            "memory_mb": 512
        })
        duration = time.time() - start
        if resp.status_code == 200:
            print(f"✅ {name} Ready! (Took {duration:.2f}s)")
        else:
            print(f"❌ {name} Failed: {resp.text}")
    except Exception as e:
        print(f"❌ {name} Error: {e}")

tasks = [
    ("typescript", "console.log('ready');", "TypeScript"),
    ("kotlin", "fun main() { println(\"ready\") }", "Kotlin"),
    ("sql", "SELECT 1;", "SQLite"),
    ("scala", "@main def run() = println(\"ready\")", "Scala 3")
]

print(f"Starting parallel warmup for {len(tasks)} languages...")
start_all = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(warmup, lang, code, name) for lang, code, name in tasks]
    concurrent.futures.wait(futures)

print(f"All warmups completed in {time.time() - start_all:.2f}s")
