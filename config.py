import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PREDICTHQ_API_KEY = os.getenv("PREDICTHQ_API_KEY")
ACCESS_API_KEYS = os.getenv("ACCESS_API_KEYS", "").split(",")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
PREDICTHQ_SEARCH_URL = os.getenv("PREDICTHQ_SEARCH_URL")
