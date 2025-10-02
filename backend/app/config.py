# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NOTION_TOKEN = os.getenv("NOTION_TOKEN", "tn_491037271386wwbiRGg1arHRd04qyDJEk7Rbis6wyLQbO8")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCW5sncbljQ4D23e3geBpCwi8p1IbVnxMc")
    DEFAULT_PAGE_ID = os.getenv("NOTION_PAGE_ID", "046b959f77304a22aa4ac46aed6a06e4")
    MAX_REQUESTS_PER_HOUR = int(os.getenv("MAX_REQUESTS_PER_HOUR", "50"))
    MAX_SUSPICIOUS_ATTEMPTS = int(os.getenv("MAX_SUSPICIOUS_ATTEMPTS", "3"))
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")







