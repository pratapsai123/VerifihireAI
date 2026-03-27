import os
import time
from groq import Groq

# Use the key from settings or env
api_key = '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' # Key from user's last edit

client = Groq(api_key=api_key)

print("--- Testing Groq AI Speed ---")
start = time.time()
try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say 'Test OK' in JSON format."}],
        response_format={"type": "json_object"}
    )
    duration = time.time() - start
    print(f"Success! Time taken: {duration:.2f} seconds")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"FAILED: {str(e)}")
