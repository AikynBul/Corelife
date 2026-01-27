import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in .env")
            self.model = None
            return

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        self.system_prompt = """
You are a smart calendar assistant. Your goal is to help the user manage their schedule and tasks.
The user will ask you to schedule events or tasks. You must extract the details and return a JSON object.

Current Date: {current_date}

Rules:
1.  Analyze the user's request to determine if it's an 'event' or a 'task'.
2.  If it's a task, determine the priority: 'High', 'Medium', or 'Low'.
    -   'High': Urgent, important, "must do", deadlines today/tomorrow.
    -   'Medium': Standard tasks, "should do".
    -   'Low': Reminders, "nice to do", far future.
3.  Extract the title, start date, end date, and description.
4.  If time is not specified, default to 09:00 for start and 10:00 for end.
5.  Return ONLY a JSON object with the following structure (no markdown, no extra text):

{{
    "action": "create",
    "type": "event" | "task",
    "title": "string",
    "start": "YYYY-MM-DD HH:MM",
    "end": "YYYY-MM-DD HH:MM",
    "description": "string",
    "priority": "High" | "Medium" | "Low",
    "response_message": "A friendly confirmation message to show the user"
}}

If the user's request is not about scheduling, just chat normally but return a JSON with action="chat":
{{
    "action": "chat",
    "response_message": "Your conversational response here"
}}
"""

    def process_message(self, user_message: str):
        if not self.model:
            return {
                "action": "chat",
                "response_message": "AI Service is not configured. Please check your API key."
            }

        try:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            prompt = self.system_prompt.format(current_date=current_date)
            
            chat = self.model.start_chat(history=[])
            response = chat.send_message(f"{prompt}\n\nUser: {user_message}")
            
            text_response = response.text.strip()
            
            # Clean up potential markdown code blocks
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.startswith("```"):
                text_response = text_response[3:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            
            return json.loads(text_response.strip())
            
        except Exception as e:
            error_str = str(e)
            print(f"AI Error: {error_str}")
            
            if "429" in error_str or "Resource exhausted" in error_str:
                return {
                    "action": "chat",
                    "response_message": "I'm currently receiving too many requests. Please try again in a minute."
                }
            
            return {
                "action": "chat",
                "response_message": "Sorry, I encountered an error processing your request."
            }
