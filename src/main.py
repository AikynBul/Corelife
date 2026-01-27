import flet as ft
from components.layout import AppLayout
from components.header import Header
from components.chat import ChatWidget
from components.login_view import LoginView
from utils.translations import translations
from data.store import store

def main(page: ft.Page):
    page.title = "AI Calendar"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Load saved language preference
    saved_language = page.client_storage.get("language")
    if saved_language:
        translations.set_language(saved_language)
    
    # Set Google Calendar-like colors
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    def on_login(user_info):
        # Set user in store
        store.set_user(user_info["id"])
        page.clean()
        try:
            show_app(user_info)
        except Exception as e:
            import traceback
            page.add(
                ft.Column([
                    ft.Text("An error occurred:", color=ft.Colors.RED, size=20),
                    ft.Text(str(e), color=ft.Colors.RED),
                    ft.Text(traceback.format_exc(), color=ft.Colors.RED, font_family="Consolas")
                ], scroll=ft.ScrollMode.AUTO)
            )
            page.update()

    def on_logout(e):
        # Clear user from store
        store.set_user(None)
        page.clean()
        page.appbar = None
        show_login()

    def show_login():
        page.appbar = None
        login_view = LoginView(on_login=on_login)
        page.add(login_view)
        page.update()

    def refresh_ui():
        """Refresh all UI components when language changes"""
        page.clean()
        # Get current user info if available
        if hasattr(page, 'current_user_info'):
            show_app(page.current_user_info)
        else:
            show_login()

    def show_app(user_info):
        # Store user info for language change refresh
        page.current_user_info = user_info
        
        # Initialize the main layout
        app_layout = AppLayout(page, user_info, on_logout)
        
        # Header needs to know about account click to switch view
        def on_account_click():
            app_layout.set_view("Account")

        def on_language_change():
            """Handle language change - refresh entire UI"""
            refresh_ui()

        def on_menu_click(e):
            """Handle menu button click to toggle sidebar"""
            app_layout.toggle_sidebar()

        page.appbar = Header(
            page, 
            on_account_click, 
            on_language_change=on_language_change, 
            on_menu_click=on_menu_click,
            on_theme_change=on_language_change # Reuse refresh_ui for theme change
        )
        
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
        page.update()

    # Start with login
    show_login()

if __name__ == "__main__":
    ft.app(target=main)
