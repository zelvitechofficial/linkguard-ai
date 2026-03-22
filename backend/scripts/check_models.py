import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def check_models():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Missing GEMINI_API_KEY")
        return

    client = genai.Client(api_key=api_key)
    try:
        models = [m.name for m in client.models.list()]
        print(f"Total models found: {len(models)}")
        for m in models:
            try:
                print(f"Testing {m}...", end=" ", flush=True)
                response = client.models.generate_content(model=m, contents="hi")
                print("SUCCESS")
                print(f"Model {m} is working!")
                return m
            except Exception as e:
                print(f"FAILED: {e}")
    except Exception as e:
        print(f"Failed to list models: {e}")

if __name__ == "__main__":
    check_models()
