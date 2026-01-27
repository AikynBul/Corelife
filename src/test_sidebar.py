import flet as ft
from components.sidebar import Sidebar

def main(page: ft.Page):
    try:
        print("Initializing Sidebar...")
        sidebar = Sidebar()
        print("Sidebar initialized.")
        page.add(sidebar)
        print("Sidebar added to page.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN)
