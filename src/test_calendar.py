import flet as ft
from components.calendar import MonthView

def main(page: ft.Page):
    try:
        print("Initializing MonthView...")
        calendar = MonthView()
        print("MonthView initialized.")
        page.add(calendar)
        print("MonthView added to page.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN)
