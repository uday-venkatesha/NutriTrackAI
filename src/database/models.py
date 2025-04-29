import datetime
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class FoodEntry:
    """Represents a food entry in the nutrition tracker."""
    id: int = None
    food_item: str = None
    nutrition_data: Dict[str, Any] = None
    date: datetime.date = None
    timestamp: datetime.datetime = None
    
    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.date is None:
            self.date = datetime.date.today()
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()