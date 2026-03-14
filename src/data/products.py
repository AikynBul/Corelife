"""
Р‘Р°Р·Р° РґР°РЅРЅС‹С… РїСЂРѕРґСѓРєС‚РѕРІ РґР»СЏ Grocery Store
Р¦РµРЅС‹ РѕСЃРЅРѕРІР°РЅС‹ РЅР° Small marketplace (Semey, Kazakhstan)
Р’СЃРµ С†РµРЅС‹ РІ С‚РµРЅРіРµ (в‚ё)
"""

PRODUCTS = {
    "fruits": [
        {"id": "apple", "name": "Apples", "name_ru": "РЇР±Р»РѕРєРё", "unit": "1 kg", "price": 800, "icon": "\U0001F34E"},
        {"id": "banana", "name": "Bananas", "name_ru": "Р‘Р°РЅР°РЅС‹", "unit": "1 kg", "price": 600, "icon": "\U0001F34C"},
        {"id": "orange", "name": "Oranges", "name_ru": "РђРїРµР»СЊСЃРёРЅС‹", "unit": "1 kg", "price": 700, "icon": "\U0001F34A"},
        {"id": "grape", "name": "Grapes", "name_ru": "Р’РёРЅРѕРіСЂР°Рґ", "unit": "1 kg", "price": 1200, "icon": "\U0001F347"},
        {"id": "watermelon", "name": "Watermelon", "name_ru": "РђСЂР±СѓР·", "unit": "1 kg", "price": 300, "icon": "\U0001F349"},
    ],
    
    "vegetables": [
        {"id": "potato", "name": "Potatoes", "name_ru": "РљР°СЂС‚РѕС„РµР»СЊ", "unit": "1 kg", "price": 200, "icon": "\U0001F954"},
        {"id": "carrot", "name": "Carrots", "name_ru": "РњРѕСЂРєРѕРІСЊ", "unit": "1 kg", "price": 250, "icon": "\U0001F955"},
        {"id": "onion", "name": "Onions", "name_ru": "Р›СѓРє", "unit": "1 kg", "price": 180, "icon": "\U0001F9C5"},
        {"id": "tomato", "name": "Tomatoes", "name_ru": "РџРѕРјРёРґРѕСЂС‹", "unit": "1 kg", "price": 600, "icon": "\U0001F345"},
        {"id": "cucumber", "name": "Cucumbers", "name_ru": "РћРіСѓСЂС†С‹", "unit": "1 kg", "price": 500, "icon": "\U0001F952"},
        {"id": "pepper", "name": "Bell Pepper", "name_ru": "РџРµСЂРµС†", "unit": "1 kg", "price": 800, "icon": "\U0001F336\uFE0F"},
        {"id": "cabbage", "name": "Cabbage", "name_ru": "РљР°РїСѓСЃС‚Р°", "unit": "1 kg", "price": 150, "icon": "\U0001F96C"},
    ],
    
    "meat": [
        {"id": "chicken_breast", "name": "Chicken Breast", "name_ru": "РљСѓСЂРёРЅР°СЏ РіСЂСѓРґРєР°", "unit": "1 kg", "price": 2500, "icon": "\U0001F414"},
        {"id": "chicken_legs", "name": "Chicken Legs", "name_ru": "РљСѓСЂРёРЅС‹Рµ РЅРѕР¶РєРё", "unit": "1 kg", "price": 1800, "icon": "\U0001F357"},
        {"id": "beef", "name": "Beef", "name_ru": "Р“РѕРІСЏРґРёРЅР°", "unit": "1 kg", "price": 3500, "icon": "\U0001F969"},
        {"id": "pork", "name": "Pork", "name_ru": "РЎРІРёРЅРёРЅР°", "unit": "1 kg", "price": 2800, "icon": "\U0001F953"},
        {"id": "minced_meat", "name": "Minced Meat", "name_ru": "Р¤Р°СЂС€", "unit": "1 kg", "price": 2200, "icon": "\U0001F969"},
        {"id": "eggs", "name": "Eggs", "name_ru": "РЇР№С†Р°", "unit": "10 pcs", "price": 400, "icon": "\U0001F95A"},
        {"id": "turkey_breast", "name": "Turkey Breast", "name_ru": "Turkey Breast", "unit": "1 kg", "price": 2800, "icon": "\U0001F357"},
        {"id": "salmon", "name": "Salmon", "name_ru": "Salmon", "unit": "1 kg", "price": 4500, "icon": "\U0001F41F"},
        {"id": "tuna", "name": "Tuna", "name_ru": "Tuna", "unit": "500 g", "price": 1500, "icon": "\U0001F41F"},
        {"id": "protein_powder", "name": "Protein Powder", "name_ru": "Protein Powder", "unit": "1 kg", "price": 5000, "icon": "\U0001F964"},
    ],
    
    "dairy": [
        {"id": "milk", "name": "Milk", "name_ru": "РњРѕР»РѕРєРѕ", "unit": "1 L", "price": 350, "icon": "\U0001F95B"},
        {"id": "cheese", "name": "Cheese", "name_ru": "РЎС‹СЂ", "unit": "500 g", "price": 1200, "icon": "\U0001F9C0"},
        {"id": "cottage_cheese", "name": "Cottage Cheese", "name_ru": "РўРІРѕСЂРѕРі", "unit": "500 g", "price": 500, "icon": "\U0001F9C0"},
        {"id": "yogurt", "name": "Yogurt", "name_ru": "Р™РѕРіСѓСЂС‚", "unit": "500 g", "price": 400, "icon": "\U0001F368"},
        {"id": "butter", "name": "Butter", "name_ru": "РЎР»РёРІРѕС‡РЅРѕРµ РјР°СЃР»Рѕ", "unit": "200 g", "price": 600, "icon": "\U0001F9C8"},
        {"id": "sour_cream", "name": "Sour Cream", "name_ru": "РЎРјРµС‚Р°РЅР°", "unit": "500 g", "price": 450, "icon": "\U0001F95B"},
        {"id": "greek_yogurt", "name": "Greek Yogurt", "name_ru": "Greek Yogurt", "unit": "500 g", "price": 600, "icon": "\U0001F95B"},
        {"id": "protein_yogurt", "name": "High-Protein Yogurt", "name_ru": "Protein Yogurt", "unit": "500 g", "price": 700, "icon": "\U0001F95B"},
    ],
    
    "bakery": [
        {"id": "bread", "name": "White Bread", "name_ru": "Р‘РµР»С‹Р№ С…Р»РµР±", "unit": "1 loaf", "price": 200, "icon": "\U0001F35E"},
        {"id": "black_bread", "name": "Black Bread", "name_ru": "Р§С‘СЂРЅС‹Р№ С…Р»РµР±", "unit": "1 loaf", "price": 180, "icon": "\U0001F35E"},
        {"id": "pasta", "name": "Pasta", "name_ru": "РњР°РєР°СЂРѕРЅС‹", "unit": "500 g", "price": 300, "icon": "\U0001F35D"},
        {"id": "rice", "name": "Rice", "name_ru": "Р РёСЃ", "unit": "1 kg", "price": 400, "icon": "\U0001F35A"},
        {"id": "buckwheat", "name": "Buckwheat", "name_ru": "Р“СЂРµС‡РєР°", "unit": "1 kg", "price": 450, "icon": "\U0001F33E"},
        {"id": "flour", "name": "Flour", "name_ru": "РњСѓРєР°", "unit": "1 kg", "price": 250, "icon": "\U0001F32B\uFE0F"},
        {"id": "brown_rice", "name": "Brown Rice", "name_ru": "Brown Rice", "unit": "1 kg", "price": 500, "icon": "\U0001F35A"},
        {"id": "quinoa", "name": "Quinoa", "name_ru": "Quinoa", "unit": "500 g", "price": 800, "icon": "\U0001F33E"},
        {"id": "oats", "name": "Oats", "name_ru": "Oats", "unit": "1 kg", "price": 350, "icon": "\U0001F963"},
        {"id": "sweet_potato", "name": "Sweet Potato", "name_ru": "Sweet Potato", "unit": "1 kg", "price": 600, "icon": "\U0001F360"},
    ],
    
    "other": [
        {"id": "sunflower_oil", "name": "Sunflower Oil", "name_ru": "РџРѕРґСЃРѕР»РЅРµС‡РЅРѕРµ РјР°СЃР»Рѕ", "unit": "1 L", "price": 800, "icon": "\U0001F33B"},
        {"id": "olive_oil", "name": "Olive Oil", "name_ru": "РћР»РёРІРєРѕРІРѕРµ РјР°СЃР»Рѕ", "unit": "500 ml", "price": 1500, "icon": "\U0001F376"},
        {"id": "salt", "name": "Salt", "name_ru": "РЎРѕР»СЊ", "unit": "500 g", "price": 100, "icon": "\U0001F9C2"},
        {"id": "sugar", "name": "Sugar", "name_ru": "РЎР°С…Р°СЂ", "unit": "1 kg", "price": 300, "icon": "\U0001F36C"},
        {"id": "tea", "name": "Tea", "name_ru": "Р§Р°Р№", "unit": "100 g", "price": 500, "icon": "\U0001F375"},
        {"id": "coffee", "name": "Coffee", "name_ru": "РљРѕС„Рµ", "unit": "200 g", "price": 1200, "icon": "\u2615"},
    ]
}

