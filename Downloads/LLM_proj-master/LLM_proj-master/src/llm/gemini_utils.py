import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def load_gemini_model():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel("gemini-1.5-pro-latest")
