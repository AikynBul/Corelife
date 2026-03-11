"""
База данных продуктов для Grocery Store
Цены основаны на Small marketplace (Semey, Kazakhstan)
Все цены в тенге (₸)
"""

PRODUCTS = {
    "fruits": [
        {"id": "apple", "name": "Apples", "name_ru": "Яблоки", "unit": "1 kg", "price": 800, "icon": "🍎"},
        {"id": "banana", "name": "Bananas", "name_ru": "Бананы", "unit": "1 kg", "price": 600, "icon": "🍌"},
        {"id": "orange", "name": "Oranges", "name_ru": "Апельсины", "unit": "1 kg", "price": 700, "icon": "🍊"},
        {"id": "grape", "name": "Grapes", "name_ru": "Виноград", "unit": "1 kg", "price": 1200, "icon": "🍇"},
        {"id": "watermelon", "name": "Watermelon", "name_ru": "Арбуз", "unit": "1 kg", "price": 300, "icon": "🍉"},
    ],
    
    "vegetables": [
        {"id": "potato", "name": "Potatoes", "name_ru": "Картофель", "unit": "1 kg", "price": 200, "icon": "🥔"},
        {"id": "carrot", "name": "Carrots", "name_ru": "Морковь", "unit": "1 kg", "price": 250, "icon": "🥕"},
        {"id": "onion", "name": "Onions", "name_ru": "Лук", "unit": "1 kg", "price": 180, "icon": "🟣"},
        {"id": "tomato", "name": "Tomatoes", "name_ru": "Помидоры", "unit": "1 kg", "price": 600, "icon": "🍅"},
        {"id": "cucumber", "name": "Cucumbers", "name_ru": "Огурцы", "unit": "1 kg", "price": 500, "icon": "🥒"},
        {"id": "pepper", "name": "Bell Pepper", "name_ru": "Перец", "unit": "1 kg", "price": 800, "icon": "🌶️"},
        {"id": "cabbage", "name": "Cabbage", "name_ru": "Капуста", "unit": "1 kg", "price": 150, "icon": "🥬"},
    ],
    
    "meat": [
        {"id": "chicken_breast", "name": "Chicken Breast", "name_ru": "Куриная грудка", "unit": "1 kg", "price": 2500, "icon": "🐔"},
        {"id": "chicken_legs", "name": "Chicken Legs", "name_ru": "Куриные ножки", "unit": "1 kg", "price": 1800, "icon": "🍗"},
        {"id": "beef", "name": "Beef", "name_ru": "Говядина", "unit": "1 kg", "price": 3500, "icon": "🥩"},
        {"id": "pork", "name": "Pork", "name_ru": "Свинина", "unit": "1 kg", "price": 2800, "icon": "🥓"},
        {"id": "minced_meat", "name": "Minced Meat", "name_ru": "Фарш", "unit": "1 kg", "price": 2200, "icon": "🥩"},
        {"id": "eggs", "name": "Eggs", "name_ru": "Яйца", "unit": "10 pcs", "price": 400, "icon": "🥚"},
    ],
    
    "dairy": [
        {"id": "milk", "name": "Milk", "name_ru": "Молоко", "unit": "1 L", "price": 350, "icon": "🥛"},
        {"id": "cheese", "name": "Cheese", "name_ru": "Сыр", "unit": "500 g", "price": 1200, "icon": "🧀"},
        {"id": "cottage_cheese", "name": "Cottage Cheese", "name_ru": "Творог", "unit": "500 g", "price": 500, "icon": "🧀"},
        {"id": "yogurt", "name": "Yogurt", "name_ru": "Йогурт", "unit": "500 g", "price": 400, "icon": "🍨"},
        {"id": "butter", "name": "Butter", "name_ru": "Сливочное масло", "unit": "200 g", "price": 600, "icon": "🥣"},
        {"id": "sour_cream", "name": "Sour Cream", "name_ru": "Сметана", "unit": "500 g", "price": 450, "icon": "🥄"},
    ],
    
    "bakery": [
        {"id": "bread", "name": "White Bread", "name_ru": "Белый хлеб", "unit": "1 loaf", "price": 200, "icon": "🍞"},
        {"id": "black_bread", "name": "Black Bread", "name_ru": "Чёрный хлеб", "unit": "1 loaf", "price": 180, "icon": "🍞"},
        {"id": "pasta", "name": "Pasta", "name_ru": "Макароны", "unit": "500 g", "price": 300, "icon": "🍝"},
        {"id": "rice", "name": "Rice", "name_ru": "Рис", "unit": "1 kg", "price": 400, "icon": "🍚"},
        {"id": "buckwheat", "name": "Buckwheat", "name_ru": "Гречка", "unit": "1 kg", "price": 450, "icon": "🌾"},
        {"id": "flour", "name": "Flour", "name_ru": "Мука", "unit": "1 kg", "price": 250, "icon": "🌫️"},
    ],
    
    "other": [
        {"id": "sunflower_oil", "name": "Sunflower Oil", "name_ru": "Подсолнечное масло", "unit": "1 L", "price": 800, "icon": "🌻"},
        {"id": "olive_oil", "name": "Olive Oil", "name_ru": "Оливковое масло", "unit": "500 ml", "price": 1500, "icon": "🍶"},
        {"id": "salt", "name": "Salt", "name_ru": "Соль", "unit": "500 g", "price": 100, "icon": "🧂"},
        {"id": "sugar", "name": "Sugar", "name_ru": "Сахар", "unit": "1 kg", "price": 300, "icon": "🍬"},
        {"id": "tea", "name": "Tea", "name_ru": "Чай", "unit": "100 g", "price": 500, "icon": "🍵"},
        {"id": "coffee", "name": "Coffee", "name_ru": "Кофе", "unit": "200 g", "price": 1200, "icon": "☕"},
    ]
}

# Категории для UI
CATEGORIES = {
    "fruits": {"name": "Fruits", "name_ru": "Фрукты", "icon": "🍎"},
    "vegetables": {"name": "Vegetables", "name_ru": "Овощи", "icon": "🥦"},
    "meat": {"name": "Meat & Eggs", "name_ru": "Мясо и яйца", "icon": "🥩"},
    "dairy": {"name": "Dairy", "name_ru": "Молочка", "icon": "🥛"},
    "bakery": {"name": "Grains", "name_ru": "Крупы и хлеб", "icon": "🍞"},
    "other": {"name": "Other", "name_ru": "Другое", "icon": "🧂"},
}

# Рекомендуемые бюджеты на основе diet goal
BUDGET_SUGGESTIONS = {
    "Weight Loss": 12000,
    "Muscle Gain": 18000,
    "Healthy Lifestyle": 15000,
    "Meal Planning": 14000,
}

def get_all_products():
    """Возвращает все продукты одним списком"""
    all_products = []
    for category, products in PRODUCTS.items():
        for product in products:
            product["category"] = category
            all_products.append(product)
    return all_products

def get_product_by_id(product_id):
    """Ищет продукт по ID"""
    for products in PRODUCTS.values():
        for product in products:
            if product["id"] == product_id:
                return product
    return None

def search_products(query):
    """Поиск продуктов по названию"""
    query_lower = query.lower()
    results = []
    
    for category, products in PRODUCTS.items():
        for product in products:
            if (query_lower in product["name"].lower() or 
                query_lower in product.get("name_ru", "").lower()):
                product["category"] = category
                results.append(product)
    
    return results