# РљР°С‚РµРіРѕСЂРёРё РґР»СЏ UI
CATEGORIES = {
    "fruits": {"name": "Fruits", "name_ru": "Р¤СЂСѓРєС‚С‹", "icon": "\U0001F34E"},
    "vegetables": {"name": "Vegetables", "name_ru": "РћРІРѕС‰Рё", "icon": "\U0001F966"},
    "meat": {"name": "Meat & Eggs", "name_ru": "РњСЏСЃРѕ Рё СЏР№С†Р°", "icon": "\U0001F969"},
    "dairy": {"name": "Dairy", "name_ru": "РњРѕР»РѕС‡РєР°", "icon": "\U0001F95B"},
    "bakery": {"name": "Grains", "name_ru": "РљСЂСѓРїС‹ Рё С…Р»РµР±", "icon": "\U0001F35E"},
    "other": {"name": "Other", "name_ru": "Р”СЂСѓРіРѕРµ", "icon": "\U0001F9C2"},
}

# Р РµРєРѕРјРµРЅРґСѓРµРјС‹Рµ Р±СЋРґР¶РµС‚С‹ РЅР° РѕСЃРЅРѕРІРµ diet goal
BUDGET_SUGGESTIONS = {
    "Weight Loss": 12000,
    "Muscle Gain": 18000,
    "Healthy Lifestyle": 15000,
    "Meal Planning": 14000,
}

def get_all_products():
    """Р’РѕР·РІСЂР°С‰Р°РµС‚ РІСЃРµ РїСЂРѕРґСѓРєС‚С‹ РѕРґРЅРёРј СЃРїРёСЃРєРѕРј"""
    all_products = []
    for category, products in PRODUCTS.items():
        for product in products:
            product["category"] = category
            all_products.append(product)
    return all_products

def get_product_by_id(product_id):
    """РС‰РµС‚ РїСЂРѕРґСѓРєС‚ РїРѕ ID"""
    for products in PRODUCTS.values():
        for product in products:
            if product["id"] == product_id:
                return product
    return None

def search_products(query):
    """РџРѕРёСЃРє РїСЂРѕРґСѓРєС‚РѕРІ РїРѕ РЅР°Р·РІР°РЅРёСЋ"""
    query_lower = query.lower()
    results = []
    
    for category, products in PRODUCTS.items():
        for product in products:
            if (query_lower in product["name"].lower() or 
                query_lower in product.get("name_ru", "").lower()):
                product["category"] = category
                results.append(product)
    
    return results
