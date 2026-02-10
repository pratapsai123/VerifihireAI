import requests
import time
import sys
import json
import uuid

def check_server(url, name):
    try:
        response = requests.get(url)
        print(f"[{name}] Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[{name}] Failed to connect")
        return False

def verify_interview_flow():
    base_url = "http://127.0.0.1:8000"
    
    # Check Backend
    if not check_server(f"{base_url}/admin/login/", "Backend"):
        return

    # Create dummy interview
    # We might need auth. For now, let's check if the URL exists (401/403 is fine, 404 is bad)
    print("Checking Interview URLs...")
    endpoints = [
        f"{base_url}/api/interviews/invite/",
        f"{base_url}/api/interviews/invitations/",
    ]
    
    for ep in endpoints:
        try:
            r = requests.get(ep)
            if r.status_code != 404:
                print(f"Endpoint {ep} exists (Status: {r.status_code})")
            else:
                print(f"Endpoint {ep} NOT FOUND (Status: 404)")
        except Exception as e:
            print(f"Error checking {ep}: {e}")

    # WebSocket check removed due to missing dependency
    print("Skipping WebSocket check")

if __name__ == "__main__":
    verify_interview_flow()
