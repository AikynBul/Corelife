import flet as ft
from utils.translations import translations

class OnboardingView(ft.Column):
    """
    Экран онбординга после регистрации.
    Пользователь выбирает свою цель: тайм-менеджмент и/или диета.
    """
    def __init__(self, page: ft.Page, user_info: dict, on_complete):
        super().__init__()
        self.page_ref = page
        self.user_info = user_info
        self.on_complete = on_complete  # Callback(selected_goals: list) -> None
        
        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 30
        
        # Состояние выбора
        self.selected_time_management = False
        self.selected_diet = False
        
        # UI элементы
        self.time_management_card = self.create_goal_card(
            icon=ft.Icons.CALENDAR_MONTH,
            title="Time Management",
            description="Organize your schedule and improve productivity",
            color=ft.Colors.BLUE_400,
            on_click=self.toggle_time_management
        )
        
        self.diet_card = self.create_goal_card(
            icon=ft.Icons.RESTAURANT_MENU,
            title="Diet Planning",
            description="Find your perfect diet with AI recommendations",
            color=ft.Colors.GREEN_400,
            on_click=self.toggle_diet
        )
        
        self.controls = [
            ft.Container(height=50),  # Отступ сверху
            
            # Заголовок
            ft.Text(
                "Welcome to Corelife! 👋",
                size=32,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            
            ft.Text(
                "What are your goals?",
                size=18,
                color=ft.Colors.GREY_600,
                text_align=ft.TextAlign.CENTER
            ),
            
            ft.Container(height=20),
            
            # Карточки выбора целей
            ft.Row(
                controls=[
                    self.time_management_card,
                    self.diet_card,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            ),
            
            ft.Container(height=30),
            
            # Кнопка продолжения
            ft.ElevatedButton(
                text="Continue",
                width=200,
                height=50,
                on_click=self.on_continue_click,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_600,
                )
            ),
            
            ft.Container(height=50),  # Отступ снизу
        ]
    
    def create_goal_card(self, icon, title, description, color, on_click):
        """Создает карточку выбора цели"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=60, color=color),
                    ft.Container(height=15),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    ft.Text(
                        description,
                        size=14,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                        width=250
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0
            ),
            width=300,
            height=250,
            border=ft.border.all(2, ft.Colors.GREY_300),
            border_radius=15,
            padding=20,
            ink=True,
            on_click=lambda e: on_click(),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
        )
    
    def toggle_time_management(self):
        """Переключение выбора тайм-менеджмента"""
        self.selected_time_management = not self.selected_time_management
        self.update_card_style(self.time_management_card, self.selected_time_management, ft.Colors.BLUE_400)
    
    def toggle_diet(self):
        """Переключение выбора диеты"""
        self.selected_diet = not self.selected_diet
        self.update_card_style(self.diet_card, self.selected_diet, ft.Colors.GREEN_400)
    
    def update_card_style(self, card, is_selected, color):
        """Обновляет стиль карточки в зависимости от выбора"""
        if is_selected:
            card.border = ft.border.all(3, color)
            card.bgcolor = color.replace("400", "50")  # Светлый оттенок
            card.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=color.replace("400", "200"),
                offset=ft.Offset(0, 4)
            )
        else:
            card.border = ft.border.all(2, ft.Colors.GREY_300)
            card.bgcolor = None
            card.shadow = None
        
        card.update()
    
    def on_continue_click(self, e):
        """Обработка нажатия кнопки Continue"""
        if not self.selected_time_management and not self.selected_diet:
            # Показываем предупреждение если ничего не выбрано
            snack = ft.SnackBar(
                content=ft.Text("Please select at least one goal!"),
                bgcolor=ft.Colors.RED_400
            )
            self.page_ref.open(snack)
            return
        
        # Собираем выбранные цели
        selected_goals = []
        if self.selected_time_management:
            selected_goals.append("time_management")
        if self.selected_diet:
            selected_goals.append("diet")
        
        # Вызываем callback с выбранными целями
        if self.on_complete:
            self.on_complete(selected_goals)