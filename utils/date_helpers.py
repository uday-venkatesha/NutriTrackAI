import re
import datetime
from dateutil import parser
import logging

logger = logging.getLogger(__name__)

def parse_date(date_str: str) -> datetime.date:
    """
    Parse a date string into a datetime.date object.
    Handles various formats and relative date descriptions.
    
    Args:
        date_str (str): String describing a date
        
    Returns:
        datetime.date: The parsed date, or None if parsing failed
    """
    if not date_str:
        return datetime.date.today()
    
    date_str = date_str.lower().strip()
    
    # Handle relative dates
    today = datetime.date.today()
    
    if date_str in ['today', 'now']:
        return today
    elif date_str in ['yesterday', 'last day']:
        return today - datetime.timedelta(days=1)
    elif date_str in ['tomorrow']:
        return today + datetime.timedelta(days=1)
    elif date_str in ['this week']:
        # Start of current week (Monday)
        return today - datetime.timedelta(days=today.weekday())
    elif date_str in ['last week']:
        # Start of last week
        return today - datetime.timedelta(days=today.weekday() + 7)
    
    # Handle "X days ago"
    days_ago_match = re.match(r'(\d+) days? ago', date_str)
    if days_ago_match:
        days = int(days_ago_match.group(1))
        return today - datetime.timedelta(days=days)
    
    # Handle "last Monday", "next Friday", etc.
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    last_weekday_match = re.match(r'last (monday|tuesday|wednesday|thursday|friday|saturday|sunday)', date_str)
    if last_weekday_match:
        target_weekday = weekdays[last_weekday_match.group(1)]
        days_ago = (today.weekday() - target_weekday) % 7
        if days_ago == 0:
            days_ago = 7  # If today is the target weekday, get last week's
        return today - datetime.timedelta(days=days_ago)
    
    next_weekday_match = re.match(r'next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)', date_str)
    if next_weekday_match:
        target_weekday = weekdays[next_weekday_match.group(1)]
        days_ahead = (target_weekday - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7  # If today is the target weekday, get next week's
        return today + datetime.timedelta(days=days_ahead)
    
    # Try to parse as a date string using dateutil
    try:
        parsed_date = parser.parse(date_str, dayfirst=False, yearfirst=False)
        return parsed_date.date()
    except:
        logger.warning(f"Could not parse date string: {date_str}")
        return None

def format_date(date_obj: datetime.date, format_str: str = "%Y-%m-%d") -> str:
    """
    Format a date object as a string.
    
    Args:
        date_obj (datetime.date): The date to format
        format_str (str, optional): Format string. Defaults to "%Y-%m-%d".
        
    Returns:
        str: Formatted date string
    """
    return date_obj.strftime(format_str)

def get_date_range(range_type: str, end_date: datetime.date = None) -> tuple:
    """
    Get start and end dates for common date ranges.
    
    Args:
        range_type (str): Type of range ('week', 'month', 'year')
        end_date (datetime.date, optional): End date for the range. Defaults to today.
        
    Returns:
        tuple: (start_date, end_date)
    """
    if end_date is None:
        end_date = datetime.date.today()
    
    if range_type == 'week':
        # Current week (Monday to Sunday)
        start_date = end_date - datetime.timedelta(days=end_date.weekday())
        return start_date, end_date
    
    elif range_type == 'month':
        # Current month
        start_date = end_date.replace(day=1)
        return start_date, end_date
    
    elif range_type == 'year':
        # Current year
        start_date = end_date.replace(month=1, day=1)
        return start_date, end_date
    
    elif range_type == 'last_7_days':
        # Last 7 days including today
        start_date = end_date - datetime.timedelta(days=6)
        return start_date, end_date
    
    elif range_type == 'last_30_days':
        # Last 30 days including today
        start_date = end_date - datetime.timedelta(days=29)
        return start_date, end_date
    
    # Default to last 7 days if range_type is not recognized
    start_date = end_date - datetime.timedelta(days=6)
    return start_date, end_date