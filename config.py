import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GPT_MODEL = "gpt-4" # You can change this to a different model if needed

# Database Configuration
DATABASE_PATH = 'data/nutrition_tracker.db'

# Application Configuration
DATE_FORMAT = "%Y-%m-%d"
CACHE_EXPIRY_DAYS = 30  # How long to cache nutrition data