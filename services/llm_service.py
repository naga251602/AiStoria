# services/llm_service.py
import google.generativeai as genai
from config import Config

model = None

def configure_llm():
    global model
    try:
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini AI Configured Successfully")
        else:
            print("⚠️ GEMINI_API_KEY not found in environment")
    except Exception as e:
        print(f"❌ Error configuring Gemini API: {e}")

def get_model():
    return model