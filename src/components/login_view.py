import flet as ft
from services.auth_service import auth_service

class LoginView(ft.Container):
    def __init__(self, on_login):
        super().__init__()
        self.on_login = on_login
        self.expand = True
        self.alignment = ft.alignment.center
        self.bgcolor = ft.Colors.BLUE_GREY_50
        self.is_registering = False
        
        self.username_field = ft.TextField(
            label="Username",
            width=300,
            autofocus=True,
            on_submit=self.submit
        )
        self.email_field = ft.TextField(
            label="Email (Optional)",
            width=300,
            visible=False,
            on_submit=self.submit
        )
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=self.submit
        )
        self.error_text = ft.Text(
            color=ft.Colors.RED,
            size=12,
            visible=False
        )
        
        self.title_text = ft.Text("Welcome Back", size=24, weight=ft.FontWeight.BOLD)
        self.submit_button = ft.ElevatedButton(
            "Login",
            width=300,
            height=45,
            on_click=self.submit,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
        self.toggle_text = ft.TextButton(
            "Don't have an account? Register",
            on_click=self.toggle_mode
        )

        self.content = ft.Card(
            content=ft.Container(
                padding=40,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.LOCK_OUTLINE, size=64, color=ft.Colors.BLUE),
                        self.title_text,
                        ft.Container(height=20),
                        self.username_field,
                        self.email_field,
                        self.password_field,
                        self.error_text,
                        ft.Container(height=20),
                        self.submit_button,
                        ft.Container(height=10),
                        self.toggle_text
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True
                )
            ),
            elevation=10,
        )

    def toggle_mode(self, e):
        self.is_registering = not self.is_registering
        
        if self.is_registering:
            self.title_text.value = "Create Account"
            self.submit_button.text = "Register"
            self.toggle_text.text = "Already have an account? Login"
            self.email_field.visible = True
        else:
            self.title_text.value = "Welcome Back"
            self.submit_button.text = "Login"
            self.toggle_text.text = "Don't have an account? Register"
            self.email_field.visible = False
            
        self.error_text.visible = False
        self.update()

    def submit(self, e):
        username = self.username_field.value
        password = self.password_field.value
        email = self.email_field.value
        
        if not username or not password:
            self.error_text.value = "Please enter both username and password"
            self.error_text.visible = True
            self.update()
            return
            
        self.error_text.visible = False
        self.update()
        
        if self.is_registering:
            if "@" not in email:
                self.error_text.value = "Invalid email address"
                self.error_text.visible = True
                self.update()
                return

            success, message = auth_service.register(username, password, email)
            if success:
                # Auto login after register
                self.perform_login(username, password)
            else:
                self.error_text.value = message
                self.error_text.visible = True
                self.update()
        else:
            self.perform_login(username, password)

    def perform_login(self, username, password):
        user_info, message = auth_service.login(username, password)
        
        if user_info:
            self.on_login(user_info)
        else:
            self.error_text.value = message
            self.error_text.visible = True
            self.update()
