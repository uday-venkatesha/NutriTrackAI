import logging
import json
import openai
from config import OPENAI_API_KEY, GPT_MODEL

logger = logging.getLogger(__name__)

# Configure OpenAI API
openai.api_key = OPENAI_API_KEY

class NutritionAPI:
    """Handles interactions with the OpenAI API for nutrition information."""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            raise ValueError("OpenAI API key not configured")
    
    def get_nutrition_info(self, food_item):
        """
        Gets nutrition information for a food item using the ChatGPT API.
        
        Args:
            food_item (str): Description of the food item
            
        Returns:
            dict: Nutrition data including calories, protein, carbs, fat, etc.
        """
        try:
            # Construct the prompt for the API
            prompt = f"""
            Please provide detailed nutrition information for: {food_item}
            
            Return the data in JSON format with the following fields:
            - calories (numeric, in kcal)
            - protein (numeric, in grams)
            - carbohydrates (numeric, in grams)
            - fat (numeric, in grams)
            - fiber (numeric, in grams)
            - sugar (numeric, in grams)
            - sodium (numeric, in mg)
            
            If any value is uncertain, provide your best estimate.
            Return ONLY the JSON object without any additional text or explanation.
            """
            
            # Call the OpenAI API
            response = openai.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a nutrition information assistant that provides accurate nutrition data in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=500
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content.strip()
            
            # Handle potential JSON formatting issues
            try:
                # Try direct JSON parsing
                nutrition_data = json.loads(content)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from the text
                import re
                json_match = re.search(r'({.*})', content, re.DOTALL)
                if json_match:
                    try:
                        nutrition_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON from API response: {content}")
                        return self._get_default_nutrition_data()
                else:
                    logger.error(f"No JSON found in API response: {content}")
                    return self._get_default_nutrition_data()
            
            # Validate nutrition data
            return self._validate_nutrition_data(nutrition_data, food_item)
            
        except Exception as e:
            logger.error(f"Error getting nutrition information for {food_item}: {e}")
            return self._get_default_nutrition_data()
    
    def _validate_nutrition_data(self, data, food_item):
        """Validates and cleans the nutrition data."""
        # Ensure all expected fields are present
        expected_fields = ['calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium']
        for field in expected_fields:
            if field not in data:
                data[field] = None
                
        # Convert string values to appropriate numeric types
        for field in expected_fields:
            if field in data and isinstance(data[field], str):
                try:
                    # Extract numeric values from strings like "10g" or "150 kcal"
                    import re
                    numeric_match = re.search(r'(\d+\.?\d*)', data[field])
                    if numeric_match:
                        data[field] = float(numeric_match.group(1))
                    else:
                        data[field] = None
                except (ValueError, TypeError):
                    data[field] = None
        
        # Add food item reference
        data['food_item'] = food_item
        
        return data
    
    def _get_default_nutrition_data(self):
        """Returns default nutrition data structure with null values."""
        return {
            'calories': None,
            'protein': None,
            'carbohydrates': None,
            'fat': None,
            'fiber': None,
            'sugar': None,
            'sodium': None
        }