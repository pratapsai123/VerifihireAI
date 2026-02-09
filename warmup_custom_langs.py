import requests
import time

EXECUTOR_URL = "http://localhost:4000/execute"

def warmup(lang, code, name):
    print(f"Warming up {name} ({lang})... This triggers a one-time build.")
    start = time.time()
    try:
        resp = requests.post(EXECUTOR_URL, json={
            "language": lang,
            "source_code": code,
            "time_limit_ms": 5000,
            "memory_mb": 512
        })
        duration = time.time() - start
        if resp.status_code == 200:
            print(f"✅ {name} Ready! (Took {duration:.2f}s)")
        else:
            print(f"❌ {name} Failed: {resp.text}")
    except Exception as e:
        print(f"❌ {name} Error: {e}")

# TypeScript
warmup("typescript", "console.log('ready');", "TypeScript")

# Kotlin (Downloads compiler, might take time)
warmup("kotlin", "fun main() { println(\"ready\") }", "Kotlin")

# SQLite (Builds from Alpine)
warmup("sql", "SELECT 1;", "SQLite")

# Scala 3
warmup("scala", "@main def run() = println(\"ready\")", "Scala 3")
