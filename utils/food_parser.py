import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# Food-related keywords to help identify food entries
MEAL_KEYWORDS = ['ate', 'had', 'consumed', 'eat', 'having', 'drinking', 'drank', 'lunch', 'dinner', 'breakfast',
                'snack', 'meal', 'food', 'calories']

def is_food_entry(message: str) -> bool:
    """
    Determine if a message is likely describing food that was eaten.
    
    Args:
        message (str): The user message to analyze
        
    Returns:
        bool: True if the message appears to be a food entry
    """
    message = message.lower()
    
    # Check for meal keywords
    if any(keyword in message for keyword in MEAL_KEYWORDS):
        return True
        
    # Check for common food entry patterns
    patterns = [
        r'i (?:ate|had|consumed)',
        r'for (?:breakfast|lunch|dinner|snack)',
        r'(?:today|this morning|this afternoon|this evening)'
    ]
    
    for pattern in patterns:
        if re.search(pattern, message):
            return True
    
    # If no clear indicators, assume it might be a food entry if it's relatively short 
    # and doesn't look like a command or question
    if len(message.split()) < 15 and not message.endswith('?'):
        return True
        
    return False

def parse_food_input(message: str) -> List[str]:
    """
    Extract food items from a user message.
    
    Args:
        message (str): The user message containing food information
        
    Returns:
        List[str]: List of food items extracted from the message
    """
    # Remove common prefixes that aren't part of the food
    prefixes = [
        r'^i (?:ate|had|consumed|eat|have|am having|am eating)',
        r'^(?:today|this morning|this afternoon|this evening)',
        r'^for (?:breakfast|lunch|dinner|snack)',
        r'^my (?:breakfast|lunch|dinner|snack)'
    ]
    
    cleaned_message = message.lower()
    for prefix in prefixes:
        cleaned_message = re.sub(prefix, '', cleaned_message).strip()
    
    # Split on common delimiters
    if ',' in cleaned_message:
        # Split by commas
        items = [item.strip() for item in cleaned_message.split(',')]
    elif ' and ' in cleaned_message:
        # Split by "and"
        items = [item.strip() for item in cleaned_message.split(' and ')]
    elif ';' in cleaned_message:
        # Split by semicolons
        items = [item.strip() for item in cleaned_message.split(';')]
    else:
        # Assume it's a single item
        items = [cleaned_message.strip()]
    
    # Clean up items and remove empty ones
    cleaned_items = []
    for item in items:
        # Remove words like "some", "a", "an" at the beginning
        item = re.sub(r'^(?:some|a|an|the)\s+', '', item).strip()
        
        # Remove specific timing words
        item = re.sub(r'(?:for|at|during)\s+(?:breakfast|lunch|dinner|snack)', '', item).strip()
        
        if item:
            cleaned_items.append(item)
    
    return cleaned_items

def extract_portion_info(food_item: str) -> tuple:
    """
    Extract portion information from a food item description.
    
    Args:
        food_item (str): Description of food possibly including portion info
        
    Returns:
        tuple: (food_name, quantity, unit)
    """
    # Patterns to match common portion formats
    patterns = [
        # "2 cups of rice"
        r'(\d+(?:\.\d+)?)\s+(cup|cups|oz|ounces|tbsp|tablespoons|tsp|teaspoons|g|grams|lb|pounds|slice|slices|piece|pieces)\s+(?:of\s+)?(.+)',
        # "a cup of rice"
        r'(?:a|an)\s+(cup|oz|ounce|tbsp|tablespoon|tsp|teaspoon|g|gram|lb|pound|slice|piece)\s+(?:of\s+)?(.+)',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, food_item)
        if match:
            groups = match.groups()
            if len(groups) == 3:  # numeric quantity
                quantity = float(groups[0])
                unit = groups[1]
                food = groups[2]
                return (food, quantity, unit)
            elif len(groups) == 2:  # "a" or "an" quantity (assume 1)
                unit = groups[0]
                food = groups[1]
                return (food, 1, unit)
    
    # No portion info found
    return (food_item, None, None)