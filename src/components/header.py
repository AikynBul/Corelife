import flet as ft

class Header(ft.AppBar):
    def __init__(self, page: ft.Page, on_account_click, on_language_change=None, on_menu_click=None, on_theme_change=None):
        super().__init__()
        self.page_ref = page
        self.on_account_click = on_account_click
        self.on_language_change = on_language_change
        self.on_theme_change = on_theme_change
        self.leading = ft.IconButton(ft.Icons.MENU, on_click=on_menu_click)
        self.leading_width = 40
        self.title = ft.Text("Calendar", weight=ft.FontWeight.BOLD, size=22)
        self.center_title = False
        self.bgcolor = ft.Colors.SURFACE
        self.actions = [
            ft.IconButton(ft.Icons.SEARCH, on_click=self.show_search, tooltip="Search"),
            ft.IconButton(ft.Icons.HELP_OUTLINE, on_click=self.show_help, tooltip="Help"),
            ft.IconButton(
                icon=ft.Icons.DARK_MODE_OUTLINED,
                selected_icon=ft.Icons.LIGHT_MODE_OUTLINED,
                on_click=self.toggle_theme,
                tooltip="Toggle Theme"
            ),
            ft.IconButton(ft.Icons.SETTINGS, on_click=self.show_settings, tooltip="Settings"),
            ft.Container(width=10),
            ft.GestureDetector(
                on_tap=self.on_account_tap,
                content=ft.CircleAvatar(
                    content=ft.Text("A"),
                    bgcolor=ft.Colors.BLUE_200,
                    radius=16
                )
            ),
            ft.Container(width=10),
        ]

    def on_account_tap(self, e):
        if self.on_account_click:
            self.on_account_click()

    def toggle_theme(self, e):
        e.control.selected = not e.control.selected
        self.page_ref.theme_mode = ft.ThemeMode.DARK if e.control.selected else ft.ThemeMode.LIGHT
        self.page_ref.update()
        e.control.update()
        if self.on_theme_change:
            self.on_theme_change()

    def show_search(self, e):
        # Simple search dialog placeholder
        dialog = ft.AlertDialog(
            title=ft.Text("Search"),
            content=ft.Text("Search functionality coming soon!"),
        )
        self.page_ref.open(dialog)

    def show_help(self, e):
        dialog = ft.AlertDialog(
            title=ft.Text("Help"),
            content=ft.Text("Use the sidebar to switch views.\nClick '+' to add events.\nUse the chat to ask the AI to schedule things."),
        )
        self.page_ref.open(dialog)

    def show_settings(self, e):
        from utils.translations import translations
        
        def change_language(e):
            lang_code = e.control.value
            translations.set_language(lang_code)
            self.page_ref.client_storage.set("language", lang_code)
            if self.on_language_change:
                self.on_language_change()
            self.page_ref.close(dialog)

        lang_dropdown = ft.Dropdown(
            label="Language",
            value=translations.current_language,
            options=[
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("ru", "Russian"),
            ],
            on_change=change_language
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Settings"),
            content=ft.Column([
                ft.Text("Version: 1.0.0"),
                ft.Container(height=10),
                lang_dropdown
            ], tight=True, width=300),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.page_ref.close(dialog))
            ]
        )
        self.page_ref.open(dialog)
