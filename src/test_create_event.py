import flet as ft
from components.sidebar import Sidebar
from components.event_dialog import EventDialog
from data.store import store
import os

def main(page: ft.Page):
    page.title = "Test Create Event"
    
    def on_refresh():
        print("Refresh called")
        # Check if event was added to store
        print(f"Events in store: {len(store.events)}")
        if len(store.events) > 0:
            print(f"Last event: {store.events[-1]}")

    sidebar = Sidebar(on_refresh=on_refresh)
    
    page.add(sidebar)
    
    # Simulate clicking the create button
    # We can't easily simulate click in this script without running the UI, 
    # but we can verify the open_create_dialog method works.
    
    print("Opening create dialog...")
    # Create a dummy event
    e = ft.ControlEvent(
        target="test",
        name="click",
        data="",
        control=sidebar.build_create_button(),
        page=page
    )
    
    sidebar.open_create_dialog(e)
    
    # Check if dialog is in overlay (since we use page.open)
    # Note: page.open adds to page.overlay or similar
    # We can check if any AlertDialog is open
    
    print("Checking for open dialog...")
    # In Flet, page.open might not immediately add to overlay list in a way we can easily check synchronously without update?
    # But let's try to find it in overlay
    
    dialog = None
    if page.overlay:
        for control in page.overlay:
            if isinstance(control, ft.AlertDialog) and control.open:
                dialog = control
                break
                
    if dialog:
        print("Dialog opened successfully")
        
        # Simulate filling the form and saving
        dialog.title_field.value = "Test Event"
        dialog.description_field.value = "This is a test event"
        
        print("Saving event...")
        dialog.save_event(None)
        
        if not dialog.open:
            print("Dialog closed successfully")
        else:
            print("Error: Dialog did not close")
            
    else:
        # Fallback check if page.dialog is set (old way)
        if page.dialog and page.dialog.open:
             print("Dialog opened via page.dialog (unexpected but working)")
        else:
             print("Error: Dialog did not open")

if __name__ == "__main__":
    # Ensure we don't overwrite actual data, maybe mock store?
    # For now, we'll just use the actual store but print what happens.
    # We should probably backup events.json if it exists.
    if os.path.exists("events.json"):
        os.rename("events.json", "events.json.bak")
        
    try:
        ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN)
    finally:
        if os.path.exists("events.json.bak"):
            if os.path.exists("events.json"):
                os.remove("events.json")
            os.rename("events.json.bak", "events.json")
