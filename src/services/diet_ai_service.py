import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class DietAIService:
    """AI ÑÐµÑ€Ð²Ð¸Ñ Ð´Ð»Ñ Ð³ÐµÐ½ÐµÑ€Ð°Ñ†Ð¸Ð¸ Ð¿Ð»Ð°Ð½Ð¾Ð² Ð¿Ð¸Ñ‚Ð°Ð½Ð¸Ñ Ñ‡ÐµÑ€ÐµÐ· Groq API"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found in .env")
            self.client = None
            return
        
        self.client = Groq(api_key=api_key)
        
        # Ð¦ÐµÐ»ÐµÐ²Ñ‹Ðµ ÐºÐ°Ð»Ð¾Ñ€Ð¸Ð¸ Ð¿Ð¾ Ñ†ÐµÐ»ÑÐ¼ Ð´Ð¸ÐµÑ‚Ñ‹
        self.CALORIE_TARGETS = {
            "weight_loss": {"min": 1500, "max": 1700, "daily": 1600},
            "muscle_gain": {"min": 2500, "max": 2800, "daily": 2650},
            "healthy_lifestyle": {"min": 2000, "max": 2200, "daily": 2100},
            "meal_planning": {"min": 2000, "max": 2200, "daily": 2100}
        }
    
    def get_target_calories(self, goal):
        """Ð’Ð¾Ð·Ð²Ñ€Ð°Ñ‰Ð°ÐµÑ‚ Ñ†ÐµÐ»ÐµÐ²Ñ‹Ðµ ÐºÐ°Ð»Ð¾Ñ€Ð¸Ð¸ Ð´Ð»Ñ Ñ†ÐµÐ»Ð¸"""
        return self.CALORIE_TARGETS.get(goal, {"daily": 2000})["daily"]
    
    def build_diet_prompt(self, preferences, target_calories, restrictions_text):
        """Ð¡Ñ‚Ñ€Ð¾Ð¸Ñ‚ Ð¿Ñ€Ð¾Ð¼Ð¿Ñ‚ Ð´Ð»Ñ Groq API"""
        
        goal = preferences.get("diet_goal", "meal_planning")
        meal_types = preferences.get("meal_preference", [])
        if isinstance(meal_types, str):
            meal_types = [meal_types]
        
        cuisines = preferences.get("cuisine_preference", [])
        avoid_foods = preferences.get("avoid_foods", [])
        meal_frequency = preferences.get("meal_frequency", "3")
        
        # Ð¤Ð¾Ñ€Ð¼Ð°Ñ‚Ð¸Ñ€ÑƒÐµÐ¼ Ñ‚Ð¸Ð¿Ñ‹ Ð¿Ð¸Ñ‚Ð°Ð½Ð¸Ñ
        meal_type_text = ", ".join(meal_types) if meal_types else "balanced"
        
        # Ð¤Ð¾Ñ€Ð¼Ð°Ñ‚Ð¸Ñ€ÑƒÐµÐ¼ ÐºÑƒÑ…Ð½Ð¸
        cuisine_text = ", ".join(cuisines) if cuisines else "any cuisine"
        
        # Ð¤Ð¾Ñ€Ð¼Ð°Ñ‚Ð¸Ñ€ÑƒÐµÐ¼ Ð¿Ñ€Ð¾Ð´ÑƒÐºÑ‚Ñ‹ Ð´Ð»Ñ Ð¸Ð·Ð±ÐµÐ³Ð°Ð½Ð¸Ñ
        avoid_text = ", ".join(avoid_foods) if avoid_foods else "none"
        
        # ÐžÐ¿Ñ€ÐµÐ´ÐµÐ»ÑÐµÐ¼ Ð¿Ñ€Ð¸Ñ‘Ð¼Ñ‹ Ð¿Ð¸Ñ‰Ð¸
        meals_per_day = int(meal_frequency)
        meal_names = []
        if meals_per_day == 2:
            meal_names = ["breakfast", "dinner"]
        elif meals_per_day == 3:
            meal_names = ["breakfast", "lunch", "dinner"]
        elif meals_per_day >= 4:
            meal_names = ["breakfast", "lunch", "snack", "dinner"]
        
        # Ð¡Ð¿ÐµÑ†Ð¸Ñ„Ð¸Ñ‡Ð½Ñ‹Ðµ Ñ€ÐµÐºÐ¾Ð¼ÐµÐ½Ð´Ð°Ñ†Ð¸Ð¸ Ð¿Ð¾ Ñ†ÐµÐ»Ð¸
        goal_instructions = {
            "weight_loss": "Focus on low-calorie, high-protein meals. Include plenty of vegetables. Avoid sugary and fried foods.",
            "muscle_gain": "Focus on high-protein meals (chicken, fish, eggs, legumes). Include complex carbs (rice, pasta, potatoes).",
            "healthy_lifestyle": "Focus on balanced nutrition with variety. Include fruits, vegetables, whole grains, and lean proteins.",
            "meal_planning": "Create practical, easy-to-prepare meals suitable for students. Focus on affordability and simplicity."
        }
        
        goal_instruction = goal_instructions.get(goal, goal_instructions["meal_planning"])
        
        prompt = f"""Create a 7-day meal plan for a student.

