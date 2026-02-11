"""
Расширенная система категорий и типов событий для Corelife
"""

# ═══════════════════════════════════════════════════════════════
# КАТЕГОРИИ СОБЫТИЙ (Categories)
# ═══════════════════════════════════════════════════════════════

EVENT_CATEGORIES = {
    # === ROUTINE (Рутинные действия) ===
    "Routine": {
        "emoji": "🔄",
        "color": "#9E9E9E",  # Серый
        "optimal_time": {"start": 7, "end": 22},
        "description": "Daily routine activities",
        "examples": ["Morning routine", "Brush teeth", "Shower", "Get dressed"],
    },
    
    # === SLEEP (Сон и отдых) ===
    "Sleep": {
        "emoji": "😴",
        "color": "#3F51B5",  # Индиго
        "optimal_time": {"start": 22, "end": 7},
        "description": "Sleep and rest",
        "examples": ["Sleep", "Nap", "Rest"],
    },
    
    # === FOOD (Приёмы пищи) ===
    "Food": {
        "emoji": "🍽️",
        "color": "#FF9800",  # Оранжевый
        "optimal_time": {"start": 8, "end": 20},
        "description": "Meals and eating",
        "examples": ["Breakfast", "Lunch", "Dinner", "Snack"],
        "subcategories": {
            "breakfast": {"time": "08:00", "duration": 1},
            "lunch": {"time": "12:00", "duration": 1},
            "dinner": {"time": "18:00", "duration": 1},
            "snack": {"time": "15:00", "duration": 0.5},
        }
    },
    
    # === STUDY (Учёба) ===
    "Study": {
        "emoji": "📚",
        "color": "#2196F3",  # Синий
        "optimal_time": {"start": 17, "end": 21},
        "description": "Academic activities",
        "examples": ["Study session", "Homework", "Lecture", "Exam", "Reading"],
    },
    
    # === EXERCISE (Тренировки) ===
    "Exercise": {
        "emoji": "💪",
        "color": "#4CAF50",  # Зелёный
        "optimal_time": {"start": 14, "end": 18},
        "description": "Physical activities",
        "examples": ["Workout", "Gym", "Running", "Yoga", "Sports"],
    },
    
    # === WORK (Работа) ===
    "Work": {
        "emoji": "💼",
        "color": "#607D8B",  # Сине-серый
        "optimal_time": {"start": 9, "end": 17},
        "description": "Work-related activities",
        "examples": ["Meeting", "Project", "Deadline", "Presentation"],
    },
    
    # === SOCIAL (Социальные события) ===
    "Social": {
        "emoji": "👥",
        "color": "#E91E63",  # Розовый
        "optimal_time": {"start": 18, "end": 22},
        "description": "Social interactions",
        "examples": ["Hangout", "Party", "Date", "Friends"],
    },
    
    # === HEALTH (Здоровье) ===
    "Health": {
        "emoji": "🏥",
        "color": "#F44336",  # Красный
        "optimal_time": {"start": 9, "end": 18},
        "description": "Health and medical",
        "examples": ["Doctor", "Dentist", "Checkup", "Therapy"],
    },
    
    # === PERSONAL (Личные дела) ===
    "Personal": {
        "emoji": "👤",
        "color": "#9C27B0",  # Фиолетовый
        "optimal_time": {"start": 8, "end": 22},
        "description": "Personal tasks",
        "examples": ["Shopping", "Errands", "Hobbies", "Relaxation"],
    },
    
    # === ENTERTAINMENT (Развлечения) ===
    "Entertainment": {
        "emoji": "🎮",
        "color": "#00BCD4",  # Циановый
        "optimal_time": {"start": 19, "end": 23},
        "description": "Fun and entertainment",
        "examples": ["Gaming", "Movies", "TV shows", "Music"],
    },
}


# ═══════════════════════════════════════════════════════════════
# ТИПЫ СОБЫТИЙ (Event Types)
# ═══════════════════════════════════════════════════════════════

EVENT_TYPES = {
    # Обычное событие с фиксированным временем
    "event": {
        "label": "Event",
        "description": "Time-specific activity",
        "requires_time": True,
    },
    
    # Задача (может быть без времени)
    "task": {
        "label": "Task",
        "description": "To-do item",
        "requires_time": False,
    },
    
    # Рутинное действие (повторяющееся)
    "routine": {
        "label": "Routine",
        "description": "Recurring routine activity",
        "requires_time": True,
        "default_duration": 0.5,  # 30 минут
    },
    
    # Приём пищи (специальный тип)
    "meal": {
        "label": "Meal",
        "description": "Food intake",
        "requires_time": True,
        "default_category": "Food",
        "default_duration": 1,  # 1 час
    },
}


