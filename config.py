import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

    LANGUAGES = [
        "English", "Hindi", "Telugu", "Tamil", "Kannada", "Malayalam",
        "Marathi", "Bengali", "Gujarati", "Punjabi", "Odia", "Urdu"
    ]

    CATEGORIES = [
        {"id": "general", "name": "General Chat"},
        {"id": "medicine", "name": "Medicine Info"},
        {"id": "hospitals", "name": "Find Hospitals"},
        {"id": "reports", "name": "Report Analysis"},
        {"id": "symptoms", "name": "Symptom Check"},
        {"id": "emergency", "name": "Emergency"},
    ]