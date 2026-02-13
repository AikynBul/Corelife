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
        self.title = ft.Text("Corelife", weight=ft.FontWeight.BOLD, size=22)  # ✅ Изменено с Calendar на Corelife
        self.center_title = False
        self.bgcolor = ft.Colors.SURFACE
        
        # Создаем кнопку темы и сохраняем ссылку ✅
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE_OUTLINED,
            selected_icon=ft.Icons.LIGHT_MODE_OUTLINED,
            on_click=self.toggle_theme,
            tooltip="Toggle Theme"
        )
        
        self.actions = [
            ft.IconButton(ft.Icons.SEARCH, on_click=self.show_search, tooltip="Search"),
            ft.IconButton(ft.Icons.HELP_OUTLINE, on_click=self.show_help, tooltip="Help"),
            self.theme_button,  # ✅ Используем сохраненную ссылку
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
        """Переключение между светлой и тёмной темой ✅ ИСПРАВЛЕНО"""
        if self.page_ref.theme_mode == ft.ThemeMode.LIGHT:
            self.page_ref.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE_OUTLINED
            self.theme_button.tooltip = "Switch to Light Mode"
        else:
            self.page_ref.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE_OUTLINED
            self.theme_button.tooltip = "Switch to Dark Mode"
        
        # Обновляем кнопку и страницу
        self.theme_button.update()
        self.page_ref.update()

    def show_search(self, e):
        # Simple search dialog placeholder
        dialog = ft.AlertDialog(
            title=ft.Text("Search"),
            content=ft.Text("Search functionality coming soon!"),
        )
        self.page_ref.open(dialog)

    def show_help(self, e):
        """✅ УЛУЧШЕННЫЙ дизайн Help диалога"""
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.HELP_OUTLINE, size=28, color=ft.Colors.BLUE_600),
                ft.Text("Help & Quick Start", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    # Getting Started
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.ROCKET_LAUNCH, size=18, color=ft.Colors.GREEN_600),
                                ft.Text("Getting Started", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                            ft.Container(height=5),
                            ft.Text("• Use sidebar to switch calendar views", size=12),
                            ft.Text("• Click '+' button to add events", size=12),
                            ft.Text("• Click dates in mini calendar to jump to Day view", size=12),
                        ]),
                        padding=15,
                        border_radius=8,
                        bgcolor=ft.Colors.GREEN_50,
                        border=ft.border.all(1, ft.Colors.GREEN_200),
                    ),
                    
                    ft.Container(height=10),
                    
                    # AI Chat
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CHAT, size=18, color=ft.Colors.BLUE_600),
                                ft.Text("AI Chat", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                            ft.Container(height=5),
                            ft.Text("• Ask AI to schedule things naturally", size=12),
                            ft.Text('• Try: "Add meeting at 3pm tomorrow"', size=12, italic=True),
                            ft.Text('• Try: "Suggest meals with eggs"', size=12, italic=True),
                        ]),
                        padding=15,
                        border_radius=8,
                        bgcolor=ft.Colors.BLUE_50,
                        border=ft.border.all(1, ft.Colors.BLUE_200),
                    ),
                    
                    ft.Container(height=10),
                    
                    # Categories & Priority
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PALETTE, size=18, color=ft.Colors.PURPLE_600),
                                ft.Text("Categories & Colors", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                            ft.Container(height=5),
                            ft.Text("• Events are color-coded by category", size=12),
                            ft.Text("• 10 categories: Study, Exercise, Food, etc.", size=12),
                            ft.Text("• 4 priority levels: Critical, High, Medium, Low", size=12),
                        ]),
                        padding=15,
                        border_radius=8,
                        bgcolor=ft.Colors.PURPLE_50,
                        border=ft.border.all(1, ft.Colors.PURPLE_200),
                    ),
                    
                    ft.Container(height=10),
                    
                    # Diet Planning
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.RESTAURANT_MENU, size=18, color=ft.Colors.ORANGE_600),
                                ft.Text("Diet Planning", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                            ft.Container(height=5),
                            ft.Text("• Go to Diet page to generate meal plans", size=12),
                            ft.Text("• Add meals to calendar with one click", size=12),
                            ft.Text("• Track macros: calories, protein, carbs, fats", size=12),
                        ]),
                        padding=15,
                        border_radius=8,
                        bgcolor=ft.Colors.ORANGE_50,
                        border=ft.border.all(1, ft.Colors.ORANGE_200),
                    ),
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
                width=450,
                height=500,
            ),
            actions=[
                ft.TextButton(
                    "Got it!",
                    on_click=lambda _: self.page_ref.close(dialog),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                        padding=15,
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page_ref.open(dialog)

    def show_settings(self, e):
        """✅ УЛУЧШЕННЫЙ дизайн Settings диалога"""
        from utils.translations import translations
        
        def change_language(e):
            lang_code = e.control.value
            translations.set_language(lang_code)
            self.page_ref.client_storage.set("language", lang_code)
            if self.on_language_change:
                self.on_language_change()
            self.page_ref.close(dialog)
        
        def toggle_theme_mode(e):
            """Переключение темы из Settings"""
            self.toggle_theme(e)
            # Обновляем текст в switch
            theme_switch.label = "Dark Mode" if self.page_ref.theme_mode == ft.ThemeMode.DARK else "Light Mode"
            theme_switch.update()

        lang_dropdown = ft.Dropdown(
            label="Language",
            value=translations.current_language,
            options=[
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("ru", "Русский"),
            ],
            on_change=change_language,
            border_radius=8,
            filled=True,
        )
        
        theme_switch = ft.Switch(
            label="Dark Mode" if self.page_ref.theme_mode == ft.ThemeMode.DARK else "Light Mode",
            value=self.page_ref.theme_mode == ft.ThemeMode.DARK,
            on_change=toggle_theme_mode,
        )

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.SETTINGS, size=28, color=ft.Colors.BLUE_600),
                ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    # About Section
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=ft.Colors.BLUE_600),
                                ft.Text("About", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                            ft.Container(height=8),
                            ft.Row([
                                ft.Text("Version:", size=12, color=ft.Colors.GREY_600),
                                ft.Text("1.0.0", size=12, weight=ft.FontWeight.BOLD),
                            ], spacing=10),
                            ft.Row([
                                ft.Text("Build:", size=12, color=ft.Colors.GREY_600),
                                ft.Text("2026-02-13", size=12),
                            ], spacing=10),
                        ]),
                        padding=15,
                        border_radius=8,
                        bgcolor=ft.Colors.BLUE_50,
                        border=ft.border.all(1, ft.Colors.BLUE_200),
                    ),
                    
                    ft.Container(height=15),
                    
                    # Appearance Section
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PALETTE, size=18, color=ft.Colors.PURPLE_600),
                                ft.Text("Appearance", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                            ft.Container(height=8),
                            theme_switch,
                        ]),
                        padding=15,
                        border_radius=8,
                        bgcolor=ft.Colors.PURPLE_50,
                        border=ft.border.all(1, ft.Colors.PURPLE_200),
                    ),
                    
                    ft.Container(height=15),
                    
                    # Language Section
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.LANGUAGE, size=18, color=ft.Colors.GREEN_600),
                                ft.Text("Language", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                            ft.Container(height=8),
                            lang_dropdown,
                        ]),
                        padding=15,
                        border_radius=8,
                        bgcolor=ft.Colors.GREEN_50,
                        border=ft.border.all(1, ft.Colors.GREEN_200),
                    ),
                    
                    ft.Container(height=15),
                    
                    # Links Section
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.LINK, size=18, color=ft.Colors.ORANGE_600),
                                ft.Text("Resources", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                            ft.Container(height=8),
                            ft.TextButton(
                                "📖 Help & FAQ",
                                on_click=lambda _: self.show_help(_),
                                icon=ft.Icons.HELP_OUTLINE,
                            ),
                            ft.TextButton(
                                "🐛 Report Bug",
                                on_click=lambda _: print("Report bug"),
                                icon=ft.Icons.BUG_REPORT,
                            ),
                            ft.TextButton(
                                "⭐ Rate Us",
                                on_click=lambda _: print("Rate app"),
                                icon=ft.Icons.STAR_OUTLINE,
                            ),
                        ]),
                        padding=15,
                        border_radius=8,
                        bgcolor=ft.Colors.ORANGE_50,
                        border=ft.border.all(1, ft.Colors.ORANGE_200),
                    ),
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=500,
            ),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=lambda _: self.page_ref.close(dialog),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                        padding=15,
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page_ref.open(dialog)