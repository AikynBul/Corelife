import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def get_monday_of_week(date):
    """Р’РѕР·РІСЂР°С‰Р°РµС‚ РїРѕРЅРµРґРµР»СЊРЅРёРє С‚РµРєСѓС‰РµР№ РЅРµРґРµР»Рё"""
    return date - timedelta(days=date.weekday())


class EventStore:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.completions_collection = None
        self.user_id = None # Set when user logs in
        self._connect()

    CATEGORIES = {
        "Study": "📚",
        "Exercise": "💪",
        "Sleep": "😴",
        "Personal": "👤",
        "Work": "💼",
        "Social": "👥",
        "Health": "🏥",
        "Food": "🍽️"
    }

    OPTIMAL_TIMES = {
        "Study": {"start": 17, "end": 21},      # Р’РµС‡РµСЂ 17:00-21:00
        "Exercise": {"start": 14, "end": 18},   # РџРѕСЃР»Рµ РѕР±РµРґР° 14:00-18:00
        "Sleep": {"start": 22, "end": 7},       # РќРѕС‡СЊ 22:00-07:00
        "Food": {"start": 12, "end": 14},       # РћР±РµРґ 12:00-14:00
        "Work": {"start": 9, "end": 17},        # Р Р°Р±РѕС‡РёР№ РґРµРЅСЊ 9:00-17:00
        "Social": {"start": 18, "end": 22},     # Р’РµС‡РµСЂ 18:00-22:00
        "Personal": {"start": 8, "end": 22},    # Р“РёР±РєРѕРµ РІСЂРµРјСЏ
        "Health": {"start": 9, "end": 18}       # Р”РЅС‘Рј 9:00-18:00
    }

    def _connect(self):
        mongo_uri = os.getenv("MONGO_URI")
        if mongo_uri:
            try:
                self.client = MongoClient(mongo_uri)
                self.db = self.client.get_database("ai_calendar_db")
                self.collection = self.db.get_collection("events")
                self.completions_collection = self.db.get_collection("event_completions")
                print("Connected to MongoDB")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
        else:
            print("MONGO_URI not found in .env")

    def set_user(self, user_id):
        self.user_id = user_id

    def add_event(self, title, start_date, end_date, description, event_type="event",
                  recurrence=None, priority="Medium", completed=False, category="Personal"):
        if self.collection is None or not self.user_id:
            print("Database not connected or user not set")
            return None

        new_event = {
            "user_id": self.user_id,
            "title": title,
            "start": start_date,
            "end": end_date,
            "description": description,
            "type": event_type,
            "recurrence": recurrence,
            "priority": priority,
            "category": category,
            "completed": completed,
            "created_at": datetime.now()
        }
        try:
            result = self.collection.insert_one(new_event)
            new_event["id"] = str(result.inserted_id)
            return new_event
        except Exception as e:
            print(f"Error adding event: {e}")
            return None

    def update_event(self, event_id, updates):
        if self.collection is None or not self.user_id:
            return None
        
        from bson.objectid import ObjectId
        try:
            # Ensure we only update fields that are allowed and belong to the user
            result = self.collection.update_one(
                {"_id": ObjectId(event_id), "user_id": self.user_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating event: {e}")
            return False

    def delete_event(self, event_id):
        if self.collection is None or not self.user_id:
            return
        
        from bson.objectid import ObjectId
        try:
            self.collection.delete_one({"_id": ObjectId(event_id), "user_id": self.user_id})
        except Exception as e:
            print(f"Error deleting event: {e}")

    def get_events_for_month(self, year, month):
        if self.collection is None or not self.user_id:
            return []

        # Get all events for the user (filtering by date is complex with recurrence, so we fetch all and filter in python for now)
        # Optimization: In a real app, we would query for non-recurring events in range OR recurring events
        try:
            cursor = self.collection.find({"user_id": self.user_id})
            events = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                events.append(doc)
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
        
        results = []

        # Helper to get number of days in month
        import calendar
        _, num_days = calendar.monthrange(year, month)

        completion_map = {}
        if self.completions_collection is not None and self.user_id:
            try:
                month_start = f"{year}-{month:02d}-01"
                month_end = f"{year}-{month:02d}-{num_days:02d}"
                completions = self.completions_collection.find({
                    "user_id": self.user_id,
                    "date": {"$gte": month_start, "$lte": month_end}
                })
                completion_map = {
                    (c.get("parent_event_id"), c.get("date")): c.get("completed", False)
                    for c in completions
                }
            except Exception as e:
                print(f"Error fetching completion map: {e}")
                completion_map = {}
        
        for event in events:
            # Handle both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM"
            try:
                start_str = event["start"].split(" ")[0]
                start_dt = datetime.strptime(start_str, "%Y-%m-%d").date()
            except (ValueError, IndexError):
                continue

            recurrence = event.get("recurrence")
            
            # If non-recurring, check if it falls in this month
            if not recurrence or recurrence == "none":
                if start_dt.year == year and start_dt.month == month:
                    results.append(event)
                continue
                
            # Handle recurrence
            # We only care if the event started on or before this month (or if it repeats yearly in this month)
            
            # Optimization: If event starts after this month, skip
            if start_dt.year > year or (start_dt.year == year and start_dt.month > month):
                continue
                
            # Generate occurrences for this month
            for day in range(1, num_days + 1):
                current_date = datetime(year, month, day).date()
                
                # Skip if before start date
                if current_date < start_dt:
                    continue
                    
                should_add = False
                
                if recurrence == "daily":
                    should_add = True
                elif recurrence == "workdays":
                    # Mon=0, Sun=6
                    if current_date.weekday() < 5:
                        should_add = True
                elif recurrence == "weekends":
                    if current_date.weekday() >= 5:
                        should_add = True
                elif recurrence == "monthly":
                    if current_date.day == start_dt.day:
                        should_add = True
                elif recurrence == "yearly":
                    if current_date.month == start_dt.month and current_date.day == start_dt.day:
                        should_add = True
                        
                if should_add:
                    # Create a virtual event instance
                    instance = event.copy()
                    date_str = current_date.isoformat()
                    instance["start"] = date_str
                    instance["end"] = date_str
                    instance["completed"] = completion_map.get((event.get("id"), date_str), False)
                    results.append(instance)
                    
        return results

    def get_events_for_date(self, date):
        """РџРѕР»СѓС‡РёС‚СЊ РІСЃРµ СЃРѕР±С‹С‚РёСЏ РґР»СЏ РєРѕРЅРєСЂРµС‚РЅРѕР№ РґР°С‚С‹ (YYYY-MM-DD)"""
        if self.collection is None or not self.user_id:
            return []
        
        from datetime import datetime
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return []
        
        events = self.get_events_for_month(target_date.year, target_date.month)
        
        # Р¤РёР»СЊС‚СЂСѓРµРј С‚РѕР»СЊРєРѕ СЃРѕР±С‹С‚РёСЏ РЅР° СЌС‚Сѓ РґР°С‚Сѓ
        result = []
        for event in events:
            try:
                event_date_str = event["start"].split(" ")[0]
                event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
                if event_date == target_date:
                    result.append(event)
            except (ValueError, IndexError):
                continue
        
        return result
    
    def get_free_slots(self, date, duration_hours=1, category="Personal"):
        """
        РќР°Р№С‚Рё СЃРІРѕР±РѕРґРЅС‹Рµ СЃР»РѕС‚С‹ РІ СѓРєР°Р·Р°РЅРЅСѓСЋ РґР°С‚Сѓ
        
        Args:
            date: РґР°С‚Р° РІ С„РѕСЂРјР°С‚Рµ YYYY-MM-DD
            duration_hours: РїСЂРѕРґРѕР»Р¶РёС‚РµР»СЊРЅРѕСЃС‚СЊ РІ С‡Р°СЃР°С…
            category: РєР°С‚РµРіРѕСЂРёСЏ РґР»СЏ РѕРїСЂРµРґРµР»РµРЅРёСЏ РѕРїС‚РёРјР°Р»СЊРЅРѕРіРѕ РІСЂРµРјРµРЅРё
        
        Returns:
            list of dicts: [{"start": "HH:MM", "end": "HH:MM", "score": int}, ...]
        """
        from datetime import datetime, timedelta
        
        events = self.get_events_for_date(date)
        
        # РџРѕР»СѓС‡Р°РµРј РѕРїС‚РёРјР°Р»СЊРЅРѕРµ РІСЂРµРјСЏ РґР»СЏ РєР°С‚РµРіРѕСЂРёРё
        optimal = self.OPTIMAL_TIMES.get(category, {"start": 9, "end": 21})
        optimal_start = optimal["start"]
        optimal_end = optimal["end"]
        
        # РЎРѕР·РґР°РµРј СЃРїРёСЃРѕРє Р·Р°РЅСЏС‚С‹С… С‡Р°СЃРѕРІ
        busy_slots = []
        for event in events:
            try:
                time_part = event["start"].split(" ")[1] if " " in event["start"] else "09:00"
                hour = int(time_part.split(":")[0])
                busy_slots.append(hour)
            except (ValueError, IndexError):
                continue
        
        # РќР°С…РѕРґРёРј СЃРІРѕР±РѕРґРЅС‹Рµ СЃР»РѕС‚С‹ РІ РѕРїС‚РёРјР°Р»СЊРЅРѕРµ РІСЂРµРјСЏ
        free_slots = []
        
        # Р”Р»СЏ СЃРЅР° РѕСЃРѕР±Р°СЏ Р»РѕРіРёРєР° (РЅРѕС‡РЅРѕРµ РІСЂРµРјСЏ)
        if category == "Sleep":
            for hour in range(22, 24):
                if hour not in busy_slots:
                    score = 100
                    free_slots.append({
                        "start": f"{hour:02d}:00",
                        "end": f"{(hour + duration_hours) % 24:02d}:00",
                        "score": score
                    })
        else:
            # РћР±С‹С‡РЅР°СЏ Р»РѕРіРёРєР° РґР»СЏ РѕСЃС‚Р°Р»СЊРЅС‹С… РєР°С‚РµРіРѕСЂРёР№
            for hour in range(optimal_start, optimal_end):
                if hour not in busy_slots and hour + duration_hours <= optimal_end:
                    mid_time = (optimal_start + optimal_end) / 2
                    distance_from_optimal = abs(hour - mid_time)
                    score = 100 - int(distance_from_optimal * 10)
                    
                    free_slots.append({
                        "start": f"{hour:02d}:00",
                        "end": f"{hour + duration_hours:02d}:00",
                        "score": max(score, 1)
                    })
        
        # Р•СЃР»Рё РЅРµС‚ СЃР»РѕС‚РѕРІ РІ РѕРїС‚РёРјР°Р»СЊРЅРѕРµ РІСЂРµРјСЏ, РёС‰РµРј РІ Р»СЋР±РѕРµ РІСЂРµРјСЏ (8:00 - 22:00)
        if not free_slots:
            for hour in range(8, 22):
                if hour not in busy_slots:
                    free_slots.append({
                        "start": f"{hour:02d}:00",
                        "end": f"{hour + duration_hours:02d}:00",
                        "score": 30
                    })
        
        free_slots.sort(key=lambda x: x["score"], reverse=True)
        return free_slots

    def save_diet_preferences(self, user_id, preferences):
        """РЎРѕС…СЂР°РЅСЏРµС‚ РїСЂРµРґРїРѕС‡С‚РµРЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РїРѕ РґРёРµС‚Рµ"""
        try:
            # вњ… РРЎРџР РђР’Р›Р•РќРћ: РљРѕРЅРІРµСЂС‚РёСЂСѓРµРј РІСЃРµ СЃРїРёСЃРєРё РІ СЃС‚СЂРѕРєРё РґР»СЏ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё СЃ MongoDB
            # MongoDB РјРѕР¶РµС‚ С…СЂР°РЅРёС‚СЊ СЃРїРёСЃРєРё, РЅРѕ РёРЅРѕРіРґР° РІРѕР·РЅРёРєР°СЋС‚ РїСЂРѕР±Р»РµРјС‹ СЃ С…РµС€РёСЂРѕРІР°РЅРёРµРј
            
            # РЎРѕР·РґР°С‘Рј РєРѕРїРёСЋ С‡С‚РѕР±С‹ РЅРµ РёР·РјРµРЅСЏС‚СЊ РѕСЂРёРіРёРЅР°Р»СЊРЅС‹Р№ СЃР»РѕРІР°СЂСЊ
            safe_preferences = {}
            
            for key, value in preferences.items():
                # Р•СЃР»Рё Р·РЅР°С‡РµРЅРёРµ - СЃРїРёСЃРѕРє, СЃРѕС…СЂР°РЅСЏРµРј РєР°Рє РµСЃС‚СЊ (MongoDB РїРѕРґРґРµСЂР¶РёРІР°РµС‚ РјР°СЃСЃРёРІС‹)
                # РќРѕ СѓР±РµР¶РґР°РµРјСЃСЏ С‡С‚Рѕ СЌС‚Рѕ РїСЂРѕСЃС‚С‹Рµ С‚РёРїС‹ РґР°РЅРЅС‹С…
                if isinstance(value, list):
                    # РљРѕРЅРІРµСЂС‚РёСЂСѓРµРј РІСЃРµ СЌР»РµРјРµРЅС‚С‹ СЃРїРёСЃРєР° РІ СЃС‚СЂРѕРєРё
                    safe_preferences[key] = [str(item) for item in value]
                else:
                    safe_preferences[key] = str(value)
            
            self.db.users.update_one(
                {"_id": user_id},
                {"$set": {"diet_preferences": safe_preferences}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving diet preferences: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_diet_preferences(self, user_id):
        """РџРѕР»СѓС‡Р°РµС‚ РїСЂРµРґРїРѕС‡С‚РµРЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РїРѕ РґРёРµС‚Рµ"""
        try:
            user = self.db.users.find_one({"_id": user_id})
            if user and "diet_preferences" in user:
                return user["diet_preferences"]
            return None
        except Exception as e:
            print(f"Error getting diet preferences: {e}")
            return None

    def save_user_goals(self, user_id, goals):
        """РЎРѕС…СЂР°РЅСЏРµС‚ С†РµР»Рё РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ (time_management, diet)"""
        try:
            self.db.users.update_one(
                {"_id": user_id},
                {"$set": {
                    "goals": goals,
                    "onboarding_completed": True
                }},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving user goals: {e}")
            return False

    def get_user_goals(self, user_id):
        """РџРѕР»СѓС‡Р°РµС‚ С†РµР»Рё РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""
        try:
            user = self.db.users.find_one({"_id": user_id})
            if user and "goals" in user:
                return user["goals"]
            return []
        except Exception as e:
            print(f"Error getting user goals: {e}")
            return []

    def has_completed_onboarding(self, user_id):
        """РџСЂРѕРІРµСЂСЏРµС‚ РїСЂРѕС€С‘Р» Р»Рё РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ РѕРЅР±РѕСЂРґРёРЅРі"""
        try:
            user = self.db.users.find_one({"_id": user_id})
            if user:
                return user.get("onboarding_completed", False)
            return False
        except Exception as e:
            print(f"Error checking onboarding: {e}")
            return False
    def save_weekly_meal_plan(self, user_id, meal_plan_data):
        """
        РЎРѕС…СЂР°РЅСЏРµС‚ РїР»Р°РЅ РїРёС‚Р°РЅРёСЏ РЅР° РЅРµРґРµР»СЋ.
        
        Args:
            user_id (str): ID РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
            meal_plan_data (dict): РџР»Р°РЅ СЃ РєР»СЋС‡Р°РјРё goal, target_calories, plan, created_at
        
        Returns:
            bool: True РµСЃР»Рё СѓСЃРїРµС€РЅРѕ
        """
        try:
            # Р”РѕР±Р°РІР»СЏРµРј user_id
            meal_plan_data["user_id"] = user_id
            
            # РЎРѕС…СЂР°РЅСЏРµРј РёР»Рё РѕР±РЅРѕРІР»СЏРµРј
            self.db.meal_plans.update_one(
                {"user_id": user_id},
                {"$set": meal_plan_data},
                upsert=True
            )
            
            print(f"вњ… Meal plan saved for user {user_id}")
            return True
            
        except Exception as e:
            print(f"Error saving meal plan: {e}")
            return False

    def get_weekly_meal_plan(self, user_id):
        """
        РџРѕР»СѓС‡Р°РµС‚ СЃРѕС…СЂР°РЅС‘РЅРЅС‹Р№ РїР»Р°РЅ РїРёС‚Р°РЅРёСЏ.
        
        Args:
            user_id (str): ID РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
        
        Returns:
            dict: РџР»Р°РЅ РїРёС‚Р°РЅРёСЏ РёР»Рё None
        """
        try:
            plan = self.db.meal_plans.find_one({"user_id": user_id})
            
            if plan:
                # РЈРґР°Р»СЏРµРј _id РґР»СЏ СѓРґРѕР±СЃС‚РІР°
                plan.pop("_id", None)
                return plan
            
            return None
            
        except Exception as e:
            print(f"Error getting meal plan: {e}")
            return None

    def replace_meal_in_plan(self, user_id, day, meal_type, new_meal):
        """
        Р—Р°РјРµРЅСЏРµС‚ РєРѕРЅРєСЂРµС‚РЅРѕРµ Р±Р»СЋРґРѕ РІ РїР»Р°РЅРµ.
        
        Args:
            user_id (str): ID РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
            day (str): Р”РµРЅСЊ РЅРµРґРµР»Рё (monday, tuesday, ...)
            meal_type (str): РўРёРї РїСЂРёС‘РјР° РїРёС‰Рё (breakfast, lunch, dinner, snack)
            new_meal (dict): РќРѕРІРѕРµ Р±Р»СЋРґРѕ СЃ РєР»СЋС‡Р°РјРё name, calories, protein, carbs, fats
        
        Returns:
            bool: True РµСЃР»Рё СѓСЃРїРµС€РЅРѕ
        """
        try:
            # РћР±РЅРѕРІР»СЏРµРј РєРѕРЅРєСЂРµС‚РЅРѕРµ Р±Р»СЋРґРѕ
            update_path = f"plan.{day}.{meal_type}"
            
            result = self.db.meal_plans.update_one(
                {"user_id": user_id},
                {"$set": {update_path: new_meal}}
            )
            
            if result.modified_count > 0:
                print(f"вњ… Replaced {day}'s {meal_type}")
                return True
            else:
                print(f"вљ пёЏ No meal plan found to update")
                return False
            
        except Exception as e:
            print(f"Error replacing meal: {e}")
            return False

    def delete_meal_plan(self, user_id):
        """
        РЈРґР°Р»СЏРµС‚ РїР»Р°РЅ РїРёС‚Р°РЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ.
        
        Args:
            user_id (str): ID РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
        
        Returns:
            bool: True РµСЃР»Рё СѓСЃРїРµС€РЅРѕ
        """
        try:
            result = self.db.meal_plans.delete_one({"user_id": user_id})
            
            if result.deleted_count > 0:
                print(f"вњ… Meal plan deleted for user {user_id}")
                return True
            else:
                print(f"вљ пёЏ No meal plan found to delete")
                return False
            
        except Exception as e:
            print(f"Error deleting meal plan: {e}")
            return False
            
    # ============= GROCERY STORE METHODS =============

    def set_user_budget(self, user_id, budget):
        """РЈСЃС‚Р°РЅРѕРІРёС‚СЊ РЅРµРґРµР»СЊРЅС‹Р№ Р±СЋРґР¶РµС‚ РЅР° РїСЂРѕРґСѓРєС‚С‹"""
        if self.db is None:
            return False
        
        week_start = get_monday_of_week(datetime.now().date())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        try:
            self.db.grocery_budgets.update_one(
                {"user_id": user_id, "week_start": week_start_str},
                {"$set": {
                    "user_id": user_id,
                    "week_start": week_start_str,
                    "weekly_budget": budget,
                    "spent": 0,
                    "remaining": budget,
                    "subtotal": 0,
                    "cart": [],
                    "purchased": False,
                    "purchased_at": None,
                    "created_at": datetime.now()
                }},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error setting budget: {e}")
            return False

    def get_user_groceries(self, user_id):
        """РџРѕР»СѓС‡РёС‚СЊ РґР°РЅРЅС‹Рµ Рѕ РїСЂРѕРґСѓРєС‚Р°С… С‚РµРєСѓС‰РµР№ РЅРµРґРµР»Рё"""
        if self.db is None:
            return None
        
        week_start = get_monday_of_week(datetime.now().date())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        return self.db.grocery_budgets.find_one({
            "user_id": user_id,
            "week_start": week_start_str
        })

    def update_cart(self, user_id, cart):
        """РћР±РЅРѕРІРёС‚СЊ РєРѕСЂР·РёРЅСѓ РїРѕРєСѓРїРѕРє"""
        if self.db is None:
            return False
        
        week_start = get_monday_of_week(datetime.now().date())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        # Р Р°СЃСЃС‡РёС‚С‹РІР°РµРј subtotal
        subtotal = sum(item.get("total", 0) for item in cart)
        
        try:
            self.db.grocery_budgets.update_one(
                {"user_id": user_id, "week_start": week_start_str},
                {"$set": {
                    "cart": cart,
                    "subtotal": subtotal
                }}
            )
            return True
        except Exception as e:
            print(f"Error updating cart: {e}")
            return False

    def confirm_purchase(self, user_id):
        """РџРѕРґС‚РІРµСЂРґРёС‚СЊ РїРѕРєСѓРїРєСѓ.
        РЎРѕС…СЂР°РЅСЏРµС‚ cart -> purchased_cart, РѕС‡РёС‰Р°РµС‚ cart/subtotal, РЅР°РєР°РїР»РёРІР°РµС‚ spent."""
        if self.db is None:
            return False
        grocery = self.get_user_groceries(user_id)
        if not grocery:
            return False
        subtotal = grocery.get("subtotal", 0)
        budget = grocery.get("weekly_budget", 0)
        prev_spent = grocery.get("spent", 0)
        current_cart = grocery.get("cart", [])
        existing_purchased = grocery.get("purchased_cart", [])
        merged_purchased = existing_purchased + current_cart
        new_spent = prev_spent + subtotal
        new_remaining = budget - new_spent
        try:
            update_doc = {"$set": {
                "spent": new_spent,
                "remaining": new_remaining,
                "purchased": True,
                "purchased_at": datetime.now(),
                "purchased_cart": merged_purchased,
                "cart": [],
                "subtotal": 0,
            }}
            self.db.grocery_budgets.update_one({"_id": grocery["_id"]}, update_doc)
            print(f"[Store] Purchase OK. subtotal={subtotal}, new_spent={new_spent}, items={len(current_cart)}")
            return True
        except Exception as e:
            print(f"Error confirming purchase: {e}")
            return False

    def get_week_range(self):
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ РґРёР°РїР°Р·РѕРЅ С‚РµРєСѓС‰РµР№ РЅРµРґРµР»Рё (Monday-Sunday)"""
        today = datetime.now().date()
        monday = get_monday_of_week(today)
        sunday = monday + timedelta(days=6)
        
        # Р¤РѕСЂРјР°С‚РёСЂСѓРµРј: "Feb 10-16"
        if monday.month == sunday.month:
            return f"{monday.strftime('%b %d')}-{sunday.day}"
        else:
            return f"{monday.strftime('%b %d')}-{sunday.strftime('%b %d')}"
    
    def initialize_starter_inventory(self, user_id):
        """Р”Р°С‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ СЃС‚Р°СЂС‚РѕРІС‹Р№ РёРЅРІРµРЅС‚Р°СЂСЊ Р’РЎР•РҐ РїСЂРѕРґСѓРєС‚РѕРІ"""
        from data.products import PRODUCTS
        
        if self.db is None:
            return False
        
        week_start = get_monday_of_week(datetime.now().date())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        # РЎРѕР±РёСЂР°РµРј Р’РЎР• РїСЂРѕРґСѓРєС‚С‹
        starter_items = []
        
        for category, products in PRODUCTS.items():
            for product in products:
                # Р”Р°С‘Рј РїРѕ 10 РµРґРёРЅРёС† РєР°Р¶РґРѕРіРѕ РїСЂРѕРґСѓРєС‚Р°
                starter_items.append({
                    "product_id": product["id"],
                    "name": product["name"],
                    "quantity": 10,
                    "unit": product["unit"],
                    "price_per_unit": 0,
                    "total": 0,
                })
        
        total_spent = sum(item["total"] for item in starter_items)
        
        try:
            self.db.grocery_budgets.update_one(
                {"user_id": user_id, "week_start": week_start_str},
                {"$set": {
                    "user_id": user_id,
                    "week_start": week_start_str,
                    "weekly_budget": 99999999,
                    "spent": total_spent,
                    "remaining": 99999999,
                    "subtotal": 0,
                    "cart": starter_items,
                    "purchased": True,
                    "purchased_at": datetime.now(),
                    "created_at": datetime.now()
                }},
                upsert=True
            )
            print(f"вњ… Starter inventory created: {len(starter_items)} items")
            return True
        except Exception as e:
            print(f"Error creating starter inventory: {e}")
            return False
    
    def update_purchased_items(self, user_id, cart_items, spent):
        """РћР±РЅРѕРІРёС‚СЊ purchased_cart РїРѕСЃР»Рµ СѓРґР°Р»РµРЅРёСЏ С‚РѕРІР°СЂР° РёР· РєСѓРїР»РµРЅРЅС‹С…."""
        if self.db is None:
            return False
        week_start = get_monday_of_week(datetime.now().date())
        week_start_str = week_start.strftime("%Y-%m-%d")
        try:
            update_doc = {"$set": {"purchased_cart": cart_items, "spent": spent}}
            self.db.grocery_budgets.update_one(
                {"user_id": user_id, "week_start": week_start_str}, update_doc
            )
            return True
        except Exception as e:
            print(f"Error updating purchased items: {e}")
            return False

    def delete_account(self, user_id):
        """РџРѕР»РЅРѕСЃС‚СЊСЋ СѓРґР°Р»РёС‚СЊ Р°РєРєР°СѓРЅС‚ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ Рё РІСЃРµ РµРіРѕ РґР°РЅРЅС‹Рµ."""
        if self.db is None:
            return False, "Database not connected"
        try:
            # РЈРґР°Р»СЏРµРј СЃРѕР±С‹С‚РёСЏ
            self.db.events.delete_many({"user_id": user_id})
            # РЈРґР°Р»СЏРµРј РїР»Р°РЅС‹ РїРёС‚Р°РЅРёСЏ
            self.db.meal_plans.delete_many({"user_id": user_id})
            # РЈРґР°Р»СЏРµРј РґР°РЅРЅС‹Рµ РїСЂРѕРґСѓРєС‚РѕРІРѕРіРѕ РјР°РіР°Р·РёРЅР°
            self.db.grocery_budgets.delete_many({"user_id": user_id})
            # РЈРґР°Р»СЏРµРј СЃР°РјРѕРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
            result = self.db.users.delete_one({"_id": user_id})
            if result.deleted_count > 0:
                self.user_id = None
                print(f"[Store] Account deleted: {user_id}")
                return True, "Account deleted successfully"
            else:
                return False, "User not found"
        except Exception as e:
            print(f"Error deleting account: {e}")
            return False, str(e)

    def update_username(self, user_id, new_name):
        """РћР±РЅРѕРІРёС‚СЊ РёРјСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
        if self.db is None:
            return False, "Database not connected"
        try:
            update_doc = {"$set": {"name": new_name}}
            result = self.db.users.update_one({"_id": user_id}, update_doc)
            if result.modified_count > 0:
                return True, "Name updated"
            return False, "No changes made"
        except Exception as e:
            print(f"Error updating username: {e}")
            return False, str(e)


    def save_avatar_url(self, user_id, avatar_url: str):
        """РЎРѕС…СЂР°РЅРёС‚СЊ base64 Р°РІР°С‚Р°СЂРєРё РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
        if self.db is None:
            return False, "Database not connected"
        try:
            from bson.objectid import ObjectId
            oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
            self.db.users.update_one(
                {"_id": oid},
                {"$set": {"avatar_url": avatar_url}}
            )
            return True, "Avatar saved"
        except Exception as e:
            print(f"Error saving avatar: {e}")
            return False, str(e)

    def get_avatar_url(self, user_id=None) -> str:
        """РџРѕР»СѓС‡РёС‚СЊ base64 Р°РІР°С‚Р°СЂРєРё РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
        if self.db is None:
            return ""
        uid = user_id or self.user_id
        if not uid:
            return ""
        try:
            from bson.objectid import ObjectId
            oid = ObjectId(uid) if isinstance(uid, str) else uid
            user = self.db.users.find_one({"_id": oid})
            if user:
                return user.get("avatar_url", "")
            return ""
        except Exception as e:
            print(f"Error getting avatar: {e}")
            return ""

    def change_password(self, user_id, current_password, new_password):
        """РЎРјРµРЅРёС‚СЊ РїР°СЂРѕР»СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ."""
        if self.db is None:
            return False, "Database not connected"
        try:
            import hashlib
            user = self.db.users.find_one({"_id": user_id})
            if not user:
                return False, "User not found"
            # РџСЂРѕРІРµСЂСЏРµРј С‚РµРєСѓС‰РёР№ РїР°СЂРѕР»СЊ
            hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
            if user.get("password") != hashed_current:
                return False, "Current password is incorrect"
            # РЈСЃС‚Р°РЅР°РІР»РёРІР°РµРј РЅРѕРІС‹Р№
            hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
            update_doc = {"$set": {"password": hashed_new}}
            self.db.users.update_one({"_id": user_id}, update_doc)
            return True, "Password changed successfully"
        except Exception as e:
            print(f"Error changing password: {e}")
            return False, str(e)


    def mark_recurring_completion(self, parent_event_id, date_str, completed):
        """Mark a specific recurrence of a repeating event as completed."""
        if self.completions_collection is None or not self.user_id:
            return False
        if not parent_event_id or not date_str:
            return False
        try:
            update_doc = {
                "$set": {
                    "parent_event_id": parent_event_id,
                    "date": date_str,
                    "completed": completed,
                    "user_id": self.user_id,
                    "updated_at": datetime.now(),
                }
            }
            self.completions_collection.update_one(
                {"parent_event_id": parent_event_id, "date": date_str, "user_id": self.user_id},
                update_doc,
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error marking recurring completion: {e}")
            return False

    def get_recurring_completion(self, parent_event_id, date_str):
        """Get completion status for a specific recurrence."""
        if self.completions_collection is None or not self.user_id:
            return None
        if not parent_event_id or not date_str:
            return None
        try:
            doc = self.completions_collection.find_one(
                {"parent_event_id": parent_event_id, "date": date_str, "user_id": self.user_id}
            )
            return doc.get("completed") if doc else None
        except Exception as e:
            print(f"Error getting recurring completion: {e}")
            return None
    def mark_event_completed(self, event_id, completed: bool):
        """РћС‚РјРµС‚РёС‚СЊ СЃРѕР±С‹С‚РёРµ/Р·Р°РґР°С‡Сѓ РєР°Рє РІС‹РїРѕР»РЅРµРЅРЅРѕРµ РёР»Рё РЅРµС‚."""
        if self.collection is None or not self.user_id:
            return False
        try:
            from bson import ObjectId
            update_doc = {"$set": {"completed": completed}}
            self.collection.update_one(
                {"_id": ObjectId(event_id), "user_id": self.user_id},
                update_doc
            )
            return True
        except Exception as e:
            print(f"Error marking event completed: {e}")
            return False


    # ============= CREDITS SYSTEM =============

    def ensure_starter_credits(self, user_id):
        """Р’С‹РґР°С‚СЊ 500 СЃС‚Р°СЂС‚РѕРІС‹С… РєСЂРµРґРёС‚РѕРІ РЅРѕРІРѕРјСѓ РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ.
        Р§РёС‚Р°РµРј С‚РµРєСѓС‰РёР№ Р±Р°Р»Р°РЅСЃ РЅР°РїСЂСЏРјСѓСЋ вЂ” РµСЃР»Рё 0 РёР»Рё РїРѕР»СЏ РЅРµС‚, РїСЂРёРЅСѓРґРёС‚РµР»СЊРЅРѕ СЃС‚Р°РІРёРј 500.
        """
        if self.db is None:
            return
        try:
            current = self.get_credits(user_id)
            if current > 0:
                print(f"[Credits] User {user_id} has {current} cr, no top-up needed")
                return

            # Balance is 0 or missing вЂ” set 500 unconditionally
            self.db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {"credits": 500},
                    "$push": {
                        "credits_history": {
                            "amount": 500,
                            "reason": "Welcome bonus",
                            "type": "bonus",
                            "created_at": datetime.now()
                        }
                    }
                },
                upsert=True
            )
            print(f"[Credits] User {user_id} received 500 starter credits")
        except Exception as e:
            print(f"Error in ensure_starter_credits: {e}")

    def get_credits(self, user_id):
        """РџРѕР»СѓС‡РёС‚СЊ С‚РµРєСѓС‰РёР№ Р±Р°Р»Р°РЅСЃ РєСЂРµРґРёС‚РѕРІ."""
        if self.db is None:
            return 0
        try:
            user = self.db.users.find_one({"_id": user_id})
            return user.get("credits", 0) if user else 0
        except Exception as e:
            print(f"Error getting credits: {e}")
            return 0

    def spend_credits(self, user_id, amount, reason=""):
        """Spend credits. Admin accounts have effectively unlimited credits."""
        if self.db is None:
            return False, 0
        try:
            if self.is_admin_account(user_id):
                current = self.get_credits(user_id)
                print(f"[Admin] credits not spent (amount: {amount})")
                return True, current

            balance = self.get_credits(user_id)
            if balance < amount:
                print(f"[Credits] Not enough: have {balance}, need {amount}")
                return False, balance
            update_doc = {
                "$inc": {"credits": -amount},
                "$push": {
                    "credits_history": {
                        "amount": -amount,
                        "reason": reason,
                        "type": "spend",
                        "created_at": datetime.now()
                    }
                }
            }
            self.db.users.update_one({"_id": user_id}, update_doc)
            new_balance = balance - amount
            print(f"[Credits] -{amount} ({reason}) | balance: {new_balance}")
            return True, new_balance
        except Exception as e:
            print(f"Error spending credits: {e}")
            return False, 0

    def update_grocery_budget(self, user_id: str, amount: int) -> bool:
        """Update grocery budget. Admin accounts have effectively unlimited budget."""
        if self.db is None:
            return False
        try:
            if self.is_admin_account(user_id):
                print(f"[Admin] budget not spent (amount: {amount})")
                return True

            user = self.db.users.find_one({"_id": user_id})
            if not user:
                return False

            current_budget = user.get("grocery_budget", 0)
            new_budget = current_budget + amount
            if new_budget < 0:
                print(f"[Budget] Not enough. Have: {current_budget}, Need: {abs(amount)}")
                return False

            self.db.users.update_one({"_id": user_id}, {"$set": {"grocery_budget": new_budget}})
            print(f"[Budget] Updated. New balance: {new_budget}")
            return True
        except Exception as e:
            print(f"Error updating budget: {e}")
            return False
    def add_credits(self, user_id, amount, reason=""):
        """РќР°С‡РёСЃР»РёС‚СЊ РєСЂРµРґРёС‚С‹ РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ."""
        if self.db is None:
            return False
        try:
            update_doc = {
                "$inc": {"credits": amount},
                "$push": {
                    "credits_history": {
                        "amount": amount,
                        "reason": reason,
                        "type": "earn",
                        "created_at": datetime.now()
                    }
                }
            }
            self.db.users.update_one({"_id": user_id}, update_doc)
            return True
        except Exception as e:
            print(f"Error adding credits: {e}")
            return False

    def get_credits_history(self, user_id, limit=15):
        """РСЃС‚РѕСЂРёСЏ РѕРїРµСЂР°С†РёР№ СЃ РєСЂРµРґРёС‚Р°РјРё."""
        if self.db is None:
            return []
        try:
            user = self.db.users.find_one({"_id": user_id})
            if user:
                history = user.get("credits_history", [])
                return list(reversed(history[-limit:]))
            return []
        except Exception as e:
            print(f"Error getting credits history: {e}")
            return []
        
    def grant_admin_privileges(self, user_id: str):
        """Grant admin privileges and unlimited resources."""
        if self.db is None:
            return False
        try:
            self.db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "is_admin": True,
                        "admin_activated_at": datetime.now().isoformat(),
                        "can_view_reports": True,
                        "can_view_ratings": True,
                        "credits": 999999999,
                        "grocery_budget": 999999999,
                    }
                },
                upsert=True
            )
            print(f"[Admin] privileges granted to user {user_id}")
            print("[Admin] Credits: 999,999,999")
            print("[Admin] Budget: 999,999,999")
            return True
        except Exception as e:
            print(f"Error granting admin privileges: {e}")
            return False
    def is_admin_account(self, user_id: str) -> bool:
        """Check if user has admin role."""
        if self.db is None or not user_id:
            return False
        try:
            user = self.db.users.find_one({"_id": user_id})
            return bool(user and user.get("is_admin", False))
        except Exception as e:
            print(f"Error checking admin account: {e}")
            return False

    def save_user_rating(self, user_id: str, rating: float, comment: str = ""):
        """Persist user app rating (supports 0.5 increments)."""
        if self.db is None:
            return False
        try:
            value = float(rating)
            if value < 0.5 or value > 5:
                return False
            # allow only 0.5 steps: 0.5, 1.0, 1.5 ... 5.0
            if int(value * 2) != value * 2:
                return False

            rating_data = {
                "user_id": user_id,
                "rating": value,
                "comment": comment or "",
                "created_at": datetime.now().isoformat(),
                "status": "new",
            }
            self.db.ratings.insert_one(rating_data)
            print(f"[Admin] Rating {value}/5 saved from user {user_id}")
            return True
        except Exception as e:
            print(f"Error saving rating: {e}")
            return False
    def save_bug_report(self, user_id: str, bug_type: str, description: str):
        """Persist bug report from user."""
        if self.db is None:
            return False
        try:
            report_data = {
                "user_id": user_id,
                "bug_type": bug_type,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "status": "new",  # new, in_progress, resolved, closed
                "priority": "medium",  # low, medium, high, critical
            }
            self.db.bug_reports.insert_one(report_data)
            print(f"[Admin] Bug report saved from user {user_id}")
            return True
        except Exception as e:
            print(f"Error saving bug report: {e}")
            return False

    def get_all_ratings(self, status: str = None, limit: int = 100):
        """Get ratings list for admin dashboard."""
        if self.db is None:
            return []
        try:
            query = {}
            if status:
                query["status"] = status
            ratings = list(self.db.ratings.find(query).sort("created_at", -1).limit(limit))
            for rating in ratings:
                rating["id"] = str(rating.pop("_id"))
            return ratings
        except Exception as e:
            print(f"Error getting ratings: {e}")
            return []

    def get_all_bug_reports(self, status: str = None, limit: int = 100):
        """Get bug reports list for admin dashboard."""
        if self.db is None:
            return []
        try:
            query = {}
            if status:
                query["status"] = status
            reports = list(self.db.bug_reports.find(query).sort("created_at", -1).limit(limit))
            for report in reports:
                report["id"] = str(report.pop("_id"))
            return reports
        except Exception as e:
            print(f"Error getting bug reports: {e}")
            return []

    def update_report_status(self, report_id: str, new_status: str):
        """Update bug report status by id."""
        if self.db is None:
            return False
        try:
            from bson.objectid import ObjectId

            self.db.bug_reports.update_one(
                {"_id": ObjectId(report_id)},
                {"$set": {"status": new_status}}
            )
            return True
        except Exception as e:
            print(f"Error updating report status: {e}")
            return False

    def delete_user_completely(self, user_id: str):
        """
        вњ… РРЎРџР РђР’Р›Р•РќРћ: РџРѕР»РЅРѕСЃС‚СЊСЋ СѓРґР°Р»СЏРµС‚ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РёР· РІСЃРµС… РєРѕР»Р»РµРєС†РёР№
        РўРµРїРµСЂСЊ РЅРёРєРЅРµР№Рј РѕСЃРІРѕР±РѕР¶РґР°РµС‚СЃСЏ РґР»СЏ РїРѕРІС‚РѕСЂРЅРѕРіРѕ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ
        
        Args:
            user_id: ID РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РґР»СЏ СѓРґР°Р»РµРЅРёСЏ
        """
        try:
            from bson.objectid import ObjectId
            
            # 1. РЈРґР°Р»СЏРµРј РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РёР· users
            result = self.db.users.delete_one({"_id": user_id})
            print(f"вњ… Deleted user from users collection: {result.deleted_count}")
            
            # 2. РЈРґР°Р»СЏРµРј РІСЃРµ СЃРѕР±С‹С‚РёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
            events_result = self.db.events.delete_many({"user_id": user_id})
            print(f"вњ… Deleted {events_result.deleted_count} events")
            
            # 3. РЈРґР°Р»СЏРµРј РїСЂРµРґРїРѕС‡С‚РµРЅРёСЏ РґРёРµС‚С‹
            diet_result = self.db.diet_preferences.delete_many({"user_id": user_id})
            print(f"вњ… Deleted {diet_result.deleted_count} diet preferences")
            
            # 4. РЈРґР°Р»СЏРµРј РёСЃС‚РѕСЂРёСЋ РїРѕРєСѓРїРѕРє РІ РјР°РіР°Р·РёРЅРµ (РµСЃР»Рё РµСЃС‚СЊ)
            if "grocery_purchases" in self.db.list_collection_names():
                grocery_result = self.db.grocery_purchases.delete_many({"user_id": user_id})
                print(f"вњ… Deleted {grocery_result.deleted_count} grocery purchases")
            
            # 5. РЈРґР°Р»СЏРµРј РёСЃС‚РѕСЂРёСЋ С‚СЂР°РЅР·Р°РєС†РёР№ РєСЂРµРґРёС‚РѕРІ (РµСЃР»Рё РµСЃС‚СЊ)
            if "credit_transactions" in self.db.list_collection_names():
                credit_result = self.db.credit_transactions.delete_many({"user_id": user_id})
                print(f"вњ… Deleted {credit_result.deleted_count} credit transactions")
            
            print(f"рџ—‘пёЏ User {user_id} completely deleted - username is now available")
            return True
            
        except Exception as e:
            print(f"вќЊ Error deleting user: {e}")
            return False

    def check_username_available(self, username: str, exclude_user_id: str = None) -> bool:
        """
        вњ… РРЎРџР РђР’Р›Р•РќРћ: РџСЂРѕРІРµСЂСЏРµС‚ РґРѕСЃС‚СѓРїРЅРѕСЃС‚СЊ РЅРёРєРЅРµР№РјР° (СѓС‡РёС‚С‹РІР°СЏ СѓРґР°Р»С‘РЅРЅС‹С… РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№)
        
        Args:
            username: РќРёРєРЅРµР№Рј РґР»СЏ РїСЂРѕРІРµСЂРєРё
            exclude_user_id: ID РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РєРѕС‚РѕСЂРѕРіРѕ РЅСѓР¶РЅРѕ РёСЃРєР»СЋС‡РёС‚СЊ РёР· РїСЂРѕРІРµСЂРєРё (РґР»СЏ СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ)
            
        Returns:
            bool - True РµСЃР»Рё РЅРёРєРЅРµР№Рј РґРѕСЃС‚СѓРїРµРЅ
        """
        try:
            query = {"username": username}
            
            # РСЃРєР»СЋС‡Р°РµРј С‚РµРєСѓС‰РµРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РїСЂРё СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёРё РїСЂРѕС„РёР»СЏ
            if exclude_user_id:
                query["_id"] = {"$ne": exclude_user_id}
            
            existing_user = self.db.users.find_one(query)
            
            if existing_user:
                print(f"вќЊ Username '{username}' is already taken")
                return False
            else:
                print(f"вњ… Username '{username}' is available")
                return True
                
        except Exception as e:
            print(f"вќЊ Error checking username: {e}")
            return False


# Global instance
store = EventStore()