# ═══════════════════════════════════════════════════════════════
# KEYWORD MAPPING (для AI распознавания)
# ═══════════════════════════════════════════════════════════════

CATEGORY_KEYWORDS = {
    "Routine": [
        "routine", "morning routine", "brush teeth", "shower", "get dressed",
        "wash face", "skincare", "makeup", "hair", "get ready",
        "утренняя рутина", "чистка зубов", "душ"
    ],
    
    "Sleep": [
        "sleep", "nap", "rest", "bedtime", "wake up", "alarm",
        "сон", "дремота", "отдых", "ложиться спать"
    ],
    
    "Food": [
        "breakfast", "lunch", "dinner", "snack", "meal", "eat", "food",
        "brunch", "supper", "завтрак", "обед", "ужин", "перекус"
    ],
    
    "Study": [
        "study", "homework", "assignment", "exam", "test", "lecture",
        "class", "reading", "research", "learning", "tutorial",
        "учёба", "домашка", "экзамен", "лекция", "занятие"
    ],
    
    "Exercise": [
        "workout", "gym", "exercise", "running", "jogging", "yoga",
        "fitness", "training", "sports", "cycling", "swimming",
        "тренировка", "зал", "фитнес", "бег", "спорт"
    ],
    
    "Work": [
        "work", "meeting", "project", "deadline", "presentation",
        "conference", "call", "interview", "shift",
        "работа", "встреча", "проект", "дедлайн"
    ],
    
    "Social": [
        "hangout", "party", "date", "friends", "gathering", "meetup",
        "dinner with", "coffee with", "drinks", "visit",
        "встреча с друзьями", "вечеринка", "свидание"
    ],
    
    "Health": [
        "doctor", "dentist", "checkup", "appointment", "therapy",
        "hospital", "clinic", "medicine", "treatment",
        "врач", "доктор", "стоматолог", "больница", "приём"
    ],
    
    "Personal": [
        "shopping", "errands", "groceries", "cleaning", "laundry",
        "haircut", "bank", "post office", "hobby",
        "покупки", "уборка", "стирка", "парикмахерская"
    ],
    
    "Entertainment": [
        "gaming", "game", "movie", "tv", "series", "music", "concert",
        "theater", "cinema", "netflix", "youtube",
        "игры", "фильм", "кино", "музыка", "концерт"
    ],
}


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def detect_category_from_title(title: str) -> str:
    """
    Определяет категорию события по названию
    
    Args:
        title: Название события
    
    Returns:
        Категория (например "Study", "Food", "Exercise")
    """
    title_lower = title.lower()
    
    # Проверяем ключевые слова для каждой категории
    category_scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in title_lower:
                # Чем точнее совпадение, тем выше балл
                if keyword == title_lower:
                    score += 10
                elif title_lower.startswith(keyword):
                    score += 5
                else:
                    score += 1
        
        if score > 0:
            category_scores[category] = score
    
    # Возвращаем категорию с максимальным баллом
    if category_scores:
        return max(category_scores, key=category_scores.get)
    
    # По умолчанию - Personal
    return "Personal"


def get_default_duration(category: str, event_type: str = "event") -> float:
    """
    Возвращает длительность по умолчанию для события
    
    Args:
        category: Категория события
        event_type: Тип события
    
    Returns:
        Длительность в часах
    """
    # Специальные длительности
    durations = {
        "Routine": 0.5,   # 30 минут
        "Sleep": 8,       # 8 часов
        "Food": 1,        # 1 час
        "Study": 2,       # 2 часа
        "Exercise": 1,    # 1 час
        "Work": 1,        # 1 час (для митингов)
        "Social": 2,      # 2 часа
        "Health": 1,      # 1 час
        "Personal": 1,    # 1 час
        "Entertainment": 2,  # 2 часа
    }
    
    return durations.get(category, 1)


def is_meal_event(title: str) -> bool:
    """
    Проверяет является ли событие приёмом пищи
    
    Args:
        title: Название события
    
    Returns:
        True если это еда
    """
    meal_keywords = ["breakfast", "lunch", "dinner", "snack", "meal", "eat", "brunch"]
    title_lower = title.lower()
    
    return any(keyword in title_lower for keyword in meal_keywords)


def get_meal_type(title: str) -> str:
    """
    Определяет тип приёма пищи
    
    Returns:
        "breakfast", "lunch", "dinner", "snack" или None
    """
    title_lower = title.lower()
    
    if "breakfast" in title_lower or "завтрак" in title_lower:
        return "breakfast"
    elif "lunch" in title_lower or "обед" in title_lower:
        return "lunch"
    elif "dinner" in title_lower or "ужин" in title_lower:
        return "dinner"
    elif "snack" in title_lower or "перекус" in title_lower:
        return "snack"
    
    return None