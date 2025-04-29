import sqlite3
import json
import datetime
import logging
import os
from config import DATABASE_PATH
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def get_connection():
    """Get a connection to the SQLite database."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create the necessary tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create food_entries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_item TEXT NOT NULL,
        nutrition_data TEXT NOT NULL,
        date TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    
    # Create user_metrics table for tracking weight, calories goals, etc.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        weight REAL,
        calories_goal INTEGER,
        protein_goal INTEGER,
        carbs_goal INTEGER,
        fat_goal INTEGER,
        notes TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database tables created or verified.")

def add_food_entry(food_item: str, nutrition_data: Dict[str, Any]):
    """
    Add a new food entry to the database.
    
    Args:
        food_item (str): The name or description of the food
        nutrition_data (dict): Nutrition information for the food
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now()
        date = now.strftime('%Y-%m-%d')
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert nutrition data to JSON string
        nutrition_json = json.dumps(nutrition_data)
        
        cursor.execute(
            "INSERT INTO food_entries (food_item, nutrition_data, date, timestamp) VALUES (?, ?, ?, ?)",
            (food_item, nutrition_json, date, timestamp)
        )
        
        conn.commit()
        conn.close()
        logger.info(f"Added food entry: {food_item}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding food entry: {e}")
        return False

def get_daily_entries(date: datetime.date = None) -> List[Dict]:
    """
    Get all food entries for a specific date.
    
    Args:
        date (datetime.date, optional): The date to get entries for. Defaults to today.
        
    Returns:
        List[Dict]: List of food entries with their nutrition data
    """
    try:
        if date is None:
            date = datetime.date.today()
            
        date_str = date.strftime('%Y-%m-%d')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM food_entries WHERE date = ? ORDER BY timestamp",
            (date_str,)
        )
        
        entries = []
        for row in cursor.fetchall():
            entry = dict(row)
            # Parse JSON string back to dictionary
            entry['nutrition_data'] = json.loads(entry['nutrition_data'])
            # Convert timestamp string to datetime object
            entry['timestamp'] = datetime.datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
            entries.append(entry)
        
        conn.close()
        return entries
        
    except Exception as e:
        logger.error(f"Error retrieving daily entries: {e}")
        return []

def get_date_range_entries(start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
    """
    Get all food entries within a date range.
    
    Args:
        start_date (datetime.date): Start date of the range
        end_date (datetime.date): End date of the range
        
    Returns:
        List[Dict]: List of food entries within the range
    """
    try:
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM food_entries WHERE date >= ? AND date <= ? ORDER BY date, timestamp",
            (start_date_str, end_date_str)
        )
        
        entries = []
        for row in cursor.fetchall():
            entry = dict(row)
            # Parse JSON string back to dictionary
            entry['nutrition_data'] = json.loads(entry['nutrition_data'])
            # Convert timestamp string to datetime object
            entry['timestamp'] = datetime.datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
            entries.append(entry)
        
        conn.close()
        return entries
        
    except Exception as e:
        logger.error(f"Error retrieving entries for date range: {e}")
        return []

def update_user_metrics(date: datetime.date, metrics: Dict[str, Any]):
    """
    Update or insert user metrics for a specific date.
    
    Args:
        date (datetime.date): The date for the metrics
        metrics (dict): User metrics including weight, goals, etc.
    """
    try:
        date_str = date.strftime('%Y-%m-%d')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if metrics for this date already exist
        cursor.execute("SELECT id FROM user_metrics WHERE date = ?", (date_str,))
        result = cursor.fetchone()
        
        if result:
            # Update existing record
            query = "UPDATE user_metrics SET "
            params = []
            
            for key, value in metrics.items():
                if value is not None:
                    query += f"{key} = ?, "
                    params.append(value)
            
            # Remove trailing comma and space
            query = query[:-2]
            query += " WHERE date = ?"
            params.append(date_str)
            
            cursor.execute(query, params)
        else:
            # Insert new record
            keys = ["date"] + list(metrics.keys())
            placeholders = ", ".join(["?"] * len(keys))
            values = [date_str] + list(metrics.values())
            
            query = f"INSERT INTO user_metrics ({', '.join(keys)}) VALUES ({placeholders})"
            cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error updating user metrics: {e}")
        return False

def get_user_metrics(date: datetime.date = None) -> Dict:
    """
    Get user metrics for a specific date.
    
    Args:
        date (datetime.date, optional): The date to get metrics for. Defaults to today.
        
    Returns:
        Dict: User metrics for the date
    """
    try:
        if date is None:
            date = datetime.date.today()
            
        date_str = date.strftime('%Y-%m-%d')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user_metrics WHERE date = ?", (date_str,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        else:
            return {}
            
    except Exception as e:
        logger.error(f"Error retrieving user metrics: {e}")
        return {}