import random
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generates appropriate responses for the chatbot."""
    
    def __init__(self):
        # Load response templates
        self.templates = self._load_response_templates()
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different message types."""
        return {
            'greeting': [
                "Hello! Ready to track your nutrition today?",
                "Hi there! What have you eaten today?",
                "Hey! How can I help with your nutrition tracking today?"
            ],
            'food_entry_confirmation': [
                "Got it! I've added {food} to your log.",
                "Added {food} to your food diary.",
                "I've recorded {food} in your nutrition tracker."
            ],
            'analysis_intro': [
                "Here's your nutrition summary for {date}:",
                "I've analyzed your food intake for {date}:",
                "Here's how your nutrition looks for {date}:"
            ],
            'positive_feedback': [
                "Great job staying within your calorie goal!",
                "You're doing well with your nutrition today!",
                "Excellent work on managing your calories!"
            ],
            'suggestion': [
                "You might want to add more protein to your diet.",
                "Consider adding more fiber-rich foods to your meals.",
                "Try to reduce your sugar intake for better results."
            ],
            'farewell': [
                "Goodbye! Keep up the good work on your fitness journey!",
                "See you later! Remember to log all your meals for better tracking.",
                "Take care! Looking forward to helping you track your nutrition again."
            ],
            'help': [
                "I can help you track your food and analyze your nutrition. Just tell me what you ate, or ask for an analysis.",
                "You can tell me what you've eaten, and I'll track the nutrition. You can also ask for a daily or weekly report."
            ]
        }
    
    def generate_response(self, message_type: str, data: Dict[str, Any] = None) -> str:
        """
        Generate a response based on message type and data.
        
        Args:
            message_type (str): Type of message to generate
            data (Dict[str, Any], optional): Data to include in the response
            
        Returns:
            str: Generated response
        """
        if data is None:
            data = {}
        
        if message_type in self.templates:
            # Get a random template for the message type
            template = random.choice(self.templates[message_type])
            
            # Fill in template with data
            try:
                return template.format(**data)
            except KeyError as e:
                logger.error(f"Missing data for template: {e}")
                return template
        else:
            return "I'm not sure how to respond to that."
    
    def generate_food_entry_response(self, food_item: str, nutrition_data: Dict[str, Any]) -> str:
        """
        Generate a response for a food entry.
        
        Args:
            food_item (str): The food that was entered
            nutrition_data (Dict[str, Any]): Nutrition information
            
        Returns:
            str: Generated response
        """
        # Basic confirmation
        response = self.generate_response('food_entry_confirmation', {'food': food_item})
        
        # Add nutrition highlights if available
        if nutrition_data:
            calories = nutrition_data.get('calories')
            if calories:
                response += f" That contains approximately {calories} calories."
            
            # Add a random nutrition highlight
            possible_highlights = []
            
            protein = nutrition_data.get('protein')
            if protein and float(protein) > 15:
                possible_highlights.append(f"It's a good source of protein with {protein}g.")
            
            fiber = nutrition_data.get('fiber')
            if fiber and float(fiber) > 5:
                possible_highlights.append(f"It contains {fiber}g of fiber, which is great for digestion.")
            
            sugar = nutrition_data.get('sugar')
            if sugar and float(sugar) > 15:
                possible_highlights.append(f"Be aware that it contains {sugar}g of sugar.")
            
            if possible_highlights:
                response += " " + random.choice(possible_highlights)
        
        return response
    
    def generate_analysis_response(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generate a response for nutritional analysis.
        
        Args:
            analysis_data (Dict[str, Any]): Analysis information
            
        Returns:
            str: Generated response
        """
        # This should be implemented based on your specific analysis format
        # For now, just return the raw analysis
        return str(analysis_data)
    
    def generate_no_entries_response(self) -> str:
        """Generate a response when no food entries are found."""
        responses = [
            "I don't see any food entries for this period. Try logging your meals by telling me what you ate.",
            "You haven't logged any food yet. Would you like to add something you've eaten?",
            "No food entries found. Remember to log your meals for better tracking!"
        ]
        return random.choice(responses)
    
    def generate_error_response(self) -> str:
        """Generate a response for when an error occurs."""
        responses = [
            "I'm sorry, I encountered an error while processing that. Could you try again?",
            "Something went wrong on my end. Let's try a different approach.",
            "I couldn't complete that action. Please try again or try a different request."
        ]
        return random.choice(responses)