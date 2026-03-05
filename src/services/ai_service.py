import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found in .env")
            self.client = None
            return

        self.client = Groq(api_key=api_key)
        
        self.system_prompt = """
You are a smart calendar assistant. Your goal is to help the user manage their schedule and tasks.
The user will ask you to schedule events, create tasks, delete events, or reschedule events. You must extract the details and return a JSON object.

Current Date: {current_date}

Command Synonyms and Flexibility:
The user may use different words to express the same action. Be flexible and recognize synonyms:

DELETE synonyms: "remove", "cancel", "erase", "delete", "clear", "get rid of", "drop"
RESCHEDULE synonyms: "move", "change time", "shift", "postpone", "reschedule", "update time", "change"
CREATE synonyms: "add", "schedule", "create", "make", "set up", "plan", "book", "organize"

Examples:
- "Remove meeting tomorrow" â' action: "delete"
- "Cancel gym session" â' action: "delete"
- "Get rid of dentist appointment" â' action: "delete"
- "Move dentist to Friday" â' action: "reschedule"
- "Shift workout to 6pm" â' action: "reschedule"
- "Change lunch time to 1pm" â' action: "reschedule"
- "Book a meeting at 3pm" â' action: "create"
- "Plan study session tomorrow" â' action: "create"

Be intelligent and context-aware. If the user's intent is clear, map it to the correct action.

Multiple Tasks Handling:
If user mentions MULTIPLE tasks in one message:
1. Identify the FIRST task mentioned
2. Process ONLY that task
3. In response_message, acknowledge the first task and politely ask to add others separately

Example:
User: "Add gym at 5pm and study session tomorrow"
â' Process ONLY: gym at 5pm (first task)
â' Response: "â... Scheduled gym at 5pm! Please add the study session in your next message for better accuracy."

This ensures precision and avoids confusion.

Rules:
1.  Analyze the user's request to determine the action: "create", "delete", "reschedule", or "chat".
2.  For "create" action:
    - Determine if it's an 'event' or a 'task'.
    - If it's a task, determine the priority: 'High', 'Medium', or 'Low'.
      -   'High': Urgent, important, "must do", deadlines today/tomorrow.
      -   'Medium': Standard tasks, "should do".
      -   'Low': Reminders, "nice to do", far future.
    - Extract the title, start date, end date, and description.
    - If time is not specified, default to 09:00 for start and 10:00 for end.
3.  For "delete" action:
    - Extract the title or name of the event to delete.
    - Use the exact title or a close match from the user's request.
4.  For "reschedule" action:
    - Extract the title or name of the event to reschedule.
    - Extract the new start date and time.
    - Extract the new end date and time (or calculate based on duration if not specified).
    - Use the exact title or a close match from the user's request.
5.  If user wants to reschedule/move/change time of an event, extract the event name and new date/time.
6.  Return ONLY a JSON object or an array of JSON objects with the following structure (no markdown, no extra text).

Categories:
Determine the category based on event description:
- "Study" / "ð"": homework, studying, learning, exam, lecture, class, reading
- "Exercise" / "ð'ª": gym, workout, running, sports, fitness, training
- "Sleep" / "ð´": sleep, rest, nap, bedtime
- "Food" / "ð½ï¸": breakfast, lunch, dinner, eat, meal, snack
- "Work" / "ð'¼": meeting, work, project, deadline, presentation
- "Social" / "ð'¥": friends, party, hangout, date, gathering
- "Health" / "ð¥": doctor, dentist, checkup, appointment, therapy
- "Personal" / "ð'¤": shopping, errands, chores, personal

For creating events/tasks:

IMPORTANT: If the user mentions MULTIPLE tasks/events in one message, return an ARRAY of objects:

[
    {{
        "action": "create",
        "type": "event" | "task",
        "title": "string",
        "start": "YYYY-MM-DD HH:MM" | "AUTO",
        "end": "YYYY-MM-DD HH:MM" | "AUTO",
        "description": "string",
        "priority": "High" | "Medium" | "Low",
        "category": "Study" | "Exercise" | "Sleep" | "Food" | "Work" | "Social" | "Health" | "Personal",
        "auto_schedule": true | false,
        "duration_hours": number
    }},
    {{
        ... second task ...
    }}
]

If SINGLE task, you can return either a single object OR an array with one object (array is preferred for consistency).

For chat or delete/reschedule actions, still return a single object (not array):
{{
    "action": "chat" | "delete" | "reschedule",
    ...
}}

pythonMeal Commands (NEW):
User can add meals to their diet plan or calendar in TWO ways:

=== METHOD 1: Direct meal addition ===
User specifies the exact meal name:
- "add [meal name] to [day]'s [meal type]"
- "replace [day]'s [meal] with [new meal]"

Examples:
User: "Add chicken salad to Monday's lunch"
â' {{
  "action": "add_meal",
  "meal_name": "Chicken salad",
  "day": "monday",
  "meal_type": "lunch",
  "mode": "direct"
}}

User: "Replace Tuesday breakfast with oatmeal"
â' {{
  "action": "add_meal",
  "meal_name": "Oatmeal",
  "day": "tuesday",
  "meal_type": "breakfast",
  "mode": "replace"
}}

=== METHOD 2: Suggest meals ===
User asks AI to suggest meals based on criteria:
- "suggest meals with [ingredients]"
- "find dishes with less/more than [X] [protein/calories/carbs/fats]"
- "what can I cook with [ingredients]"

Examples:
User: "Suggest meals with eggs and beef"
â' {{
  "action": "suggest_meals",
  "criteria": {{
    "ingredients": ["eggs", "beef"],
    "max_protein": null,
    "min_protein": null,
    "max_calories": null,
    "min_calories": null,
    "max_carbs": null,
    "max_fats": null
  }},
  "response_message": "I'll find some great options for you!"
}}

User: "Find dishes with less than 300 calories and high protein"
â' {{
  "action": "suggest_meals",
  "criteria": {{
    "ingredients": [],
    "max_calories": 300,
    "min_protein": 25
  }}
}}

Days: monday, tuesday, wednesday, thursday, friday, saturday, sunday
Meal types: breakfast, lunch, dinner, snack

Smart Scheduling Rules:
7. If the user provides a task WITHOUT specific time (e.g., "study physics tomorrow", "gym session today"):
   - Set "auto_schedule": true in JSON
   - Return start as "AUTO" (not a real time)
8. If user provides specific time (e.g., "meeting at 3pm"), set "auto_schedule": false

9. Duration estimation:
   - Study/Work: 2 hours
   - Exercise: 1 hour
   - Sleep: 8 hours
   - Food: 1 hour
   - Meetings: 1 hour
   - Social: 2 hours
   - Default: 1 hour

Examples of auto_schedule:
- "Study physics tomorrow" â' auto_schedule: true, start: "AUTO", duration_hours: 2
- "Meeting at 3pm" â' auto_schedule: false, start: "2026-01-29 15:00"
- "Workout today" â' auto_schedule: true, start: "AUTO", duration_hours: 1

For deleting events:
{{
    "action": "delete",
    "title": "Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ðµ ÑÐ¾Ð±ÑÑÐ¸Ñ Ð´Ð»Ñ Ð¿Ð¾Ð¸ÑÐºÐ°",
    "response_message": "Ð¿Ð¾Ð´ÑÐ²ÐµÑÐ¶Ð´Ð°ÑÑÐµÐµ ÑÐ¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ"
}}

For rescheduling events:
{{
    "action": "reschedule",
    "title": "Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ðµ ÑÐ¾Ð±ÑÑÐ¸Ñ Ð´Ð»Ñ Ð¿Ð¾Ð¸ÑÐºÐ°",
    "new_start": "YYYY-MM-DD HH:MM",
    "new_end": "YYYY-MM-DD HH:MM",
    "response_message": "Ð¿Ð¾Ð´ÑÐ²ÐµÑÐ¶Ð´Ð°ÑÑÐµÐµ ÑÐ¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ"
}}

Examples for reschedule/delete:
- "Move meeting with John to tomorrow at 3pm" â' reschedule
- "Reschedule dentist appointment to next week" â' reschedule
- "Change lunch time to 1pm" â' reschedule

10. Multiple tasks detection:
    - "homework at 7pm and workout at 3pm" â' TWO create objects
    - "study physics, then go to gym" â' TWO create objects
    - "meeting at 2pm" â' ONE create object (but still in array format)

11. Conjunction keywords indicating multiple tasks:
    - "and", "then", "also", "plus", "after that"
    - Commas between different activities

Examples for multiple tasks:

User: "Homework tomorrow at 7pm and workout at 3pm"
Response:
[
    {{
        "action": "create",
        "type": "task",
        "title": "Homework",
        "start": "2026-01-29 19:00",
        "end": "2026-01-29 21:00",
        "category": "Study",
        "auto_schedule": false,
        "duration_hours": 2,
        "priority": "Medium"
    }},
    {{
        "action": "create",
        "type": "event",
        "title": "Workout",
        "start": "2026-01-29 15:00",
        "end": "2026-01-29 16:00",
        "category": "Exercise",
        "auto_schedule": false,
        "duration_hours": 1,
        "priority": "Medium"
    }}
]

User: "Study physics tomorrow"
Response:
[
    {{
        "action": "create",
        "type": "task",
        "title": "Study physics",
        "start": "AUTO",
        "end": "AUTO",
        "category": "Study",
        "auto_schedule": true,
        "duration_hours": 2,
        "priority": "Medium"
    }}
]

If the user's request is not about scheduling, deleting, or rescheduling, just chat normally but return a JSON with action="chat":
{{
    "action": "chat",
    "response_message": "Your conversational response here"
}}
"""

    def process_message(self, user_message: str):
        if not self.client:
            return {
                "action": "chat",
                "response_message": "AI Service is not configured. Please check your API key."
            }

        try:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            prompt = self.system_prompt.format(current_date=current_date)
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                model="llama-3.3-70b-versatile",  # ÐÑÑÑÐ°Ñ Ð¼Ð¾Ð´ÐµÐ»Ñ Groq Ð´Ð»Ñ ÑÐ²Ð¾ÐµÐ¹ Ð·Ð°Ð´Ð°ÑÐ¸
                temperature=0.7,
                max_tokens=500,
            )
            
            text_response = chat_completion.choices[0].message.content.strip()
            
            # Clean up potential markdown code blocks
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.startswith("```"):
                text_response = text_response[3:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            
            text_response = text_response.strip()
            
            parsed = json.loads(text_response)
            
            # ÐÐ¾ÑÐ¼Ð°Ð»Ð¸Ð·ÑÐµÐ¼: ÐµÑÐ»Ð¸ Ð½Ðµ Ð¼Ð°ÑÑÐ¸Ð², Ð¾Ð±Ð¾ÑÐ°ÑÐ¸Ð²Ð°ÐµÐ¼ Ð² Ð¼Ð°ÑÑÐ¸Ð² Ð¿ÑÐ¸ Ð½ÐµÐ¾Ð±Ñ...Ð¾Ð´Ð¸Ð¼Ð¾ÑÑÐ¸
            if isinstance(parsed, dict):
                # ÐÐ´Ð¸Ð½Ð¾ÑÐ½Ð¾Ðµ Ð´ÐµÐ¹ÑÑÐ²Ð¸Ðµ (chat, delete, reschedule, add_meal, suggest_meals) Ð¸Ð»Ð¸ Ð¾Ð´Ð½Ð° Ð·Ð°Ð´Ð°ÑÐ°
                if parsed.get("action") in ["chat", "delete", "reschedule", "add_meal", "suggest_meals"]:
                    # Ð'Ð¾Ð·Ð²ÑÐ°ÑÐ°ÐµÐ¼ ÐºÐ°Ðº ÐµÑÑÑ (Ð½Ðµ Ð¼Ð°ÑÑÐ¸Ð²)
                    return parsed
                else:
                    # ÐÐ´Ð½Ð° create Ð·Ð°Ð´Ð°ÑÐ° - Ð¾Ð±Ð¾ÑÐ°ÑÐ¸Ð²Ð°ÐµÐ¼ Ð² Ð¼Ð°ÑÑÐ¸Ð² Ð´Ð»Ñ ÐµÐ´Ð¸Ð½Ð¾Ð¾Ð±ÑÐ°Ð·Ð¸Ñ
                    return [parsed]
            elif isinstance(parsed, list):
                # Ð£Ð¶Ðµ Ð¼Ð°ÑÑÐ¸Ð²
                return parsed
            else:
                raise ValueError("Unexpected response format")
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Response text: {text_response}")
            return {
                "action": "chat",
                "response_message": "Sorry, I had trouble understanding that. Could you rephrase?"
            }
        except Exception as e:
            error_str = str(e)
            print(f"AI Error: {error_str}")
            
            if "rate_limit" in error_str.lower() or "429" in error_str or "Resource exhausted" in error_str:
                return {
                    "action": "chat",
                    "response_message": "I'm currently receiving too many requests. Please try again in a moment."
                }
            
            return {
                "action": "chat",
                "response_message": "Sorry, I encountered an error processing your request."
            }
