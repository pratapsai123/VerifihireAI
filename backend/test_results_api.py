import requests
import json

def test_results_api():
    url = "http://localhost:8001/api/results/"
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"Total results: {data.get('count')}")
            for r in results:
                if str(r.get('submission_id')).startswith('ai_'):
                    print(f"Found AI Result: {r['candidate']['name']} - {r['assessment']['display_name']} - Score: {r['score']}/{r['total']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_results_api()
