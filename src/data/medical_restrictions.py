"""
База медицинских противопоказаний для диеты.
Используется AI для фильтрации нежелательных продуктов.
"""

# ═══════════════════════════════════════════════════════════════
# БАЗА МЕДИЦИНСКИХ ПРОТИВОПОКАЗАНИЙ
# ═══════════════════════════════════════════════════════════════

MEDICAL_RESTRICTIONS = {
    "diabetes": {
        "name": "Diabetes",
        "name_ru": "Диабет",
        "avoid_keywords": [
            "sugar", "candy", "dessert", "cake", "cookie", "soda", "juice",
            "white bread", "white rice", "pasta", "pastry", "honey", "syrup",
            "сахар", "конфеты", "десерт", "торт", "печенье", "газировка"
        ],
        "recommendation": "Focus on low-GI foods, complex carbs, lean proteins, vegetables",
    },
    
    "pancreatitis": {
        "name": "Pancreatitis",
        "name_ru": "Панкреатит",
        "avoid_keywords": [
            "fried", "oil", "butter", "cream", "fatty meat", "pork", "bacon",
            "cheese", "whole milk", "avocado", "nuts", "mayonnaise", "fast food",
            "жареное", "масло", "сливки", "жирное мясо", "свинина"
        ],
        "recommendation": "Low-fat diet, lean proteins, steamed vegetables, whole grains",
    },
    
    "gastritis": {
        "name": "Gastritis",
        "name_ru": "Гастрит",
        "avoid_keywords": [
            "spicy", "pepper", "chili", "citrus", "tomato", "coffee", "alcohol",
            "fried food", "chocolate", "soda", "vinegar", "pickled",
            "острое", "перец", "чили", "кофе", "алкоголь", "жареное"
        ],
        "recommendation": "Mild foods, avoid irritants, eat small frequent meals",
    },
    
    "cholecystitis": {
        "name": "Cholecystitis",
        "name_ru": "Холецистит",
        "avoid_keywords": [
            "fatty meat", "fried", "butter", "oil", "cream", "egg yolk",
            "cheese", "nuts", "chocolate", "spicy", "alcohol",
            "жирное мясо", "яичный желток", "шоколад", "острое"
        ],
        "recommendation": "Low-fat diet, lean proteins, vegetables, whole grains",
    },
    
    "hypertension": {
        "name": "Hypertension",
        "name_ru": "Гипертония",
        "avoid_keywords": [
            "salt", "soy sauce", "pickled", "canned", "processed meat",
            "fast food", "chips", "crackers", "instant noodles", "bacon",
            "соль", "соевый соус", "консервы", "чипсы", "фастфуд"
        ],
        "recommendation": "DASH diet, reduce sodium, increase potassium-rich foods",
    },
    
    "celiac": {
        "name": "Celiac Disease",
        "name_ru": "Целиакия",
        "avoid_keywords": [
            "wheat", "barley", "rye", "bread", "pasta", "cake", "cookie",
            "beer", "malt", "couscous", "farro", "semolina",
            "пшеница", "ячмень", "рожь", "хлеб", "паста", "пиво"
        ],
        "recommendation": "Strict gluten-free diet",
    },
    
    "lactose intolerance": {
        "name": "Lactose Intolerance",
        "name_ru": "Лактозная непереносимость",
        "avoid_keywords": [
            "milk", "cheese", "yogurt", "cream", "ice cream", "butter",
            "whey", "casein", "lactose",
            "молоко", "сыр", "йогурт", "сливки", "мороженое", "масло"
        ],
        "recommendation": "Lactose-free or plant-based alternatives",
    },
    
    "gout": {
        "name": "Gout",
        "name_ru": "Подагра",
        "avoid_keywords": [
            "red meat", "organ meat", "liver", "shellfish", "sardines",
            "anchovies", "beer", "alcohol", "sugary drinks", "fructose",
            "красное мясо", "печень", "моллюски", "пиво"
        ],
        "recommendation": "Low-purine diet, plenty of water, limit alcohol",
    },
    
    "kidney disease": {
        "name": "Kidney Disease",
        "name_ru": "Болезни почек",
        "avoid_keywords": [
            "salt", "processed meat", "bananas", "oranges", "potatoes",
            "tomatoes", "dairy", "nuts", "beans", "whole grain bread",
            "соль", "бананы", "апельсины", "картофель", "орехи"
        ],
        "recommendation": "Controlled protein, sodium, potassium, and phosphorus",
    },
    
    "high cholesterol": {
        "name": "High Cholesterol",
        "name_ru": "Повышенный холестерин",
        "avoid_keywords": [
            "red meat", "butter", "cheese", "egg yolk", "fried food",
            "fast food", "processed meat", "palm oil", "coconut oil", "margarine",
            "красное мясо", "яичный желток", "жареное", "фастфуд"
        ],
        "recommendation": "Low saturated fat, high fiber, omega-3 rich foods",
    },
}


