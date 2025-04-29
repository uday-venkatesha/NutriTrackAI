import logging
import datetime
from src.api.openai_client import NutritionAPI
from src.database.operations import add_food_entry, get_daily_entries
from src.analytics.nutrition_analyzer import analyze_daily_nutrition
from utils.food_parser import parse_food_input, is_food_entry
from utils.date_helpers import parse_date, format_date

logger = logging.getLogger(__name__)

class ChatbotMessageHandler:
    """Handles and processes user messages, determining appropriate responses."""
    
    def __init__(self):
        self.nutrition_api = NutritionAPI()
        
    def handle_message(self, message):
        """Process the user message and return an appropriate response."""
        message = message.strip()
        
        # Check for commands or specific message types
        if message.lower() == 'help':
            return self._get_help_message()
            
        elif message.lower().startswith('analyze') or message.lower().startswith('report'):
            # Format: "analyze [date]" or "report [date]"
            parts = message.split(maxsplit=1)
            date_str = parts[1] if len(parts) > 1 else None
            return self._generate_analysis(date_str)
            
        elif message.lower().startswith('today'):
            # Show today's entries
            return self._get_today_entries()
            
        elif is_food_entry(message):
            # Process as a food entry
            return self._process_food_entry(message)
            
        else:
            # Generic response for unrecognized messages
            return "I'm your nutrition tracking assistant. Tell me what you ate, or type 'help' for commands."
    
    def _get_help_message(self):
        """Returns help information for the user."""
        return """
Available commands:
- Tell me what you ate (e.g., "I had a turkey sandwich and an apple for lunch")
- "analyze [date]" - Get nutrition analysis for a specific date (defaults to today)
- "today" - See all food entries for today
- "help" - Show this help message
- "exit" - Exit the application
"""
    
    def _process_food_entry(self, message):
        """Process a food entry message, extract nutrition data and store it."""
        try:
            # Parse the food items from the message
            food_items = parse_food_input(message)
            
            if not food_items:
                return "I couldn't identify any food items in your message. Please try again."
            
            # Get nutrition information for each food item
            all_responses = []
            for food in food_items:
                # Get nutrition data from API
                nutrition_data = self.nutrition_api.get_nutrition_info(food)
                
                # Store in database
                add_food_entry(food, nutrition_data)
                
                # Generate user-friendly response
                response = f"Added {food} to your food log. "
                if nutrition_data.get('calories'):
                    response += f"(Calories: {nutrition_data.get('calories', 'unknown')})"
                
                all_responses.append(response)
            
            return "\n".join(all_responses) + "\n\nIs there anything else you ate today?"
            
        except Exception as e:
            logger.error(f"Error processing food entry: {e}")
            return "I encountered an error while processing your food entry. Please try again."
    
    def _generate_analysis(self, date_str=None):
        """Generate a nutrition analysis report for the specified date."""
        try:
            # Parse the date or use today
            if date_str:
                date = parse_date(date_str)
                if not date:
                    return f"I couldn't understand the date '{date_str}'. Please use a format like YYYY-MM-DD or 'yesterday'."
            else:
                date = datetime.date.today()
            
            # Get entries for the date
            entries = get_daily_entries(date)
            
            if not entries:
                return f"No food entries found for {format_date(date)}."
            
            # Generate the analysis
            analysis = analyze_daily_nutrition(entries)
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return "I encountered an error while generating your nutrition analysis. Please try again."
    
    def _get_today_entries(self):
        """Get all food entries for today."""
        try:
            today = datetime.date.today()
            entries = get_daily_entries(today)
            
            if not entries:
                return "You haven't logged any food items today."
            
            # Format the entries
            formatted_entries = []
            for entry in entries:
                food_item = entry['food_item']
                calories = entry['nutrition_data'].get('calories', 'unknown')
                time = entry['timestamp'].strftime("%I:%M %p")
                formatted_entries.append(f"- {food_item} ({calories} calories) at {time}")
            
            return f"Your food log for today:\n" + "\n".join(formatted_entries)
            
        except Exception as e:
            logger.error(f"Error retrieving today's entries: {e}")
            return "I encountered an error while retrieving your food entries. Please try again."