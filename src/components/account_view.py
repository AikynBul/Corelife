import flet as ft
from utils.translations import translations

class AccountView(ft.Container):
    def __init__(self, user_info, on_logout):
        super().__init__()
        self.user_info = user_info
        self.on_logout = on_logout
        self.expand = True
        self.padding = 40
        self.expand = True
        self.padding = 40
        # self.bgcolor = ft.Colors.WHITE # Removed hardcoded color
        
        # Profile Section
        self.avatar = ft.CircleAvatar(
            content=ft.Text(
                self.user_info.get("name", "U")[0].upper(), 
                size=30, 
                weight=ft.FontWeight.BOLD,
                # color=ft.Colors.BLACK
            ),
            radius=35,
            bgcolor=ft.Colors.BLUE_200,
        )
        
        self.name_text = ft.Text(
            self.user_info.get("name", "User"), 
            size=28, 
            weight=ft.FontWeight.BOLD,
            # color=ft.Colors.BLACK
        )
        
        self.email_text = ft.Text(
            self.user_info.get("email", "user@example.com"), 
            size=14, 
            color=ft.Colors.GREY_500
        )

        # Account Info Section
        self.name_field = ft.TextField(
            label=translations.get("name"),
            value=self.user_info.get("name", ""),
            border_color=ft.Colors.GREY_400,
            text_size=14,
            height=50,
        )
        
        self.email_field = ft.TextField(
            label=translations.get("email"),
            value=self.user_info.get("email", ""),
            read_only=True,
            border_color=ft.Colors.GREY_400,
            text_size=14,
            height=50,
            # bgcolor=ft.Colors.GREY_100 # Removed hardcoded color
        )

        # Security Section
        self.current_password = ft.TextField(
            label=translations.get("current_password"),
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.GREY_400,
            text_size=14,
            height=50
        )
        
        self.new_password = ft.TextField(
            label=translations.get("new_password"),
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.GREY_400,
            text_size=14,
            height=50
        )
        
        self.confirm_password = ft.TextField(
            label=translations.get("confirm_password"),
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.GREY_400,
            text_size=14,
            height=50
        )

        self.content = ft.Column(
            [
                ft.Text(translations.get("account"), size=32, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20, color=ft.Colors.GREY_200),
                
                ft.Row(
                    [
                        # Left Column (Cards)
                        ft.Column(
                            [
                                self._build_info_card(),
                                ft.Container(height=10),
                                self._build_security_card(),
                                ft.Container(height=10),
                                self._build_actions_card(),
                            ],
                            expand=2,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        # Right Column (Profile Header - strictly speaking the image has it on top or side, 
                        # but the image 1 shows profile info at top left. 
                        # Let's stick to the image 1 layout: Header -> Profile Row -> Grid of cards?
                        # Actually, Image 1 shows:
                        # Header "Account"
                        # Row: Avatar | Name & Email
                        # Then below that:
                        # Column of cards: Account Info, Security, Actions (Image 2)
                        # Let's adjust to that.)
                    ],
                    expand=True
                )
            ],
            expand=True,
        )
        
        # Re-building content to match Image 1 & 2 flow better
        self.content = ft.ListView(
            [
                ft.Text(translations.get("account"), size=32, weight=ft.FontWeight.BOLD),
                ft.Divider(height=30, color=ft.Colors.GREY_200),
                
                # Profile Header
                ft.Row(
                    [
                        self.avatar,
                        ft.Column(
                            [
                                self.name_text,
                                self.email_text
                            ],
                            spacing=0
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
                ft.Container(height=30),
                
                # Cards Area - Using a Row to limit width if screen is wide, or just Column
                ft.Row(
                    [
                        ft.Column(
                            [
                                self._build_info_card(),
                                ft.Container(height=20),
                                self._build_security_card(),
                                ft.Container(height=20),
                                self._build_actions_card(),
                            ],
                            width=400, # Fixed width for the form cards as per typical UI
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START
                )
            ],
            padding=ft.padding.only(bottom=50)
        )

    def _build_info_card(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(translations.get("account_info"), size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    self.name_field,
                    self.email_field,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        translations.get("save_name"),
                        icon=ft.Icons.SAVE,
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLUE_700,
                            bgcolor=ft.Colors.BLUE_50,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=lambda e: print("Save Name Clicked")
                    )
                ]
            ),
            padding=20,
            bgcolor=ft.Colors.SURFACE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _build_security_card(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(translations.get("security"), size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    self.current_password,
                    self.new_password,
                    self.confirm_password,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        translations.get("change_password"),
                        icon=ft.Icons.LOCK,
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLUE_700,
                            bgcolor=ft.Colors.BLUE_50,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=lambda e: print("Change Password Clicked")
                    )
                ]
            ),
            padding=20,
            bgcolor=ft.Colors.SURFACE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def _build_actions_card(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(translations.get("actions"), size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        translations.get("logout"),
                        icon=ft.Icons.LOGOUT,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.RED_400,
                            shape=ft.RoundedRectangleBorder(radius=20), # Rounded as per image
                        ),
                        on_click=self.on_logout
                    ),
                    ft.Container(height=5),
                    ft.TextButton(
                        translations.get("delete_account"),
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        style=ft.ButtonStyle(
                            color=ft.Colors.RED_400,
                        ),
                        on_click=lambda e: print("Delete Account Clicked")
                    )
                ]
            ),
            padding=20,
            bgcolor=ft.Colors.SURFACE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        )
