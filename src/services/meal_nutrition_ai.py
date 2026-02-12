import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class MealNutritionAI:
    """
    AI сервис для анализа пищевой ценности блюд через Groq API
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found")
            self.client = None
            return

        self.client = Groq(api_key=api_key)

    def analyze_meal_nutrition(self, meal_name: str) -> dict:
        """
        Анализирует БЖУ и калории блюда по названию

        Args:
            meal_name: Название блюда (например "Chicken salad")

        Returns:
            {
                "name": "Chicken salad",
                "calories": 350,
                "protein": 30,
                "carbs": 15,
                "fats": 18
            }
        """
        if not self.client:
            return self._get_default_nutrition(meal_name)

        try:
            prompt = f"""Analyze the nutritional value of the following meal: "{meal_name}"

Return ONLY a JSON object (no markdown, no explanations):
{{
  "name": "{meal_name}",
  "calories": estimated_calories_integer,
  "protein": grams_of_protein_integer,
  "carbs": grams_of_carbs_integer,
  "fats": grams_of_fats_integer
}}

Provide realistic estimates based on a standard serving size.
"""

            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a nutrition expert. Provide accurate meal nutrition data.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=200,
            )

            text = response.choices[0].message.content.strip()

            # Очистка от markdown
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            nutrition = json.loads(text.strip())

            return nutrition

        except Exception as e:
            print(f"Error analyzing nutrition: {e}")
            return self._get_default_nutrition(meal_name)

    def suggest_meals(self, criteria: dict) -> list:
        """
        Подбирает блюда по критериям

        Args:
            criteria: {
                "ingredients": ["eggs", "beef"],
                "max_calories": 300,
                "min_protein": 25,
                ...
            }

        Returns:
            [
                {"name": "Beef omelette", "calories": 280, "protein": 28, ...},
                {"name": "Scrambled eggs with beef", "calories": 290, ...},
                ...
            ]
        """
        if not self.client:
            return []

        try:
            # Формируем критерии для промпта
            criteria_text = []

            if criteria.get("ingredients"):
                ingredients = ", ".join(criteria["ingredients"])
                criteria_text.append(f"- Must contain: {ingredients}")

            if criteria.get("max_calories"):
                criteria_text.append(f"- Max {criteria['max_calories']} calories")

            if criteria.get("min_protein"):
                criteria_text.append(f"- At least {criteria['min_protein']}g protein")

            if criteria.get("max_protein"):
                criteria_text.append(f"- Max {criteria['max_protein']}g protein")

            if criteria.get("max_carbs"):
                criteria_text.append(f"- Max {criteria['max_carbs']}g carbs")

            if criteria.get("max_fats"):
                criteria_text.append(f"- Max {criteria['max_fats']}g fats")

            criteria_str = "\n".join(criteria_text) if criteria_text else "Any healthy meals"

            prompt = f"""Suggest 4 meal options that meet these criteria:

{criteria_str}

Return ONLY a JSON array (no markdown, no explanations):
[
  {{"name": "Meal name", "calories": 0, "protein": 0, "carbs": 0, "fats": 0}},
  {{"name": "Meal name", "calories": 0, "protein": 0, "carbs": 0, "fats": 0}},
  {{"name": "Meal name", "calories": 0, "protein": 0, "carbs": 0, "fats": 0}},
  {{"name": "Meal name", "calories": 0, "protein": 0, "carbs": 0, "fats": 0}}
]

Provide realistic, tasty meal suggestions with accurate nutrition data.
"""

            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a nutrition expert and chef. Suggest creative, healthy meals.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.8,
                max_tokens=800,
            )

            text = response.choices[0].message.content.strip()

            # Очистка
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

            meals = json.loads(text.strip())

            return meals

        except Exception as e:
            print(f"Error suggesting meals: {e}")
            return []

    def _get_default_nutrition(self, meal_name: str) -> dict:
        """Возвращает усреднённые значения если API недоступен"""
        return {
            "name": meal_name,
            "calories": 300,
            "protein": 20,
            "carbs": 25,
            "fats": 10,
        }

