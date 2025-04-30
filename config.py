# config.py
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # MongoDB Configuration
# MONGO_URI = os.getenv("MONGO_URI", "")
# DATABASE_NAME = "nutrition_tracker"
# FOOD_COLLECTION = "food_entries"
# USERS_COLLECTION = "user_metrics"

# # OpenAI Configuration
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")  # Default to GPT-4 if not specified

# # Streamlit Configuration
# DEFAULT_CALORIE_GOAL = 2000


import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# Securely encode credentials
MONGO_USERNAME = quote_plus(os.getenv("MONGO_USERNAME", ""))
MONGO_PASSWORD = quote_plus(os.getenv("MONGO_PASSWORD", ""))

# Construct encoded URI
MONGO_URI = (
    f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}"
    "@uday1.n8mb8lm.mongodb.net/?retryWrites=true&w=majority&appName=Uday1"
)

# Database and collection names
DATABASE_NAME = "nutrition_tracker"
FOOD_COLLECTION = "food_entries"
USERS_COLLECTION = "user_metrics"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")

# Streamlit Configuration
DEFAULT_CALORIE_GOAL = 2000
