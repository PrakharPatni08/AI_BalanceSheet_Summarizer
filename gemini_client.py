"""
Google Gemini API client for AI Balance Sheet Summarizer
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

class GeminiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.api_url = GEMINI_API_URL

    def generate_summary(self, prompt: str) -> str:
        if not self.api_key:
            return "Gemini API key not set. Please add GEMINI_API_KEY to your .env file."
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            response = requests.post(self.api_url, headers=headers, params=params, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Gemini API error: {str(e)}"
