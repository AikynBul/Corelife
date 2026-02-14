# Corelife
Corelife project repository
✨ Features
📅 Smart Calendar

Multiple Views: Month, Week, and Day views
AI-Powered Scheduling: Natural language event creation ("Plan a meeting tomorrow at 3pm")
Smart Time Slots: Automatic optimal time detection based on event category
10 Event Categories: Study 📚, Exercise 💪, Sleep 😴, Food 🍽️, Work 💼, Social 👥, Health 🏥, Personal 👤, Entertainment 🎮, Routine 🔄
4 Priority Levels: Critical 🔴, High 🔥, Medium ⚡, Low ✨
Color-Coded Events: Visual categorization across all calendar views
Overlapping Events: Side-by-side display for simultaneous events

🍽️ Meal Planning

AI Diet Generation: Personalized weekly meal plans based on your goals
4 Diet Goals: Weight Loss, Muscle Gain, Healthy Lifestyle, Meal Planning
Nutritional Analysis: Automatic macros (calories, protein, carbs, fats) calculation
Meal Suggestions: AI-powered recommendations based on ingredients or nutritional criteria
Calendar Integration: Add meals to your schedule with one click

🤖 AI Chat Assistant

Natural Language Processing: Talk to your calendar like a human
Smart Commands:

Create: "Add meeting at 3pm tomorrow"
Delete: "Cancel gym session"
Reschedule: "Move dentist to Friday"
Meal Analysis: "Add chicken salad to Monday's lunch"
Meal Suggestions: "Find dishes with eggs and beef"



📊 Analytics

Weekly Nutrition Stats: Average daily calories, protein, carbs, and fats
Visual Insights: Color-coded cards for macros tracking


🚀 Quick Start
Prerequisites

Python 3.11 or higher
MongoDB (local or cloud)
Groq API key (Get one for free)

Installation

Clone the repository

bashgit clone https://github.com/yourusername/corelife.git
cd corelife

Create virtual environment

bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies

bashpip install -r requirements.txt

Set up environment variables

Create a .env file in the root directory:
envGROQ_API_KEY=your_groq_api_key_here
MONGO_URI=mongodb://localhost:27017/  # or your MongoDB Atlas URI

Run the app

bashpython src/main.py

📖 User Guide
Creating Events
Method 1: AI Chat
Just type naturally:

"Schedule meeting at 3pm"
"Add gym session tomorrow"
"Plan study time this evening"

The AI will automatically:

Detect the event type and category
Set optimal time slots
Assign appropriate priority

Method 2: Create Button
Click the Create button in the sidebar:

Enter event title
Choose date and time
Select category (Study, Exercise, etc.)
Set priority level
Add description (optional)
Save

Managing Meals
Generate Weekly Plan

Go to Diet page
Set your diet goal (Weight Loss, Muscle Gain, etc.)
Specify preferences (meals per day, dietary restrictions)
Click Generate Meal Plan
Wait 5-10 seconds for AI to create your personalized plan

Add Meals to Calendar
Method 1: Add entire week

Click Add All to Calendar button

Method 2: Add individual meals

Click 📅 button next to any meal
Choose date and time
Confirm

Method 3: AI Chat

"Add chicken salad to Monday's lunch"
"Suggest meals with eggs and beef"

Navigation

Sidebar: Switch between Month/Week/Day views
Mini Calendar: Click any date to jump to Day view
View Filters: Toggle Events/Tasks visibility
Diet Page: Manage meal plans and nutrition goals
Account: View profile and settings


🎨 Color System
Events are color-coded by category:
CategoryColorIconBest TimeRoutineGray🔄7:00-22:00SleepIndigo😴22:00-7:00FoodOrange🍽️8:00-20:00StudyBlue📚17:00-21:00ExerciseGreen💪14:00-18:00WorkBlue-Grey💼9:00-17:00SocialPink👥18:00-22:00HealthRed🏥9:00-18:00PersonalPurple👤8:00-22:00EntertainmentCyan🎮19:00-23:00

🔧 Configuration
Diet Preferences

Diet Goal: Weight Loss, Muscle Gain, Healthy Lifestyle, Meal Planning
Meals Per Day: 2, 3, or 4 meals
Daily Calorie Target: Customizable
Medical Restrictions: Allergies, intolerances

Calendar Settings

First Day of Week: Monday (default)
View Filters: Show/hide Events and Tasks
Time Format: 24-hour clock


🤝 Contributing
We welcome contributions! Here's how:

Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request


📝 Architecture
Corelife/
├── src/
│   ├── main.py                 # Entry point
│   ├── components/             # UI components
│   │   ├── calendar.py        # Month view
│   │   ├── day_view.py        # Day view with timeline
│   │   ├── week_view.py       # Week view
│   │   ├── sidebar.py         # Navigation sidebar
│   │   ├── chat.py            # AI chat interface
│   │   ├── diet_view.py       # Meal planning
│   │   └── event_dialog.py    # Event creation/edit
│   ├── services/               # AI & Data services
│   │   ├── ai_service.py      # Calendar AI (Groq)
│   │   ├── meal_nutrition_ai.py  # Meal analysis AI
│   │   └── diet_ai_service.py    # Diet plan generation
│   ├── data/
│   │   ├── store.py           # MongoDB storage
│   │   └── event_categories.py   # Category system
│   └── utils/
│       └── translations.py    # Localization
└── .env                        # Environment variables

🌟 Technologies

UI Framework: Flet - Python-powered Flutter apps
Database: MongoDB - NoSQL document storage
AI: Groq - Ultra-fast LLM inference (llama-3.3-70b)
Language: Python 3.11+


📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

Flet team for the amazing UI framework
Groq for blazing-fast AI inference
MongoDB for reliable data storage
Everyone who contributed to this project