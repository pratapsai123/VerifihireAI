import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

print(f"✅ Found API Key: {api_key[:5]}...{api_key[-5:]}")

# Configure Gemini
genai.configure(api_key=api_key)

try:
    print("MATCHING_TEST: Listing available models...")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")
    
    print("\nMATCHING_TEST: Attempting to use 'gemini-2.5-flash-lite'...")
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    response = model.generate_content("Are you working? Reply with 'Yes, I am functional'.")
    print(f"✅ API Response: {response.text}")
    print("🎉 Verification Successful! The Resume Matcher backend is ready.")
except Exception as e:
    print(f"❌ API Error: {str(e)}")
