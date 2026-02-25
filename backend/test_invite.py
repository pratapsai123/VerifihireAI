import requests
import json
import base64

url = "http://localhost:8001/api/ai-candidates/bulk-invite/"

# Create a dummy CSV file in memory
csv_content = "name,email\nTest User,python.nexnoratech@gmail.com"

# Prepare the form data
files = {
    'file': ('test.csv', csv_content, 'text/csv')
}
data = {
    'job_description': 'Software Engineer Test',
    'available_from': '2026-02-23T10:00:00Z',
    'available_until': '2026-02-23T18:00:00Z'
}

print("Sending request...")
response = requests.post(url, data=data, files=files)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
