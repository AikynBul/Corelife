import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"Using API Key: {api_key[:5]}...{api_key[-5:]}")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

try:
    print("Sending test message...")
    response = model.generate_content("Hello, are you working?")
    print("Response received:")
    print(response.text)
    print("SUCCESS: AI is working!")
except Exception as e:
    print(f"ERROR: {e}")
