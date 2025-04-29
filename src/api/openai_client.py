import logging
import json
import openai
from config import OPENAI_API_KEY, GPT_MODEL

logger = logging.getLogger(__name__)

openai.api_key = OPENAI_API_KEY

class NutritionAPI:
    """Handles interactions with the OpenAI API for nutrition information."""

    def __init__(self):
        if not OPENAI_API_KEY:
            logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            raise ValueError("OpenAI API key not configured")

    def get_nutrition_info(self, food_item):
        """
        Gets nutrition information for a food item using the OpenAI GPT API.

        Args:
            food_item (str): Description of the food item

        Returns:
            dict: Nutrition data including calories, protein, carbs, fat, etc.
        """
        try:
            # Prompt GPT to return nutrition facts as JSON
            prompt = f"""
You are a nutrition expert. Given the following food description, estimate its nutrition facts as accurately as possible.
Return ONLY a JSON object with these fields:
- calories (numeric, in kcal)
- protein (numeric, in grams)
- carbohydrates (numeric, in grams)
- fat (numeric, in grams)
- fiber (numeric, in grams)
- sugar (numeric, in grams)
- sodium (numeric, in mg)

If any value is uncertain, provide your best estimate. Use typical portion sizes if not specified.
Food: {food_item}
JSON:
"""
            response = openai.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a nutrition assistant that provides only JSON nutrition data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            content = response.choices[0].message.content.strip()

            # Attempt to parse JSON
            try:
                nutrition_data = json.loads(content)
            except json.JSONDecodeError:
                import re
                match = re.search(r'({.*})', content, re.DOTALL)
                if match:
                    nutrition_data = json.loads(match.group(1))
                else:
                    logger.error(f"No JSON found in API response: {content}")
                    return self._get_default_nutrition_data(food_item)

            return self._validate_nutrition_data(nutrition_data, food_item)

        except Exception as e:
            logger.error(f"Error getting nutrition information for {food_item}: {e}")
            return self._get_default_nutrition_data(food_item)

    def _validate_nutrition_data(self, data, food_item):
        expected_fields = ['calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'sugar', 'sodium']
        for field in expected_fields:
            if field not in data:
                data[field] = None
            if isinstance(data[field], str):
                try:
                    import re
                    match = re.search(r'(\d+\.?\d*)', data[field])
                    if match:
                        data[field] = float(match.group(1))
                    else:
                        data[field] = None
                except Exception:
                    data[field] = None
        data['food_item'] = food_item
        return data

    def _get_default_nutrition_data(self, food_item):
        return {
            'calories': None,
            'protein': None,
            'carbohydrates': None,
            'fat': None,
            'fiber': None,
            'sugar': None,
            'sodium': None,
            'food_item': food_item
        }
