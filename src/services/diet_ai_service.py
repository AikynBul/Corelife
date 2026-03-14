import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# USDA FoodData Central integration for accurate nutrition data
try:
    from services.usda_service import USDAService
    _usda = USDAService()
except Exception:
    _usda = None

load_dotenv()

class DietAIService:
    """AI Г‘ВЃГђВµГ‘в‚¬ГђВІГђВёГ‘ВЃ ГђВґГђВ»Г‘ВЏ ГђВіГђВµГђВЅГђВµГ‘в‚¬ГђВ°Г‘вЂ ГђВёГђВё ГђВїГђВ»ГђВ°ГђВЅГђВѕГђВІ ГђВїГђВёГ‘вЂљГђВ°ГђВЅГђВёГ‘ВЏ Г‘вЂЎГђВµГ‘в‚¬ГђВµГђВ· Groq API"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found in .env")
            self.client = None
            return
        
        self.client = Groq(api_key=api_key)
        
        # ГђВ¦ГђВµГђВ»ГђВµГђВІГ‘вЂ№ГђВµ ГђВєГђВ°ГђВ»ГђВѕГ‘в‚¬ГђВёГђВё ГђВїГђВѕ Г‘вЂ ГђВµГђВ»Г‘ВЏГђВј ГђВґГђВёГђВµГ‘вЂљГ‘вЂ№
        self.CALORIE_TARGETS = {
            "weight_loss": {"daily": 1800},
            "muscle_gain": {"daily": 3000},
            "healthy_lifestyle": {"daily": 2200},
            "meal_planning": {"daily": 2000},
        }
        self.MACRO_TARGETS = {
            "weight_loss": {"protein": 35, "carbs": 40, "fat": 25},
            "muscle_gain": {"protein": 30, "carbs": 45, "fat": 25},
            "healthy_lifestyle": {"protein": 25, "carbs": 50, "fat": 25},
            "meal_planning": {"protein": 25, "carbs": 50, "fat": 25},
        }
    
    def get_target_calories(self, goal):
        """ГђвЂ™ГђВѕГђВ·ГђВІГ‘в‚¬ГђВ°Г‘вЂ°ГђВ°ГђВµГ‘вЂљ Г‘вЂ ГђВµГђВ»ГђВµГђВІГ‘вЂ№ГђВµ ГђВєГђВ°ГђВ»ГђВѕГ‘в‚¬ГђВёГђВё ГђВґГђВ»Г‘ВЏ Г‘вЂ ГђВµГђВ»ГђВё"""
        return self.CALORIE_TARGETS.get(goal, {"daily": 2000})["daily"]

    def get_macro_targets(self, goal):
        return self.MACRO_TARGETS.get(goal, {"protein": 25, "carbs": 50, "fat": 25})

    def calculate_macro_grams(self, target_calories, macro_targets):
        protein_pct = macro_targets["protein"] / 100
        carbs_pct = macro_targets["carbs"] / 100
        fat_pct = macro_targets["fat"] / 100
        return {
            "protein_g": round((target_calories * protein_pct) / 4),
            "carbs_g": round((target_calories * carbs_pct) / 4),
            "fat_g": round((target_calories * fat_pct) / 9),
        }
    
    def build_diet_prompt(self, preferences, target_calories, restrictions_text):
        """ГђВЎГ‘вЂљГ‘в‚¬ГђВѕГђВёГ‘вЂљ ГђВїГ‘в‚¬ГђВѕГђВјГђВїГ‘вЂљ ГђВґГђВ»Г‘ВЏ Groq API"""
        
        goal = preferences.get("diet_goal", "meal_planning")
        meal_types = preferences.get("meal_preference", [])
        if isinstance(meal_types, str):
            meal_types = [meal_types]
        
        cuisines = preferences.get("cuisine_preference", [])
        avoid_foods = preferences.get("avoid_foods", [])
        meal_frequency = preferences.get("meal_frequency", "3")
        
        # ГђВ¤ГђВѕГ‘в‚¬ГђВјГђВ°Г‘вЂљГђВёГ‘в‚¬Г‘Ж’ГђВµГђВј Г‘вЂљГђВёГђВїГ‘вЂ№ ГђВїГђВёГ‘вЂљГђВ°ГђВЅГђВёГ‘ВЏ
        meal_type_text = ", ".join(meal_types) if meal_types else "balanced"
        
        # ГђВ¤ГђВѕГ‘в‚¬ГђВјГђВ°Г‘вЂљГђВёГ‘в‚¬Г‘Ж’ГђВµГђВј ГђВєГ‘Ж’Г‘вЂ¦ГђВЅГђВё
        cuisine_text = ", ".join(cuisines) if cuisines else "any cuisine"
        
        # ГђВ¤ГђВѕГ‘в‚¬ГђВјГђВ°Г‘вЂљГђВёГ‘в‚¬Г‘Ж’ГђВµГђВј ГђВїГ‘в‚¬ГђВѕГђВґГ‘Ж’ГђВєГ‘вЂљГ‘вЂ№ ГђВґГђВ»Г‘ВЏ ГђВёГђВ·ГђВ±ГђВµГђВіГђВ°ГђВЅГђВёГ‘ВЏ
        avoid_text = ", ".join(avoid_foods) if avoid_foods else "none"
        
        # ГђЕѕГђВїГ‘в‚¬ГђВµГђВґГђВµГђВ»Г‘ВЏГђВµГђВј ГђВїГ‘в‚¬ГђВёГ‘вЂГђВјГ‘вЂ№ ГђВїГђВёГ‘вЂ°ГђВё
        meals_per_day = int(meal_frequency)
        meal_names = []
        if meals_per_day == 2:
            meal_names = ["breakfast", "dinner"]
        elif meals_per_day == 3:
            meal_names = ["breakfast", "lunch", "dinner"]
        elif meals_per_day >= 4:
            meal_names = ["breakfast", "lunch", "snack", "dinner"]

        macro_targets = self.get_macro_targets(goal)
        macro_grams = self.calculate_macro_grams(target_calories, macro_targets)
        weekly_calories = target_calories * 7
        weekly_protein = macro_grams["protein_g"] * 7
        weekly_carbs = macro_grams["carbs_g"] * 7
        weekly_fat = macro_grams["fat_g"] * 7
        
        # ГђВЎГђВїГђВµГ‘вЂ ГђВёГ‘вЂћГђВёГ‘вЂЎГђВЅГ‘вЂ№ГђВµ Г‘в‚¬ГђВµГђВєГђВѕГђВјГђВµГђВЅГђВґГђВ°Г‘вЂ ГђВёГђВё ГђВїГђВѕ Г‘вЂ ГђВµГђВ»ГђВё
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
WEEKLY TARGET: {weekly_calories} kcal/week

DIETARY PREFERENCES:
- Diet Type: {meal_type_text}
- Favorite Cuisines: {cuisine_text}
- Foods to Avoid: {avoid_text}
- Meals per day: {meal_frequency}

MEDICAL RESTRICTIONS:
{restrictions_text}

GOAL-SPECIFIC INSTRUCTIONS:
{goal_instruction}

IMPORTANT: Calculate calories and macros correctly.
Daily macro targets for {goal.replace('_', ' ').title()}:
- Protein: {macro_grams["protein_g"]}g ({macro_targets["protein"]}%)
- Carbs: {macro_grams["carbs_g"]}g ({macro_targets["carbs"]}%)
- Fat: {macro_grams["fat_g"]}g ({macro_targets["fat"]}%)

Weekly macro targets:
- Protein: {weekly_protein}g/week
- Carbs: {weekly_carbs}g/week
- Fat: {weekly_fat}g/week

CRITICAL RULES:
1. ALL meals MUST be {meal_type_text} (strictly follow this!)
2. NEVER include these foods: {avoid_text}
3. Respect all medical restrictions listed above
4. Each meal should be realistic and easy to prepare for students
5. Include variety across the week (don't repeat meals)
6. Provide accurate calorie and macro estimates
7. Keep each day close to {target_calories} kcal (В±10%)
8. WEEKLY TOTAL must be around {weekly_calories} kcal
9. Each MEAL should have approximately {target_calories // meals_per_day} kcal
10. For Muscle Gain - prioritize HIGH PROTEIN sources (chicken, fish, beef, eggs, legumes)
11. For Weight Loss - prioritize LOW CALORIE, HIGH PROTEIN foods with lots of vegetables
12. Match the macro percentages: Protein {macro_targets["protein"]}%, Carbs {macro_targets["carbs"]}%, Fat {macro_targets["fat"]}%

Return ONLY valid JSON (no markdown, no backticks, no explanations):
{{
  "monday": {{
    {self._format_meal_structure(meal_names, goal, target_calories)}
  }},
  "tuesday": {{
    {self._format_meal_structure(meal_names, goal, target_calories)}
  }},
  "wednesday": {{
    {self._format_meal_structure(meal_names, goal, target_calories)}
  }},
  "thursday": {{
    {self._format_meal_structure(meal_names, goal, target_calories)}
  }},
  "friday": {{
    {self._format_meal_structure(meal_names, goal, target_calories)}
  }},
  "saturday": {{
    {self._format_meal_structure(meal_names, goal, target_calories)}
  }},
  "sunday": {{
    {self._format_meal_structure(meal_names, goal, target_calories)}
  }}
}}

Each meal must have:
- "name": string (meal name)
- "calories": number (estimated calories)
- "protein": number (grams)
- "carbs": number (grams)
- "fats": number (grams)"""

        return prompt
    def _format_meal_structure(self, meal_names, goal="meal_planning", target_calories=2000):
        """
        Форматирует структуру приёмов пищи с примерами под целевые калории и цель.
        """
        calories_per_meal = target_calories // len(meal_names)

        if goal == "muscle_gain":
            examples = {
                "breakfast": f'"breakfast": {{"name": "Scrambled eggs with whole grain toast and avocado", "calories": {int(calories_per_meal * 0.9)}, "protein": {int(calories_per_meal * 0.3 / 4)}, "carbs": {int(calories_per_meal * 0.45 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "lunch": f'"lunch": {{"name": "Grilled chicken breast with brown rice and vegetables", "calories": {int(calories_per_meal * 1.0)}, "protein": {int(calories_per_meal * 0.3 / 4)}, "carbs": {int(calories_per_meal * 0.45 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "dinner": f'"dinner": {{"name": "Beef steak with sweet potato and broccoli", "calories": {int(calories_per_meal * 1.1)}, "protein": {int(calories_per_meal * 0.3 / 4)}, "carbs": {int(calories_per_meal * 0.45 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "snack": f'"snack": {{"name": "Protein shake with banana and peanut butter", "calories": 400, "protein": 30, "carbs": 45, "fats": 10}}'
            }
        elif goal == "weight_loss":
            examples = {
                "breakfast": f'"breakfast": {{"name": "Greek yogurt with berries and chia seeds", "calories": {int(calories_per_meal * 0.9)}, "protein": {int(calories_per_meal * 0.35 / 4)}, "carbs": {int(calories_per_meal * 0.4 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "lunch": f'"lunch": {{"name": "Grilled chicken salad with olive oil dressing", "calories": {int(calories_per_meal * 1.0)}, "protein": {int(calories_per_meal * 0.35 / 4)}, "carbs": {int(calories_per_meal * 0.4 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "dinner": f'"dinner": {{"name": "Baked salmon with steamed vegetables", "calories": {int(calories_per_meal * 1.0)}, "protein": {int(calories_per_meal * 0.35 / 4)}, "carbs": {int(calories_per_meal * 0.4 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "snack": f'"snack": {{"name": "Apple slices with almond butter", "calories": 200, "protein": 8, "carbs": 20, "fats": 10}}'
            }
        elif goal == "healthy_lifestyle":
            examples = {
                "breakfast": f'"breakfast": {{"name": "Oatmeal with nuts and fresh fruit", "calories": {int(calories_per_meal * 0.9)}, "protein": {int(calories_per_meal * 0.25 / 4)}, "carbs": {int(calories_per_meal * 0.5 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "lunch": f'"lunch": {{"name": "Turkey sandwich on whole grain with side salad", "calories": {int(calories_per_meal * 1.0)}, "protein": {int(calories_per_meal * 0.25 / 4)}, "carbs": {int(calories_per_meal * 0.5 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "dinner": f'"dinner": {{"name": "Chicken stir-fry with quinoa and vegetables", "calories": {int(calories_per_meal * 1.1)}, "protein": {int(calories_per_meal * 0.25 / 4)}, "carbs": {int(calories_per_meal * 0.5 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "snack": f'"snack": {{"name": "Mixed nuts and dried fruit", "calories": 250, "protein": 10, "carbs": 25, "fats": 12}}'
            }
        else:
            examples = {
                "breakfast": f'"breakfast": {{"name": "Scrambled eggs with toast", "calories": {int(calories_per_meal * 0.9)}, "protein": {int(calories_per_meal * 0.25 / 4)}, "carbs": {int(calories_per_meal * 0.5 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "lunch": f'"lunch": {{"name": "Pasta with tomato sauce and vegetables", "calories": {int(calories_per_meal * 1.0)}, "protein": {int(calories_per_meal * 0.25 / 4)}, "carbs": {int(calories_per_meal * 0.5 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "dinner": f'"dinner": {{"name": "Baked chicken with rice and salad", "calories": {int(calories_per_meal * 1.1)}, "protein": {int(calories_per_meal * 0.25 / 4)}, "carbs": {int(calories_per_meal * 0.5 / 4)}, "fats": {int(calories_per_meal * 0.25 / 9)}}}',
                "snack": f'"snack": {{"name": "Fruit and yogurt", "calories": 200, "protein": 10, "carbs": 30, "fats": 5}}'
            }

        return ",\n    ".join([
            examples.get(
                meal,
                f'"{meal}": {{"name": "TBD", "calories": {calories_per_meal}, "protein": 0, "carbs": 0, "fats": 0}}',
            )
            for meal in meal_names
        ])
    def format_restrictions_for_prompt(self, medical_notes):
        """ГђВ¤ГђВѕГ‘в‚¬ГђВјГђВ°Г‘вЂљГђВёГ‘в‚¬Г‘Ж’ГђВµГ‘вЂљ ГђВјГђВµГђВґГђВёГ‘вЂ ГђВёГђВЅГ‘ВЃГђВєГђВёГђВµ ГђВѕГђВіГ‘в‚¬ГђВ°ГђВЅГђВёГ‘вЂЎГђВµГђВЅГђВёГ‘ВЏ ГђВґГђВ»Г‘ВЏ ГђВїГ‘в‚¬ГђВѕГђВјГђВїГ‘вЂљГђВ°"""
        if not medical_notes or medical_notes.strip() == "":
            return "No medical restrictions."
        
        # ГђЕёГђВѕГђВїГ‘вЂ№Г‘вЂљГђВєГђВ° ГђВёГђВјГђВїГђВѕГ‘в‚¬Г‘вЂљГђВёГ‘в‚¬ГђВѕГђВІГђВ°Г‘вЂљГ‘Е’ ГђВ±ГђВ°ГђВ·Г‘Ж’ ГђВјГђВµГђВґГђВёГ‘вЂ ГђВёГђВЅГ‘ВЃГђВєГђВёГ‘вЂ¦ ГђВѕГђВіГ‘в‚¬ГђВ°ГђВЅГђВёГ‘вЂЎГђВµГђВЅГђВёГђВ№
        try:
            from data.medical_restrictions import get_restrictions_for_conditions
            restrictions = get_restrictions_for_conditions(medical_notes)
            if restrictions:
                return restrictions
        except ImportError:
            pass
        
        # ГђвЂўГ‘ВЃГђВ»ГђВё ГђВ±ГђВ°ГђВ·Г‘вЂ№ ГђВЅГђВµГ‘вЂљ, ГђВїГ‘в‚¬ГђВѕГ‘ВЃГ‘вЂљГђВѕ ГђВІГђВѕГђВ·ГђВІГ‘в‚¬ГђВ°Г‘вЂ°ГђВ°ГђВµГђВј Г‘вЂљГђВµГђВєГ‘ВЃГ‘вЂљ
        return f"User notes: {medical_notes}\nPlease avoid foods that may be harmful for these conditions."
    
    def generate_weekly_plan(self, user_preferences, medical_notes="", available_ingredients=None):  # ГўЕ“вЂ¦ ГђВќГђЕѕГђвЂ™ГђВ«Гђв„ў ГђВїГђВ°Г‘в‚¬ГђВ°ГђВјГђВµГ‘вЂљГ‘в‚¬
        """
        ГђвЂњГђВµГђВЅГђВµГ‘в‚¬ГђВёГ‘в‚¬Г‘Ж’ГђВµГ‘вЂљ ГђВїГђВ»ГђВ°ГђВЅ ГђВїГђВёГ‘вЂљГђВ°ГђВЅГђВёГ‘ВЏ ГђВЅГђВ° ГђВЅГђВµГђВґГђВµГђВ»Г‘ЕЅ Г‘вЂЎГђВµГ‘в‚¬ГђВµГђВ· Groq API.
        
        Args:
            user_preferences (dict): ГђЕёГ‘в‚¬ГђВµГђВґГђВїГђВѕГ‘вЂЎГ‘вЂљГђВµГђВЅГђВёГ‘ВЏ ГђВёГђВ· diet_preferences
            medical_notes (str): ГђЕ“ГђВµГђВґГђВёГ‘вЂ ГђВёГђВЅГ‘ВЃГђВєГђВёГђВµ ГђВѕГђВіГ‘в‚¬ГђВ°ГђВЅГђВёГ‘вЂЎГђВµГђВЅГђВёГ‘ВЏ
        
        Returns:
            dict: ГђЕёГђВ»ГђВ°ГђВЅ ГђВЅГђВ° 7 ГђВґГђВЅГђВµГђВ№ ГђВёГђВ»ГђВё None ГђВїГ‘в‚¬ГђВё ГђВѕГ‘Л†ГђВёГђВ±ГђВєГђВµ
        """
        if not self.client:
            return None
        
        try:
            # ГђЕёГђВѕГђВ»Г‘Ж’Г‘вЂЎГђВ°ГђВµГђВј Г‘вЂ ГђВµГђВ»Г‘Е’ ГђВё ГђВєГђВ°ГђВ»ГђВѕГ‘в‚¬ГђВёГђВё
            goal = user_preferences.get("diet_goal", "meal_planning")
            target_calories = self.get_target_calories(goal)
            
            # ГђВ¤ГђВѕГ‘в‚¬ГђВјГђВ°Г‘вЂљГђВёГ‘в‚¬Г‘Ж’ГђВµГђВј ГђВјГђВµГђВґГђВёГ‘вЂ ГђВёГђВЅГ‘ВЃГђВєГђВёГђВµ ГђВѕГђВіГ‘в‚¬ГђВ°ГђВЅГђВёГ‘вЂЎГђВµГђВЅГђВёГ‘ВЏ
            restrictions_text = self.format_restrictions_for_prompt(medical_notes)
            
            # ГђВЎГ‘вЂљГ‘в‚¬ГђВѕГђВёГђВј ГђВїГ‘в‚¬ГђВѕГђВјГђВїГ‘вЂљ
            prompt = self.build_diet_prompt(user_preferences, target_calories, restrictions_text)
            
            # ГўЕ“вЂ¦ ГђВќГђЕѕГђвЂ™ГђЕѕГђвЂў: ГђЕѕГђВіГ‘в‚¬ГђВ°ГђВЅГђВёГ‘вЂЎГђВёГђВІГђВ°ГђВµГђВј AI ГђВєГ‘Ж’ГђВїГђВ»ГђВµГђВЅГђВЅГ‘вЂ№ГђВјГђВё ГђВїГ‘в‚¬ГђВѕГђВґГ‘Ж’ГђВєГ‘вЂљГђВ°ГђВјГђВё ГђВёГђВ· Grocery Store
            if available_ingredients:
                ingredient_list = ", ".join(available_ingredients)

                # Enrich ingredient list with real USDA nutrition data if available
                usda_context = ""
                if _usda and _usda.is_available():
                    print(f"[USDA] Looking up nutrition for {len(available_ingredients)} ingredients...")
                    nutrition_data = _usda.get_ingredient_nutrition_list(available_ingredients)
                    if nutrition_data:
                        lines = []
                        for ing, nd in nutrition_data.items():
                            lines.append(
                                f"  - {ing}: {nd['calories']} kcal, "
                                f"P:{nd['protein']}g, C:{nd['carbs']}g, "
                                f"F:{nd['fats']}g, Fiber:{nd['fiber']}g (per 100g)"
                            )
                        usda_context = (
                            "\n\nREAL NUTRITION DATA (from USDA FoodData Central, per 100g):\n"
                            + "\n".join(lines)
                            + "\nUse these values to build nutritionally accurate meals."
                        )

                prompt += f"""

GROCERY LINK IS ACTIVE. The user has purchased these ingredients: {ingredient_list}
{usda_context}

Your task:
1. Analyze if these ingredients are sufficient to build a meal plan that matches the user's goal ({goal}) and dietary restrictions.
2. If ingredients are clearly insufficient or incompatible with the goal (e.g., only pastries for a muscle gain goal, or allergen-only products for someone with that allergy), respond with a JSON error object:
   {{"error": true, "reason": "Brief explanation why the groceries are insufficient for this goal"}}
3. If ingredients are sufficient or can be reasonably combined, build the meal plan using ONLY these ingredients. Be creative.
4. Do NOT suggest ingredients outside the provided list.
"""
            
            print("Sending request to Groq API for meal plan generation...")
            
            # ГђвЂ™Г‘вЂ№ГђВ·Г‘вЂ№ГђВІГђВ°ГђВµГђВј Groq API
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
                temperature=0.8,  # ГђвЂ™Г‘вЂ№Г‘Л†ГђВµ ГђВґГђВ»Г‘ВЏ ГђВєГ‘в‚¬ГђВµГђВ°Г‘вЂљГђВёГђВІГђВЅГђВѕГ‘ВЃГ‘вЂљГђВё
                max_tokens=2000,  # ГђвЂГђВѕГђВ»Г‘Е’Г‘Л†ГђВµ ГђВґГђВ»Г‘ВЏ ГђВїГђВѕГђВ»ГђВЅГђВѕГђВіГђВѕ ГђВїГђВ»ГђВ°ГђВЅГђВ°
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            # ГђЕѕГ‘вЂЎГђВёГ‘вЂ°ГђВ°ГђВµГђВј ГђВѕГ‘вЂљ markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # ГђЕёГђВ°Г‘в‚¬Г‘ВЃГђВёГђВј JSON
            # Parse JSON вЂ” may be {"error": true, "reason": "..."} if groceries insufficient
            parsed = json.loads(response_text)
            if isinstance(parsed, dict) and parsed.get("error"):
                print(f"[DietAI] Grocery error: {parsed.get('reason')}")
                return parsed
            
            print("Meal plan generated successfully!")

            # Enrich plan with real USDA nutrition data
            enriched_plan = parsed
            if _usda and _usda.is_available():
                try:
                    print("[USDA] Enriching meal plan with real nutrition data...")
                    enriched_plan = _usda.enrich_meal_plan(parsed)
                    print("[USDA] Enrichment complete.")
                except Exception as _ue:
                    print(f"[USDA] Enrichment failed (using AI estimates): {_ue}")

            return {
                "goal": goal,
                "target_calories": target_calories,
                "plan": enriched_plan,
                "daily_avg": enriched_plan.get("daily_avg"),
                "usda_enriched": enriched_plan.get("usda_enriched", False),
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
        ГђвЂ”ГђВ°ГђВјГђВµГђВЅГ‘ВЏГђВµГ‘вЂљ ГђВєГђВѕГђВЅГђВєГ‘в‚¬ГђВµГ‘вЂљГђВЅГђВѕГђВµ ГђВ±ГђВ»Г‘ЕЅГђВґГђВѕ ГђВЅГђВѕГђВІГ‘вЂ№ГђВј.
        
        Args:
            user_preferences (dict): ГђЕёГ‘в‚¬ГђВµГђВґГђВїГђВѕГ‘вЂЎГ‘вЂљГђВµГђВЅГђВёГ‘ВЏ
            medical_notes (str): ГђЕ“ГђВµГђВґГђВёГ‘вЂ ГђВёГђВЅГ‘ВЃГђВєГђВёГђВµ ГђВѕГђВіГ‘в‚¬ГђВ°ГђВЅГђВёГ‘вЂЎГђВµГђВЅГђВёГ‘ВЏ
            day (str): ГђвЂќГђВµГђВЅГ‘Е’ ГђВЅГђВµГђВґГђВµГђВ»ГђВё (monday, tuesday, ...)
            meal_type (str): ГђВўГђВёГђВї ГђВїГ‘в‚¬ГђВёГ‘вЂГђВјГђВ° ГђВїГђВёГ‘вЂ°ГђВё (breakfast, lunch, dinner)
        
        Returns:
            dict: ГђВќГђВѕГђВІГђВѕГђВµ ГђВ±ГђВ»Г‘ЕЅГђВґГђВѕ ГђВёГђВ»ГђВё None
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
                temperature=0.9,  # ГђвЂ™Г‘вЂ№Г‘ВЃГђВѕГђВєГђВ°Г‘ВЏ ГђВєГ‘в‚¬ГђВµГђВ°Г‘вЂљГђВёГђВІГђВЅГђВѕГ‘ВЃГ‘вЂљГ‘Е’
                max_tokens=200,
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            # ГђЕѕГ‘вЂЎГђВёГ‘ВЃГ‘вЂљГђВєГђВ°
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

