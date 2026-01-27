import flet as ft
from components.layout import AppLayout
from components.header import Header
from components.chat import ChatWidget

def main(page: ft.Page):
    page.title = "Test Full App"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Initialize the main layout
    page.appbar = Header(page)
    app_layout = AppLayout(page)
    
    # Use Stack to overlay ChatWidget
    main_stack = ft.Stack(
        [
            app_layout,
            ft.Container(
                content=ChatWidget(page, on_refresh=app_layout.refresh_active_view),
                right=20,
                bottom=20,
            )
        ],
        expand=True
    )
    
    page.add(main_stack)
    
    # Simulate clicking the create button
    print("Simulating Create button click...")
    sidebar = app_layout.sidebar
    
    # Create a dummy event
    e = ft.ControlEvent(
        target="test",
        name="click",
        data="",
        control=sidebar.build_create_button(),
        page=page
    )
    
    sidebar.open_create_dialog(e)
    
    # Check if dialog is in overlay
    dialog = None
    if page.overlay:
        for control in page.overlay:
            if isinstance(control, ft.AlertDialog) and control.open:
                dialog = control
                break
    
    if dialog:
        print("Dialog opened successfully in full app context")
        
        # Check if DatePicker is in overlay
        found_picker = False
        if page.overlay:
            for control in page.overlay:
                if isinstance(control, ft.DatePicker):
                    found_picker = True
                    break
        
        if found_picker:
            print("DatePicker found in overlay")
        else:
            print("DatePicker NOT found in overlay")
            
        # Close dialog
        dialog.close_dialog(None)
        
    else:
        print("Error: Dialog did not open in full app context")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN)
