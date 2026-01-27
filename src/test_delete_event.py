import flet as ft
from components.calendar import MonthView
from components.event_details_dialog import EventDetailsDialog
from data.store import store
import datetime

def main(page: ft.Page):
    page.title = "Test Delete Event"
    
    # Add a dummy event to store
    print("Adding dummy event...")
    event = store.add_event(
        title="Event to Delete",
        start_date=datetime.date.today().isoformat(),
        end_date=datetime.date.today().isoformat(),
        description="This event should be deleted",
        event_type="event"
    )
    event_id = event["id"]
    print(f"Event added with ID: {event_id}")
    
    # Initialize calendar
    calendar = MonthView()
    page.add(calendar)
    
    # Simulate opening details dialog
    print("Opening event details dialog...")
    # We can't easily click the calendar item, so we call open_event_details directly
    calendar.open_event_details(event)
    
    # Check if dialog is open
    dialog = None
    if page.overlay:
        for control in page.overlay:
            if isinstance(control, EventDetailsDialog) and control.open:
                dialog = control
                break
                
    if dialog:
        print("Dialog opened successfully")
        
        # Simulate clicking delete
        print("Deleting event...")
        dialog.delete_event(None)
        
        # Check if dialog is closed
        if not dialog.open:
            print("Dialog closed successfully")
        else:
            print("Error: Dialog did not close")
            
        # Check if event is removed from store
        remaining_events = [e for e in store.events if e["id"] == event_id]
        if not remaining_events:
            print("Event removed from store successfully")
        else:
            print("Error: Event still exists in store")
            
    else:
        print("Error: Dialog did not open")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN)
