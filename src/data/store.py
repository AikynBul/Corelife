import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def get_monday_of_week(date):
    """Возвращает понедельник текущей недели"""
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
        "Study": {"start": 17, "end": 21},      # Вечер 17:00-21:00
        "Exercise": {"start": 14, "end": 18},   # После обеда 14:00-18:00
        "Sleep": {"start": 22, "end": 7},       # Ночь 22:00-07:00
        "Food": {"start": 12, "end": 14},       # Обед 12:00-14:00
        "Work": {"start": 9, "end": 17},        # Рабочий день 9:00-17:00
        "Social": {"start": 18, "end": 22},     # Вечер 18:00-22:00
        "Personal": {"start": 8, "end": 22},    # Гибкое время
        "Health": {"start": 9, "end": 18}       # Днём 9:00-18:00
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
        """Получить все события для конкретной даты (YYYY-MM-DD)"""
        if self.collection is None or not self.user_id:
            return []
        
        from datetime import datetime
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return []
        
        events = self.get_events_for_month(target_date.year, target_date.month)
        
        # Фильтруем только события на эту дату
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
        Найти свободные слоты в указанную дату
        
        Args:
            date: дата в формате YYYY-MM-DD
            duration_hours: продолжительность в часах
            category: категория для определения оптимального времени
        
        Returns:
            list of dicts: [{"start": "HH:MM", "end": "HH:MM", "score": int}, ...]
        """
        from datetime import datetime, timedelta
        
        events = self.get_events_for_date(date)
        
        # Получаем оптимальное время для категории
        optimal = self.OPTIMAL_TIMES.get(category, {"start": 9, "end": 21})
        optimal_start = optimal["start"]
        optimal_end = optimal["end"]
        
        # Создаем список занятых часов
        busy_slots = []
        for event in events:
            try:
                time_part = event["start"].split(" ")[1] if " " in event["start"] else "09:00"
                hour = int(time_part.split(":")[0])
                busy_slots.append(hour)
            except (ValueError, IndexError):
                continue
        
        # Находим свободные слоты в оптимальное время
        free_slots = []
        
        # Для сна особая логика (ночное время)
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
            # Обычная логика для остальных категорий
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
        
        # Если нет слотов в оптимальное время, ищем в любое время (8:00 - 22:00)
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
        """Сохраняет предпочтения пользователя по диете"""
        try:
            # ✅ ИСПРАВЛЕНО: Конвертируем все списки в строки для совместимости с MongoDB
            # MongoDB может хранить списки, но иногда возникают проблемы с хешированием
            
            # Создаём копию чтобы не изменять оригинальный словарь
            safe_preferences = {}
            
            for key, value in preferences.items():
                # Если значение - список, сохраняем как есть (MongoDB поддерживает массивы)
                # Но убеждаемся что это простые типы данных
                if isinstance(value, list):
                    # Конвертируем все элементы списка в строки
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
        """Получает предпочтения пользователя по диете"""
        try:
            user = self.db.users.find_one({"_id": user_id})
            if user and "diet_preferences" in user:
                return user["diet_preferences"]
            return None
        except Exception as e:
            print(f"Error getting diet preferences: {e}")
            return None

    def save_user_goals(self, user_id, goals):
        """Сохраняет цели пользователя (time_management, diet)"""
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
        """Получает цели пользователя"""
        try:
            user = self.db.users.find_one({"_id": user_id})
            if user and "goals" in user:
                return user["goals"]
            return []
        except Exception as e:
            print(f"Error getting user goals: {e}")
            return []

    def has_completed_onboarding(self, user_id):
        """Проверяет прошёл ли пользователь онбординг"""
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
        Сохраняет план питания на неделю.
        
        Args:
            user_id (str): ID пользователя
            meal_plan_data (dict): План с ключами goal, target_calories, plan, created_at
        
        Returns:
            bool: True если успешно
        """
        try:
            # Добавляем user_id
            meal_plan_data["user_id"] = user_id
            
            # Сохраняем или обновляем
            self.db.meal_plans.update_one(
                {"user_id": user_id},
                {"$set": meal_plan_data},
                upsert=True
            )
            
            print(f"✅ Meal plan saved for user {user_id}")
            return True
            
        except Exception as e:
            print(f"Error saving meal plan: {e}")
            return False

    def get_weekly_meal_plan(self, user_id):
        """
        Получает сохранённый план питания.
        
        Args:
            user_id (str): ID пользователя
        
        Returns:
            dict: План питания или None
        """
        try:
            plan = self.db.meal_plans.find_one({"user_id": user_id})
            
            if plan:
                # Удаляем _id для удобства
                plan.pop("_id", None)
                return plan
            
            return None
            
        except Exception as e:
            print(f"Error getting meal plan: {e}")
            return None

    def replace_meal_in_plan(self, user_id, day, meal_type, new_meal):
        """
        Заменяет конкретное блюдо в плане.
        
        Args:
            user_id (str): ID пользователя
            day (str): День недели (monday, tuesday, ...)
            meal_type (str): Тип приёма пищи (breakfast, lunch, dinner, snack)
            new_meal (dict): Новое блюдо с ключами name, calories, protein, carbs, fats
        
        Returns:
            bool: True если успешно
        """
        try:
            # Обновляем конкретное блюдо
            update_path = f"plan.{day}.{meal_type}"
            
            result = self.db.meal_plans.update_one(
                {"user_id": user_id},
                {"$set": {update_path: new_meal}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Replaced {day}'s {meal_type}")
                return True
            else:
                print(f"⚠️ No meal plan found to update")
                return False
            
        except Exception as e:
            print(f"Error replacing meal: {e}")
            return False

    def delete_meal_plan(self, user_id):
        """
        Удаляет план питания пользователя.
        
        Args:
            user_id (str): ID пользователя
        
        Returns:
            bool: True если успешно
        """
        try:
            result = self.db.meal_plans.delete_one({"user_id": user_id})
            
            if result.deleted_count > 0:
                print(f"✅ Meal plan deleted for user {user_id}")
                return True
            else:
                print(f"⚠️ No meal plan found to delete")
                return False
            
        except Exception as e:
            print(f"Error deleting meal plan: {e}")
            return False
            
    # ============= GROCERY STORE METHODS =============

    def set_user_budget(self, user_id, budget):
        """Установить недельный бюджет на продукты"""
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
        """Получить данные о продуктах текущей недели"""
        if self.db is None:
            return None
        
        week_start = get_monday_of_week(datetime.now().date())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        return self.db.grocery_budgets.find_one({
            "user_id": user_id,
            "week_start": week_start_str
        })

    def update_cart(self, user_id, cart):
        """Обновить корзину покупок"""
        if self.db is None:
            return False
        
        week_start = get_monday_of_week(datetime.now().date())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        # Рассчитываем subtotal
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
        """Подтвердить покупку.
        Сохраняет cart -> purchased_cart, очищает cart/subtotal, накапливает spent."""
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
        """Возвращает диапазон текущей недели (Monday-Sunday)"""
        today = datetime.now().date()
        monday = get_monday_of_week(today)
        sunday = monday + timedelta(days=6)
        
        # Форматируем: "Feb 10-16"
        if monday.month == sunday.month:
            return f"{monday.strftime('%b %d')}-{sunday.day}"
        else:
            return f"{monday.strftime('%b %d')}-{sunday.strftime('%b %d')}"
    
    def initialize_starter_inventory(self, user_id):
        """Дать пользователю стартовый инвентарь ВСЕХ продуктов"""
        from data.products import PRODUCTS
        
        if self.db is None:
            return False
        
        week_start = get_monday_of_week(datetime.now().date())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        # Собираем ВСЕ продукты
        starter_items = []
        
        for category, products in PRODUCTS.items():
            for product in products:
                # Даём по 10 единиц каждого продукта
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
            print(f"✅ Starter inventory created: {len(starter_items)} items")
            return True
        except Exception as e:
            print(f"Error creating starter inventory: {e}")
            return False
    
    def update_purchased_items(self, user_id, cart_items, spent):
        """Обновить purchased_cart после удаления товара из купленных."""
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
        """Полностью удалить аккаунт пользователя и все его данные."""
        if self.db is None:
            return False, "Database not connected"
        try:
            # Удаляем события
            self.db.events.delete_many({"user_id": user_id})
            # Удаляем планы питания
            self.db.meal_plans.delete_many({"user_id": user_id})
            # Удаляем данные продуктового магазина
            self.db.grocery_budgets.delete_many({"user_id": user_id})
            # Удаляем самого пользователя
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
        """Обновить имя пользователя."""
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
        """Сохранить base64 аватарки пользователя."""
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
        """Получить base64 аватарки пользователя."""
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
        """Сменить пароль пользователя."""
        if self.db is None:
            return False, "Database not connected"
        try:
            import hashlib
            user = self.db.users.find_one({"_id": user_id})
            if not user:
                return False, "User not found"
            # Проверяем текущий пароль
            hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
            if user.get("password") != hashed_current:
                return False, "Current password is incorrect"
            # Устанавливаем новый
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
        """Отметить событие/задачу как выполненное или нет."""
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
        """Выдать 500 стартовых кредитов новому пользователю.
        Читаем текущий баланс напрямую — если 0 или поля нет, принудительно ставим 500.
        """
        if self.db is None:
            return
        try:
            current = self.get_credits(user_id)
            if current > 0:
                print(f"[Credits] User {user_id} has {current} cr, no top-up needed")
                return

            # Balance is 0 or missing — set 500 unconditionally
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
        """Получить текущий баланс кредитов."""
        if self.db is None:
            return 0
        try:
            user = self.db.users.find_one({"_id": user_id})
            return user.get("credits", 0) if user else 0
        except Exception as e:
            print(f"Error getting credits: {e}")
            return 0

    def spend_credits(self, user_id, amount, reason=""):
        """Списать кредиты. Returns (success: bool, new_balance: int)."""
        if self.db is None:
            return False, 0
        balance = self.get_credits(user_id)
        if balance < amount:
            print(f"[Credits] Not enough: have {balance}, need {amount}")
            return False, balance
        try:
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
            return False, balance

    def add_credits(self, user_id, amount, reason=""):
        """Начислить кредиты пользователю."""
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
        """История операций с кредитами."""
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
        
    def grant_gamemode_privileges(self, user_id: str):
        """
        ✅ НОВОЕ: Выдаёт неограниченные права для аккаунта gamemode
        
        Args:
            user_id: ID пользователя gamemode
        """
        try:
            from datetime import datetime
            
            # Устанавливаем бесконечные кредиты и деньги
            self.db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "credits": 999999999,
                        "grocery_budget": 999999999,
                        "is_moderator": True,
                        "gamemode_activated_at": datetime.now().isoformat()
                    }
                }
            )
            
            print(f"🔑 Gamemode privileges granted to user {user_id}")
            print(f"💰 Credits: 999999999")
            print(f"🛒 Budget: 999999999")
            return True
            
        except Exception as e:
            print(f"❌ Error granting gamemode privileges: {e}")
            return False

    def is_gamemode_account(self, user_id: str) -> bool:
        """
        ✅ НОВОЕ: Проверяет является ли аккаунт gamemode
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool - True если gamemode аккаунт
        """
        try:
            user = self.db.users.find_one({"_id": user_id})
            if user:
                return user.get("is_moderator", False)
            return False
        except Exception as e:
            print(f"❌ Error checking gamemode: {e}")
            return False

    def delete_user_completely(self, user_id: str):
        """
        ✅ ИСПРАВЛЕНО: Полностью удаляет пользователя из всех коллекций
        Теперь никнейм освобождается для повторного использования
        
        Args:
            user_id: ID пользователя для удаления
        """
        try:
            from bson.objectid import ObjectId
            
            # 1. Удаляем пользователя из users
            result = self.db.users.delete_one({"_id": user_id})
            print(f"✅ Deleted user from users collection: {result.deleted_count}")
            
            # 2. Удаляем все события пользователя
            events_result = self.db.events.delete_many({"user_id": user_id})
            print(f"✅ Deleted {events_result.deleted_count} events")
            
            # 3. Удаляем предпочтения диеты
            diet_result = self.db.diet_preferences.delete_many({"user_id": user_id})
            print(f"✅ Deleted {diet_result.deleted_count} diet preferences")
            
            # 4. Удаляем историю покупок в магазине (если есть)
            if "grocery_purchases" in self.db.list_collection_names():
                grocery_result = self.db.grocery_purchases.delete_many({"user_id": user_id})
                print(f"✅ Deleted {grocery_result.deleted_count} grocery purchases")
            
            # 5. Удаляем историю транзакций кредитов (если есть)
            if "credit_transactions" in self.db.list_collection_names():
                credit_result = self.db.credit_transactions.delete_many({"user_id": user_id})
                print(f"✅ Deleted {credit_result.deleted_count} credit transactions")
            
            print(f"🗑️ User {user_id} completely deleted - username is now available")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting user: {e}")
            return False

    def check_username_available(self, username: str, exclude_user_id: str = None) -> bool:
        """
        ✅ ИСПРАВЛЕНО: Проверяет доступность никнейма (учитывая удалённых пользователей)
        
        Args:
            username: Никнейм для проверки
            exclude_user_id: ID пользователя которого нужно исключить из проверки (для редактирования)
            
        Returns:
            bool - True если никнейм доступен
        """
        try:
            query = {"username": username}
            
            # Исключаем текущего пользователя при редактировании профиля
            if exclude_user_id:
                query["_id"] = {"$ne": exclude_user_id}
            
            existing_user = self.db.users.find_one(query)
            
            if existing_user:
                print(f"❌ Username '{username}' is already taken")
                return False
            else:
                print(f"✅ Username '{username}' is available")
                return True
                
        except Exception as e:
            print(f"❌ Error checking username: {e}")
            return False


# Global instance
store = EventStore()