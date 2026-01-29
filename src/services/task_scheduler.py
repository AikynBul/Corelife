from datetime import datetime, timedelta
from typing import List, Dict, Tuple

class TaskScheduler:
    """
    Планировщик задач на день.
    Распределяет задачи по времени с учётом базовых потребностей (еда, сон).
    """
    
    # Фиксированное время для базовых задач
    FIXED_SCHEDULE = {
        "breakfast": {"start": "08:00", "end": "09:00", "category": "Food"},
        "lunch": {"start": "13:00", "end": "14:00", "category": "Food"},
        "dinner": {"start": "19:00", "end": "20:00", "category": "Food"},
        "sleep": {"start": "23:00", "end": "07:00", "category": "Sleep"},
    }
    
    # Категории задач и их длительность по умолчанию (в часах)
    DEFAULT_DURATIONS = {
        "Study": 2.0,
        "Exercise": 1.0,
        "Work": 2.0,
        "Social": 2.0,
        "Health": 1.0,
        "Personal": 1.0,
        "Food": 1.0,
        "Sleep": 8.0,
    }
    
    # Предпочтительное время для разных категорий
    PREFERRED_TIMES = {
        "Study": [(9, 12), (15, 18)],      # Утро и после обеда
        "Exercise": [(6, 8), (17, 19)],     # Раннее утро или вечер
        "Work": [(9, 17)],                  # Рабочий день
        "Social": [(18, 22)],               # Вечер
        "Health": [(10, 12), (14, 16)],    # День
        "Food": [(8, 9), (13, 14), (19, 20)], # Время еды
    }
    
    def __init__(self):
        self.scheduled_tasks = []
        self.needs_clarification = []
    
    def parse_tasks_from_text(self, text: str, current_date: datetime = None) -> Dict:
        """
        Парсит текст пользователя и определяет задачи.
        
        Args:
            text: Текст от пользователя
            current_date: Текущая дата (по умолчанию сегодня)
            
        Returns:
            Dict с автоматически запланированными задачами и задачами требующими уточнения
        """
        if current_date is None:
            current_date = datetime.now()
        
        text_lower = text.lower()
        
        # Определяем базовые задачи (еда, сон)
        basic_tasks = self._detect_basic_tasks(text_lower, current_date)
        
        # Определяем специфичные задачи (учёба, спорт и т.д.)
        specific_tasks = self._detect_specific_tasks(text_lower, current_date)
        
        # Распределяем задачи по времени
        auto_scheduled = []
        needs_clarification = []
        
        # ✅ ИСПРАВЛЕНО: Базовые задачи всегда автоматические
        for task in basic_tasks:
            auto_scheduled.append(task)
        
        # ✅ ИСПРАВЛЕНО: Специфичные задачи ВСЕГДА требуют уточнения (если нет точного времени)
        for task in specific_tasks:
            if task.get("has_time", False):
                # Если время указано явно - добавляем как есть
                auto_scheduled.append(task)
            else:
                # ✅ КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Специфичные задачи БЕЗ времени требуют уточнения
                suggested_time = self._suggest_time_for_task(
                    task, 
                    auto_scheduled, 
                    current_date
                )
                task["suggested_start"] = suggested_time["start"]
                task["suggested_end"] = suggested_time["end"]
                needs_clarification.append(task)
        
        return {
            "auto_scheduled": auto_scheduled,
            "needs_clarification": needs_clarification,
            "total_tasks": len(auto_scheduled) + len(needs_clarification)
        }
    
    def _detect_basic_tasks(self, text: str, current_date: datetime) -> List[Dict]:
        """Определяет базовые задачи (завтрак, обед, ужин, сон)"""
        tasks = []
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Завтрак
        if any(word in text for word in ["завтрак", "breakfast", "позавтракать", "поесть утром"]):
            tasks.append({
                "title": "Breakfast",
                "category": "Food",
                "start": f"{date_str} 08:00",
                "end": f"{date_str} 09:00",
                "auto_schedule": False,
                "duration_hours": 1,
                "priority": "High",
                "type": "event"
            })
        
        # Обед
        if any(word in text for word in ["обед", "lunch", "пообедать", "поесть днём", "поесть в обед"]):
            tasks.append({
                "title": "Lunch",
                "category": "Food",
                "start": f"{date_str} 13:00",
                "end": f"{date_str} 14:00",
                "auto_schedule": False,
                "duration_hours": 1,
                "priority": "High",
                "type": "event"
            })
        
        # Ужин
        if any(word in text for word in ["ужин", "dinner", "поужинать", "поесть вечером"]):
            tasks.append({
                "title": "Dinner",
                "category": "Food",
                "start": f"{date_str} 19:00",
                "end": f"{date_str} 20:00",
                "auto_schedule": False,
                "duration_hours": 1,
                "priority": "High",
                "type": "event"
            })
        
        # Сон
        if any(word in text for word in ["сон", "sleep", "поспать", "лечь спать"]):
            # Сон начинается сегодня в 23:00 и заканчивается завтра в 07:00
            next_day = current_date + timedelta(days=1)
            tasks.append({
                "title": "Sleep",
                "category": "Sleep",
                "start": f"{date_str} 23:00",
                "end": f"{next_day.strftime('%Y-%m-%d')} 07:00",
                "auto_schedule": False,
                "duration_hours": 8,
                "priority": "High",
                "type": "event"
            })
        
        return tasks
    
    def _detect_specific_tasks(self, text: str, current_date: datetime) -> List[Dict]:
        """
        ✅ ИСПРАВЛЕНО: Определяет специфичные задачи (учёба, спорт, работа)
        Эти задачи ВСЕГДА требуют уточнения времени (если оно не указано явно)
        """
        tasks = []
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Учёба / подготовка к экзаменам
        if any(word in text for word in ["sat", "экзамен", "exam", "учёба", "study", "подготовка", "homework", "домашка"]):
            # ✅ ВАЖНО: Проверяем есть ли КОНКРЕТНОЕ время (например "at 3pm")
            has_explicit_time = self._extract_explicit_time(text)
            
            task = {
                "title": "Study Session",
                "category": "Study",
                "duration_hours": 2,
                "priority": "High",
                "type": "task",
                "has_time": has_explicit_time is not None
            }
            
            if has_explicit_time:
                # Если указано конкретное время - используем его
                task["start"] = f"{date_str} {has_explicit_time}"
                end_time = self._add_hours_to_time(has_explicit_time, 2)
                task["end"] = f"{date_str} {end_time}"
                task["auto_schedule"] = False
            else:
                # ✅ БЕЗ времени - требует уточнения
                task["auto_schedule"] = True
            
            tasks.append(task)
        
        # Спорт / тренировка
        if any(word in text for word in ["зал", "gym", "тренировка", "workout", "спорт", "exercise", "потренироваться"]):
            has_explicit_time = self._extract_explicit_time(text)
            
            task = {
                "title": "Workout",
                "category": "Exercise",
                "duration_hours": 1,
                "priority": "Medium",
                "type": "event",
                "has_time": has_explicit_time is not None
            }
            
            if has_explicit_time:
                task["start"] = f"{date_str} {has_explicit_time}"
                end_time = self._add_hours_to_time(has_explicit_time, 1)
                task["end"] = f"{date_str} {end_time}"
                task["auto_schedule"] = False
            else:
                # ✅ БЕЗ времени - требует уточнения
                task["auto_schedule"] = True
            
            tasks.append(task)
        
        # Работа / проект
        if any(word in text for word in ["работа", "work", "проект", "project", "задание"]):
            # Исключаем слово "workout" чтобы не путать с работой
            if "workout" not in text.lower():
                has_explicit_time = self._extract_explicit_time(text)
                
                task = {
                    "title": "Work on Project",
                    "category": "Work",
                    "duration_hours": 2,
                    "priority": "High",
                    "type": "task",
                    "has_time": has_explicit_time is not None
                }
                
                if has_explicit_time:
                    task["start"] = f"{date_str} {has_explicit_time}"
                    end_time = self._add_hours_to_time(has_explicit_time, 2)
                    task["end"] = f"{date_str} {end_time}"
                    task["auto_schedule"] = False
                else:
                    # ✅ БЕЗ времени - требует уточнения
                    task["auto_schedule"] = True
                
                tasks.append(task)
        
        return tasks
    
    def _extract_explicit_time(self, text: str) -> str or None:
        """
        ✅ НОВЫЙ МЕТОД: Извлекает явно указанное время из текста
        Примеры: "at 3pm", "в 15:00", "at 18:00"
        
        Returns:
            Время в формате "HH:MM" или None если не найдено
        """
        import re
        
        # Паттерны для времени
        patterns = [
            r'at (\d{1,2}):?(\d{2})?\s*(am|pm)?',  # "at 3pm", "at 15:00", "at 3:30pm"
            r'в (\d{1,2}):(\d{2})',                 # "в 15:00"
            r'(\d{1,2}):(\d{2})',                   # "15:00"
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.lastindex >= 2 and match.group(2) else 0
                
                # Обработка am/pm
                if match.lastindex >= 3 and match.group(3):
                    meridiem = match.group(3)
                    if meridiem == 'pm' and hour < 12:
                        hour += 12
                    elif meridiem == 'am' and hour == 12:
                        hour = 0
                
                return f"{hour:02d}:{minute:02d}"
        
        return None
    
    def _add_hours_to_time(self, time_str: str, hours: float) -> str:
        """
        ✅ НОВЫЙ МЕТОД: Добавляет часы к времени
        
        Args:
            time_str: Время в формате "HH:MM"
            hours: Количество часов для добавления
            
        Returns:
            Новое время в формате "HH:MM"
        """
        hour, minute = map(int, time_str.split(":"))
        dt = datetime.now().replace(hour=hour, minute=minute)
        dt += timedelta(hours=hours)
        return dt.strftime("%H:%M")
    
    def _suggest_time_for_task(
        self, 
        task: Dict, 
        already_scheduled: List[Dict],
        current_date: datetime
    ) -> Dict:
        """
        Предлагает оптимальное время для задачи на основе:
        - Категории задачи
        - Уже запланированных задач
        - Предпочтительного времени для категории
        """
        category = task.get("category", "Personal")
        duration = task.get("duration_hours", 1)
        
        # Получаем предпочтительные временные слоты для категории
        preferred_slots = self.PREFERRED_TIMES.get(category, [(9, 17)])
        
        # Находим первый свободный слот
        for start_hour, end_hour in preferred_slots:
            for hour in range(start_hour, end_hour):
                proposed_start = current_date.replace(hour=hour, minute=0, second=0)
                proposed_end = proposed_start + timedelta(hours=duration)
                
                # Проверяем не пересекается ли с уже запланированными задачами
                if not self._has_conflict(proposed_start, proposed_end, already_scheduled):
                    return {
                        "start": proposed_start.strftime("%Y-%m-%d %H:%M"),
                        "end": proposed_end.strftime("%Y-%m-%d %H:%M")
                    }
        
        # Если не нашли свободный слот - предлагаем первый доступный
        next_available = current_date.replace(hour=9, minute=0, second=0)
        return {
            "start": next_available.strftime("%Y-%m-%d %H:%M"),
            "end": (next_available + timedelta(hours=duration)).strftime("%Y-%m-%d %H:%M")
        }
    
    def _has_conflict(
        self, 
        start: datetime, 
        end: datetime, 
        scheduled_tasks: List[Dict]
    ) -> bool:
        """Проверяет есть ли конфликт с уже запланированными задачами"""
        for task in scheduled_tasks:
            task_start = datetime.strptime(task["start"], "%Y-%m-%d %H:%M")
            task_end = datetime.strptime(task["end"], "%Y-%m-%d %H:%M")
            
            # Проверяем пересечение
            if (start < task_end) and (end > task_start):
                return True
        
        return False
    
    def schedule_task_at_time(
        self, 
        task: Dict, 
        start_time: str,
        current_date: datetime = None
    ) -> Dict:
        """
        Планирует задачу на конкретное время.
        
        Args:
            task: Задача из needs_clarification
            start_time: Время начала в формате "HH:MM"
            current_date: Дата (по умолчанию сегодня)
            
        Returns:
            Полностью запланированная задача
        """
        if current_date is None:
            current_date = datetime.now()
        
        date_str = current_date.strftime("%Y-%m-%d")
        duration = task.get("duration_hours", 1)
        
        # Парсим время
        try:
            hour, minute = map(int, start_time.split(":"))
            start_dt = current_date.replace(hour=hour, minute=minute, second=0)
            end_dt = start_dt + timedelta(hours=duration)
            
            task["start"] = start_dt.strftime("%Y-%m-%d %H:%M")
            task["end"] = end_dt.strftime("%Y-%m-%d %H:%M")
            task["auto_schedule"] = False
            
            # Удаляем вспомогательные поля
            task.pop("suggested_start", None)
            task.pop("suggested_end", None)
            task.pop("has_time", None)
            
            return task
            
        except Exception as e:
            print(f"Error scheduling task: {e}")
            return None