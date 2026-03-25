
import asyncio
import os
import sys
import google.genai

# Add backend to sys.path
backend_path = r'c:\Users\nithyaganesh.AcerAspireLite\Desktop\linkguard-ai\backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.chatbot_service import get_chatbot_service

async def test_chatbot():
    print(f"Python version: {sys.version}")
    print(f"google-genai version: {google.genai.__version__ if hasattr(google.genai, '__version__') else 'unknown'}")
    
    service = get_chatbot_service()
    print(f"AI Enabled: {service.ai_enabled}")
    
    query = "What is a typosquatting attack?"
    print(f"Query: {query}")
    
    response = service.get_response(query)
    
    print("-" * 30)
    print(f"Response: {response}")
    print("-" * 30)
    
    if "analyzing high-priority security logs" in response:
        print("FAILURE: Fallback message received.")
    else:
        print("SUCCESS: AI response received!")

if __name__ == "__main__":
    asyncio.run(test_chatbot())
