# src/database/mongo_operations.py (updated)
from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta
import logging
from config import MONGO_URI, DATABASE_NAME, FOOD_COLLECTION, USERS_COLLECTION, DEFAULT_CALORIE_GOAL

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        self.food_collection = self.db[FOOD_COLLECTION]
        self.users_collection = self.db[USERS_COLLECTION]
        self._create_indexes()
        
    def _create_indexes(self):
        self.food_collection.create_index([("user_id", ASCENDING), ("timestamp", ASCENDING)])
        self.users_collection.create_index([("user_id", ASCENDING), ("date", ASCENDING)])

    def insert_food_entry(self, user_id: str, entry: dict) -> bool:
        try:
            entry.update({
                "user_id": user_id,
                "timestamp": datetime.now()
            })
            result = self.food_collection.insert_one(entry)
            self._update_daily_summary(user_id)
            return True
        except Exception as e:
            logger.error(f"MongoDB insert error: {e}")
            return False

    def _update_daily_summary(self, user_id: str):
        try:
            entries = self.get_daily_entries(user_id)
            total_calories = sum(e["nutrition"]["calories"] for e in entries)
            
            summary = {
                "date": datetime.now().date().isoformat(),
                "total_calories": total_calories,
                "remaining_calories": DEFAULT_CALORIE_GOAL - total_calories,
                "protein": sum(e["nutrition"]["protein"] for e in entries),
                "carbs": sum(e["nutrition"]["carbs"] for e in entries),
                "fat": sum(e["nutrition"]["fat"] for e in entries)
            }
            
            self.users_collection.update_one(
                {"user_id": user_id, "date": datetime.now().date().isoformat()},
                {"$set": summary},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Daily summary update error: {e}")

    def get_daily_entries(self, user_id: str, target_date: datetime = None) -> list:
        try:
            query_date = target_date or datetime.now()
            start = datetime(query_date.year, query_date.month, query_date.day)
            end = start.replace(hour=23, minute=59, second=59)
            
            return list(self.food_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": start, "$lte": end}
            }).sort("timestamp", ASCENDING))
        except Exception as e:
            logger.error(f"MongoDB query error: {e}")
            return []

    def get_monthly_summary(self, user_id: str, year: int, month: int):
        try:
            start = datetime(year, month, 1)
            end = start + timedelta(days=31)
            end = end.replace(day=1) - timedelta(days=1)
            
            pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": start, "$lte": end}
                }},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "total_calories": {"$sum": "$nutrition.calories"},
                    "total_protein": {"$sum": "$nutrition.protein"},
                    "total_carbs": {"$sum": "$nutrition.carbs"},
                    "total_fat": {"$sum": "$nutrition.fat"}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            return list(self.food_collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Monthly summary error: {e}")
            return []