GOAL: {goal.replace('_', ' ').title()}
TARGET: {target_calories} kcal/day (approximately {target_calories // meals_per_day} kcal per meal)

DIETARY PREFERENCES:
- Diet Type: {meal_type_text}
- Favorite Cuisines: {cuisine_text}
- Foods to Avoid: {avoid_text}
- Meals per day: {meal_frequency}

MEDICAL RESTRICTIONS:
{restrictions_text}

GOAL-SPECIFIC INSTRUCTIONS:
{goal_instruction}

CRITICAL RULES:
1. ALL meals MUST be {meal_type_text} (strictly follow this!)
2. NEVER include these foods: {avoid_text}
3. Respect all medical restrictions listed above
4. Each meal should be realistic and easy to prepare for students
5. Include variety across the week (don't repeat meals)
6. Provide accurate calorie and macro estimates

Return ONLY valid JSON (no markdown, no backticks, no explanations):
{{
  "monday": {{
    {self._format_meal_structure(meal_names)}
  }},
  "tuesday": {{
    {self._format_meal_structure(meal_names)}
  }},
  "wednesday": {{
    {self._format_meal_structure(meal_names)}
  }},
  "thursday": {{
    {self._format_meal_structure(meal_names)}
  }},
  "friday": {{
    {self._format_meal_structure(meal_names)}
  }},
  "saturday": {{
    {self._format_meal_structure(meal_names)}
  }},
  "sunday": {{
    {self._format_meal_structure(meal_names)}
  }}
}}

Each meal must have:
- "name": string (meal name)
- "calories": number (estimated calories)
- "protein": number (grams)
- "carbs": number (grams)
- "fats": number (grams)"""

        return prompt
    
    def _format_meal_structure(self, meal_names):
        """Ð¤Ð¾Ñ€Ð¼Ð°Ñ‚Ð¸Ñ€ÑƒÐµÑ‚ ÑÑ‚Ñ€ÑƒÐºÑ‚ÑƒÑ€Ñƒ Ð¿Ñ€Ð¸Ñ‘Ð¼Ð¾Ð² Ð¿Ð¸Ñ‰Ð¸ Ð´Ð»Ñ JSON"""
        examples = {
            "breakfast": '"breakfast": {"name": "Oatmeal with berries", "calories": 350, "protein": 12, "carbs": 55, "fats": 8}',
            "lunch": '"lunch": {"name": "Grilled Chicken Salad", "calories": 450, "protein": 35, "carbs": 20, "fats": 15}',
            "dinner": '"dinner": {"name": "Salmon with Broccoli", "calories": 550, "protein": 40, "carbs": 30, "fats": 20}',
            "snack": '"snack": {"name": "Greek Yogurt with Nuts", "calories": 200, "protein": 15, "carbs": 12, "fats": 10}'
        }
        
        return ",\n    ".join([examples.get(meal, f'"{meal}": {{"name": "TBD", "calories": 0, "protein": 0, "carbs": 0, "fats": 0}}') for meal in meal_names])
    
    def format_restrictions_for_prompt(self, medical_notes):
        """Ð¤Ð¾Ñ€Ð¼Ð°Ñ‚Ð¸Ñ€ÑƒÐµÑ‚ Ð¼ÐµÐ´Ð¸Ñ†Ð¸Ð½ÑÐºÐ¸Ðµ Ð¾Ð³Ñ€Ð°Ð½Ð¸Ñ‡ÐµÐ½Ð¸Ñ Ð´Ð»Ñ Ð¿Ñ€Ð¾Ð¼Ð¿Ñ‚Ð°"""
        if not medical_notes or medical_notes.strip() == "":
            return "No medical restrictions."
        
        # ÐŸÐ¾Ð¿Ñ‹Ñ‚ÐºÐ° Ð¸Ð¼Ð¿Ð¾Ñ€Ñ‚Ð¸Ñ€Ð¾Ð²Ð°Ñ‚ÑŒ Ð±Ð°Ð·Ñƒ Ð¼ÐµÐ´Ð¸Ñ†Ð¸Ð½ÑÐºÐ¸Ñ… Ð¾Ð³Ñ€Ð°Ð½Ð¸Ñ‡ÐµÐ½Ð¸Ð¹
        try:
            from data.medical_restrictions import get_restrictions_for_conditions
            restrictions = get_restrictions_for_conditions(medical_notes)
            if restrictions:
                return restrictions
        except ImportError:
            pass
        
        # Ð•ÑÐ»Ð¸ Ð±Ð°Ð·Ñ‹ Ð½ÐµÑ‚, Ð¿Ñ€Ð¾ÑÑ‚Ð¾ Ð²Ð¾Ð·Ð²Ñ€Ð°Ñ‰Ð°ÐµÐ¼ Ñ‚ÐµÐºÑÑ‚
        return f"User notes: {medical_notes}\nPlease avoid foods that may be harmful for these conditions."
    
    def generate_weekly_plan(self, user_preferences, medical_notes="", available_ingredients=None):  # âœ… ÐÐžÐ’Ð«Ð™ Ð¿Ð°Ñ€Ð°Ð¼ÐµÑ‚Ñ€
        """
        Ð“ÐµÐ½ÐµÑ€Ð¸Ñ€ÑƒÐµÑ‚ Ð¿Ð»Ð°Ð½ Ð¿Ð¸Ñ‚Ð°Ð½Ð¸Ñ Ð½Ð° Ð½ÐµÐ´ÐµÐ»ÑŽ Ñ‡ÐµÑ€ÐµÐ· Groq API.
        
        Args:
            user_preferences (dict): ÐŸÑ€ÐµÐ´Ð¿Ð¾Ñ‡Ñ‚ÐµÐ½Ð¸Ñ Ð¸Ð· diet_preferences
            medical_notes (str): ÐœÐµÐ´Ð¸Ñ†Ð¸Ð½ÑÐºÐ¸Ðµ Ð¾Ð³Ñ€Ð°Ð½Ð¸Ñ‡ÐµÐ½Ð¸Ñ
        
        Returns:
            dict: ÐŸÐ»Ð°Ð½ Ð½Ð° 7 Ð´Ð½ÐµÐ¹ Ð¸Ð»Ð¸ None Ð¿Ñ€Ð¸ Ð¾ÑˆÐ¸Ð±ÐºÐµ
        """
        if not self.client:
            return None
        
        try:
            # ÐŸÐ¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ñ†ÐµÐ»ÑŒ Ð¸ ÐºÐ°Ð»Ð¾Ñ€Ð¸Ð¸
            goal = user_preferences.get("diet_goal", "meal_planning")
            target_calories = self.get_target_calories(goal)
            
            # Ð¤Ð¾Ñ€Ð¼Ð°Ñ‚Ð¸Ñ€ÑƒÐµÐ¼ Ð¼ÐµÐ´Ð¸Ñ†Ð¸Ð½ÑÐºÐ¸Ðµ Ð¾Ð³Ñ€Ð°Ð½Ð¸Ñ‡ÐµÐ½Ð¸Ñ
            restrictions_text = self.format_restrictions_for_prompt(medical_notes)
            
            # Ð¡Ñ‚Ñ€Ð¾Ð¸Ð¼ Ð¿Ñ€Ð¾Ð¼Ð¿Ñ‚
            prompt = self.build_diet_prompt(user_preferences, target_calories, restrictions_text)
            
            # âœ… ÐÐžÐ’ÐžÐ•: ÐžÐ³Ñ€Ð°Ð½Ð¸Ñ‡Ð¸Ð²Ð°ÐµÐ¼ AI ÐºÑƒÐ¿Ð»ÐµÐ½Ð½Ñ‹Ð¼Ð¸ Ð¿Ñ€Ð¾Ð´ÑƒÐºÑ‚Ð°Ð¼Ð¸ Ð¸Ð· Grocery Store
            if available_ingredients:
                ingredient_list = ", ".join(available_ingredients)
                prompt += f"""

IMPORTANT CONSTRAINT - USE ONLY AVAILABLE INGREDIENTS:
The user has purchased these ingredients this week. You MUST create meals using combinations of these ingredients only:
{ingredient_list}

Do NOT suggest ingredients that are not in this list. Be creative with what's available."""
            
            print("Sending request to Groq API for meal plan generation...")
            
            # Ð’Ñ‹Ð·Ñ‹Ð²Ð°ÐµÐ¼ Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional nutritionist and meal planning expert. Generate accurate, healthy, and practical meal plans."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.8,  # Ð’Ñ‹ÑˆÐµ Ð´Ð»Ñ ÐºÑ€ÐµÐ°Ñ‚Ð¸Ð²Ð½Ð¾ÑÑ‚Ð¸
                max_tokens=2000,  # Ð‘Ð¾Ð»ÑŒÑˆÐµ Ð´Ð»Ñ Ð¿Ð¾Ð»Ð½Ð¾Ð³Ð¾ Ð¿Ð»Ð°Ð½Ð°
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            # ÐžÑ‡Ð¸Ñ‰Ð°ÐµÐ¼ Ð¾Ñ‚ markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # ÐŸÐ°Ñ€ÑÐ¸Ð¼ JSON
            plan = json.loads(response_text)
            
            print("âœ… Meal plan generated successfully!")
            
            return {
                "goal": goal,
                "target_calories": target_calories,
                "plan": plan,
                "created_at": datetime.now().isoformat()
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Response: {response_text}")
            return None
        except Exception as e:
            print(f"Error generating meal plan: {e}")
            return None
    
    def replace_meal(self, user_preferences, medical_notes, day, meal_type):
        """
        Ð—Ð°Ð¼ÐµÐ½ÑÐµÑ‚ ÐºÐ¾Ð½ÐºÑ€ÐµÑ‚Ð½Ð¾Ðµ Ð±Ð»ÑŽÐ´Ð¾ Ð½Ð¾Ð²Ñ‹Ð¼.
        
        Args:
            user_preferences (dict): ÐŸÑ€ÐµÐ´Ð¿Ð¾Ñ‡Ñ‚ÐµÐ½Ð¸Ñ
            medical_notes (str): ÐœÐµÐ´Ð¸Ñ†Ð¸Ð½ÑÐºÐ¸Ðµ Ð¾Ð³Ñ€Ð°Ð½Ð¸Ñ‡ÐµÐ½Ð¸Ñ
            day (str): Ð”ÐµÐ½ÑŒ Ð½ÐµÐ´ÐµÐ»Ð¸ (monday, tuesday, ...)
            meal_type (str): Ð¢Ð¸Ð¿ Ð¿Ñ€Ð¸Ñ‘Ð¼Ð° Ð¿Ð¸Ñ‰Ð¸ (breakfast, lunch, dinner)
        
        Returns:
            dict: ÐÐ¾Ð²Ð¾Ðµ Ð±Ð»ÑŽÐ´Ð¾ Ð¸Ð»Ð¸ None
        """
        if not self.client:
            return None
        
        try:
            goal = user_preferences.get("diet_goal", "meal_planning")
            target_calories = self.get_target_calories(goal)
            meal_frequency = int(user_preferences.get("meal_frequency", "3"))
            calories_per_meal = target_calories // meal_frequency
            
            meal_types = user_preferences.get("meal_preference", [])
            if isinstance(meal_types, str):
                meal_types = [meal_types]
            meal_type_text = ", ".join(meal_types) if meal_types else "balanced"
            
            avoid_foods = user_preferences.get("avoid_foods", [])
            avoid_text = ", ".join(avoid_foods) if avoid_foods else "none"
            
            restrictions_text = self.format_restrictions_for_prompt(medical_notes)
            
            prompt = f"""Generate ONE {meal_type} meal for {day}.

REQUIREMENTS:
- Diet Type: {meal_type_text}
- Avoid: {avoid_text}
- Target Calories: ~{calories_per_meal} kcal
- Goal: {goal.replace('_', ' ').title()}

MEDICAL RESTRICTIONS:
{restrictions_text}

Return ONLY valid JSON (no markdown):
{{
  "name": "Meal name",
  "calories": number,
  "protein": number,
  "carbs": number,
  "fats": number
}}"""
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a nutritionist. Generate one meal suggestion."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.9,  # Ð’Ñ‹ÑÐ¾ÐºÐ°Ñ ÐºÑ€ÐµÐ°Ñ‚Ð¸Ð²Ð½Ð¾ÑÑ‚ÑŒ
                max_tokens=200,
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            # ÐžÑ‡Ð¸ÑÑ‚ÐºÐ°
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            new_meal = json.loads(response_text)
            
            return new_meal
            
        except Exception as e:
            print(f"Error replacing meal: {e}")
            return None