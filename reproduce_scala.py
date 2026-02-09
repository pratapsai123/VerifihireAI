import requests
import time

EXECUTOR_URL = "http://localhost:4000/execute"

def test_scala(code, name):
    print(f"Testing {name}...")
    start = time.time()
    try:
        resp = requests.post(EXECUTOR_URL, json={
            "language": "scala",
            "source_code": code,
            "time_limit_ms": 5000,
            "memory_mb": 512
        })
        duration = time.time() - start
        if resp.status_code == 200:
            result = resp.json()
            if result.get("ok"):
                print(f"✅ {name} Passed! Output:\n{result.get('stdout')}")
            else:
                print(f"❌ {name} Failed (Executor Error):\n{result.get('error')}\nStderr: {result.get('stderr')}")
        else:
            print(f"❌ {name} Failed: {resp.status_code}\n{resp.text}")
    except Exception as e:
        print(f"❌ {name} Exception: {e}")

# Scala 3 style @main
scala3_code = """
@main def hello() = println("Hello from Scala 3!")
"""

# Scala 2 style object extending App
scala2_code = """
object Main extends App {
    println("Hello from Scala 2 object!")
}
"""

test_scala(scala3_code, "Scala 3 (@main)")
test_scala(scala2_code, "Scala 2 (object Main)")
