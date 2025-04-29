# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "nutrition_tracker"
FOOD_COLLECTION = "food_entries"
USERS_COLLECTION = "user_metrics"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")  # Default to GPT-4 if not specified

# Streamlit Configuration
DEFAULT_CALORIE_GOAL = 2000
