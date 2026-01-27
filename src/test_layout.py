import flet as ft
from components.layout import AppLayout

def main(page: ft.Page):
    try:
        print("Initializing AppLayout...")
        layout = AppLayout(page)
        print("AppLayout initialized.")
        page.add(layout)
        print("AppLayout added to page.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN)
