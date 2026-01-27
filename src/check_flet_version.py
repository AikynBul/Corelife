import flet as ft

def main(page: ft.Page):
    if hasattr(page, "open"):
        print("page.open exists")
    else:
        print("page.open does NOT exist")

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN)
