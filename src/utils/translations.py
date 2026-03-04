class Translations:
    def __init__(self):
        self.current_language = "en"
        self.translations = {
            "en": {
                "app_title": "AI Calendar",
                "login": "Login",
                "logout": "Logout",
                "settings": "Settings",
                "language": "Language",
                "save": "Save",
                "cancel": "Cancel",
                "create": "Create",
                "month_view": "Month View",
                "week_view": "Week View",
                "day_view": "Day View",
                "my_calendars": "My calendars",
                "events": "Events",
                "tasks": "Tasks",
                "birthdays": "Birthdays",
                "holidays": "Holidays",
                "account": "Account",
                "name": "Name",
                "email": "Email",
                "current_password": "Current Password",
                "new_password": "New Password",
                "confirm_password": "Confirm New Password",
                "account_info": "Account Information",
                "save_name": "Save Name",
                "security": "Security",
                "change_password": "Change Password",
                "actions": "Actions",
                "delete_account": "Delete Account",
                "months": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
                "weekdays_short": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "no_events": "No events today",
                "event_details": "Event Details",
                "description": "Description",
                "time": "Time",
                "close": "Close",
                "calendar": "Calendar",
                "diet_view": "Diet",
                
                # Grocery Store
                "grocery_store": "Grocery Store",
                "shop": "Shop",
                "purchased_items": "Purchased Items",
                "buy_selected": "Buy Selected",
                "clear": "Clear",
                "selected": "Selected",
                "items": "items",
                "total": "Total",
                "after_purchase": "After purchase",
                "total_spent": "Total Spent",
                "no_purchases": "No purchases yet",
                "buy_groceries_first": "Buy groceries first!",
                "remove": "Remove",
                "item_removed": "Item removed",
                
                # Categories
                "fruits": "Fruits",
                "vegetables": "Vegetables",
                "meat": "Meat & Eggs",
                "dairy": "Dairy",
                "bakery": "Bakery & Grains",
                "other": "Other",
                
                # Diet
                "generate_diet": "Generate Diet Plan",
                "add_to_calendar": "Add to Calendar",
                "your_diet_plan": "Your Diet Plan",
                "diet_preferences": "Your Diet Preferences",
                "diet_goal": "Diet Goal",
                "meal_type": "Meal Type",
                "medical_conditions": "Medical Conditions"
            },
            "ru": {
                "app_title": "AI Календарь",
                "login": "Войти",
                "logout": "Выйти",
                "settings": "Настройки",
                "language": "Язык",
                "save": "Сохранить",
                "cancel": "Отмена",
                "create": "Создать",
                "month_view": "Месяц",
                "week_view": "Неделя",
                "day_view": "День",
                "my_calendars": "Мои календари",
                "events": "События",
                "tasks": "Задачи",
                "birthdays": "Дни рождения",
                "holidays": "Праздники",
                "account": "Аккаунт",
                "name": "Имя",
                "email": "Email",
                "current_password": "Текущий пароль",
                "new_password": "Новый пароль",
                "confirm_password": "Подтвердите пароль",
                "account_info": "Информация об аккаунте",
                "save_name": "Сохранить имя",
                "security": "Безопасность",
                "change_password": "Сменить пароль",
                "actions": "Действия",
                "delete_account": "Удалить аккаунт",
                "months": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
                "weekdays_short": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
                "no_events": "Нет событий сегодня",
                "event_details": "Детали события",
                "description": "Описание",
                "time": "Время",
                "close": "Закрыть",
                "calendar": "Календарь",
                "diet_view": "Диета",
                
                # Grocery Store
                "grocery_store": "Магазин",
                "shop": "Магазин",
                "purchased_items": "Купленные товары",
                "buy_selected": "Купить выбранное",
                "clear": "Очистить",
                "selected": "Выбрано",
                "items": "товаров",
                "total": "Итого",
                "after_purchase": "После покупки",
                "total_spent": "Всего потрачено",
                "no_purchases": "Покупок пока нет",
                "buy_groceries_first": "Сначала купите продукты!",
                "remove": "Удалить",
                "item_removed": "Товар удалён",
                
                # Categories
                "fruits": "Фрукты",
                "vegetables": "Овощи",
                "meat": "Мясо и яйца",
                "dairy": "Молочные продукты",
                "bakery": "Хлеб и крупы",
                "other": "Другое",
                
                # Diet
                "generate_diet": "Создать план питания",
                "add_to_calendar": "Добавить в календарь",
                "your_diet_plan": "Ваш план питания",
                "diet_preferences": "Ваши предпочтения",
                "diet_goal": "Цель диеты",
                "meal_type": "Тип питания",
                "medical_conditions": "Медицинские ограничения"
            }
        }

    def set_language(self, language_code):
        if language_code in self.translations:
            self.current_language = language_code

    def get(self, key):
        return self.translations.get(self.current_language, {}).get(key, key)

translations = Translations()