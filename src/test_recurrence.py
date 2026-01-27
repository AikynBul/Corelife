import flet as ft
from data.store import store
import datetime
import calendar

def main(page: ft.Page):
    page.title = "Test Recurrence"
    
    # Clear existing events for clean test
    store.events = []
    store.save_events()
    
    today = datetime.date.today()
    
    print(f"Today is: {today}")
    
    # 1. Daily Event
    print("\n--- Testing Daily Event ---")
    store.add_event(
        title="Daily Standup",
        start_date=today.isoformat(),
        end_date=today.isoformat(),
        description="Daily meeting",
        recurrence="daily"
    )
    
    # Check next month
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year if today.month < 12 else today.year + 1
    
    events = store.get_events_for_month(next_year, next_month)
    daily_events = [e for e in events if e["title"] == "Daily Standup"]
    
    _, num_days = calendar.monthrange(next_year, next_month)
    print(f"Next month ({next_month}/{next_year}) has {num_days} days.")
    print(f"Found {len(daily_events)} occurrences of Daily Standup.")
    
    if len(daily_events) == num_days:
        print("PASS: Daily event appears every day.")
    else:
        print(f"FAIL: Expected {num_days}, got {len(daily_events)}")

    # 2. Workdays Event
    print("\n--- Testing Workdays Event ---")
    store.add_event(
        title="Work Sync",
        start_date=today.isoformat(),
        end_date=today.isoformat(),
        description="Workdays only",
        recurrence="workdays"
    )
    
    events = store.get_events_for_month(next_year, next_month)
    work_events = [e for e in events if e["title"] == "Work Sync"]
    
    # Calculate expected workdays
    expected_workdays = 0
    for day in range(1, num_days + 1):
        if datetime.date(next_year, next_month, day).weekday() < 5:
            expected_workdays += 1
            
    print(f"Expected workdays: {expected_workdays}")
    print(f"Found occurrences: {len(work_events)}")
    
    if len(work_events) == expected_workdays:
        print("PASS: Workdays event appears correctly.")
    else:
        print(f"FAIL: Expected {expected_workdays}, got {len(work_events)}")

    # 3. Monthly Event
    print("\n--- Testing Monthly Event ---")
    # Set start date to 15th of this month to ensure it exists in next month (unless Feb has < 29 days and today is 30th, edge case ignored for simple test)
    test_date = today.replace(day=15)
    store.add_event(
        title="Monthly Bill",
        start_date=test_date.isoformat(),
        end_date=test_date.isoformat(),
        description="Pay bill",
        recurrence="monthly"
    )
    
    events = store.get_events_for_month(next_year, next_month)
    monthly_events = [e for e in events if e["title"] == "Monthly Bill"]
    
    print(f"Found {len(monthly_events)} occurrences of Monthly Bill.")
    if len(monthly_events) == 1:
        target_date = datetime.date(next_year, next_month, 15)
        if monthly_events[0]["start"] == target_date.isoformat():
             print("PASS: Monthly event appears on correct day.")
        else:
             print(f"FAIL: Wrong date. Expected {target_date}, got {monthly_events[0]['start']}")
    else:
        print(f"FAIL: Expected 1, got {len(monthly_events)}")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN)
