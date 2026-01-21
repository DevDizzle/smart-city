
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

try:
    print("Listing models...")
    for m in client.models.list(config={"page_size": 10}):
        print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