def get_restrictions_for_condition(condition_text):
    """
    Получает ограничения для конкретного заболевания.
    
    Args:
        condition_text (str): Название заболевания
    
    Returns:
        dict: Информация об ограничениях или None
    """
    if not condition_text:
        return None
        
    condition_lower = condition_text.lower().strip()
    
    # Прямое совпадение
    if condition_lower in MEDICAL_RESTRICTIONS:
        return MEDICAL_RESTRICTIONS[condition_lower]
    
    # Поиск по частичному совпадению
    for key, value in MEDICAL_RESTRICTIONS.items():
        if key in condition_lower or condition_lower in key:
            return value
        # Проверка русского названия
        if value.get("name_ru", "").lower() in condition_lower:
            return value
    
    return None


def get_all_avoid_keywords(medical_notes):
    """
    Извлекает все запрещённые продукты из медицинских ограничений.
    
    Args:
        medical_notes (str): Медицинские ограничения пользователя
    
    Returns:
        list: Список ключевых слов которые нужно избегать
    """
    if not medical_notes:
        return []
    
    all_keywords = set()
    
    # Разделяем по запятым
    conditions = [c.strip() for c in medical_notes.split(",")]
    
    for condition in conditions:
        restrictions = get_restrictions_for_condition(condition)
        if restrictions:
            all_keywords.update(restrictions["avoid_keywords"])
    
    return list(all_keywords)


def should_avoid_food(food_name, medical_notes):
    """
    Проверяет нужно ли избегать продукт на основе медицинских ограничений.
    
    Args:
        food_name (str): Название продукта или блюда
        medical_notes (str): Медицинские ограничения
    
    Returns:
        tuple: (bool - избегать, str - причина)
    """
    if not medical_notes or not food_name:
        return False, None
    
    food_lower = food_name.lower()
    
    conditions = [c.strip() for c in medical_notes.split(",")]
    
    for condition in conditions:
        restrictions = get_restrictions_for_condition(condition)
        if restrictions:
            # Проверяем ключевые слова
            for keyword in restrictions["avoid_keywords"]:
                if keyword.lower() in food_lower:
                    return True, f"Avoid due to {restrictions['name']}"
    
    return False, None


def format_restrictions_for_ai_prompt(medical_notes):
    """
    Форматирует медицинские ограничения для AI промпта.
    
    Args:
        medical_notes (str): Медицинские ограничения пользователя
    
    Returns:
        str: Отформатированная строка для AI
    """
    if not medical_notes:
        return ""
    
    conditions = [c.strip() for c in medical_notes.split(",")]
    restrictions_text = []
    
    for condition in conditions:
        info = get_restrictions_for_condition(condition)
        if info:
            avoid_list = ", ".join(info["avoid_keywords"][:10])  # Первые 10
            restrictions_text.append(f"{info['name']}: Avoid {avoid_list}")
    
    if restrictions_text:
        return "MEDICAL RESTRICTIONS:\n" + "\n".join(restrictions_text)
    
    return ""