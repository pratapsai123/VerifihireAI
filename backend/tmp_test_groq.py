import os
import groq
from django.conf import settings
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

def test_groq():
    api_key = getattr(settings, 'GROQ_API_KEY', None)
    if not api_key:
        print("GROQ_API_KEY not found in settings.")
        return

    print(f"Testing Groq API Key: {api_key[:10]}...")
    client = groq.Groq(api_key=api_key)
    
    models_to_test = [
        "llama-3.1-8b-instant",
        "llama3-8b-8192",
        "mixtral-8x7b-32768"
    ]
    
    for model in models_to_test:
        print(f"\n--- Testing Model: {model} ---")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Ping"}],
                max_tokens=5
            )
            print(f"Success with {model}! Response:", response.choices[0].message.content)
            break
        except groq.PermissionDeniedError as e:
            print(f"Permission Denied (403) for {model}: {e}")
        except Exception as e:
            print(f"An error occurred for {model}: {e}")

if __name__ == "__main__":
    test_groq()
