FAQ_ITEMS = [
    {
        "question": "How do I create an event?",
        "answer": "Use the Create button in the sidebar, or type a natural command in AI chat.",
        "keywords": [
            "create event",
            "add event",
            "new event",
            "schedule event",
            "создать событие",
            "добавить событие",
        ],
    },
    {
        "question": "How do I switch calendar view?",
        "answer": "Open the Calendar dropdown in the sidebar and choose Month, Week, or Day.",
        "keywords": [
            "switch view",
            "calendar view",
            "month week day",
            "change view",
            "вид календаря",
            "переключить вид",
        ],
    },
    {
        "question": "How do I add meals?",
        "answer": "Open Diet page, generate a plan, and add meals directly to your calendar.",
        "keywords": [
            "add meal",
            "meal plan",
            "diet page",
            "food calendar",
            "добавить еду",
            "план питания",
            "диета",
        ],
    },
    {
        "question": "How do I change language?",
        "answer": "Open Settings in the top-right area and select your language.",
        "keywords": [
            "change language",
            "language settings",
            "switch language",
            "изменить язык",
            "язык",
        ],
    },
    {
        "question": "How do I change theme?",
        "answer": "Click the moon/sun icon in the top bar to toggle light and dark modes.",
        "keywords": [
            "change theme",
            "dark mode",
            "light mode",
            "toggle theme",
            "тема",
            "темный режим",
            "светлый режим",
        ],
    },
]


def find_faq_answer(user_text: str):
    text = (user_text or "").strip().lower()
    if not text:
        return None

    best_item = None
    best_score = 0

    for item in FAQ_ITEMS:
        score = 0
        for keyword in item.get("keywords", []):
            keyword_l = keyword.lower()
            if keyword_l in text:
                score += 2

            keyword_words = keyword_l.split()
            if keyword_words and all(word in text for word in keyword_words):
                score += 1

        question_words = item["question"].lower().replace("?", "").split()
        overlap = sum(1 for word in question_words if len(word) > 2 and word in text)
        score += overlap

        if score > best_score:
            best_score = score
            best_item = item

    return best_item if best_score >= 2 else None
