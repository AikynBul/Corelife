import flet as ft
from components.sidebar import Sidebar
from components.calendar import MonthView
from components.day_view import DayView
from components.week_view import WeekView
from components.account_view import AccountView
from components.diet_view import DietView  # ✅ НОВЫЙ ИМПОРТ

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page, user_info: dict, on_logout):
        super().__init__()
        self.page = page
        self.user_info = user_info
        self.on_logout = on_logout
        self.expand = True
        self.spacing = 0
        
        # Sidebar
        self.sidebar = ft.Container(
            content=Sidebar(
                on_view_change=self.set_view,
                on_filter_change=self.refresh_active_view
            ),
            width=250,
            bgcolor=ft.Colors.SURFACE,
            padding=10,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
        self.filters = {"events": True, "tasks": True}
        
        # Views
        self.month_view = MonthView(on_day_click=self.go_to_day)
        self.day_view = DayView()
        self.week_view = WeekView()
        self.account_view = AccountView(self.user_info, self.on_logout)
        self.diet_view = DietView(self.page, self.user_info)  # ✅ НОВЫЙ VIEW

        # Main Content Area
        self.content_area = ft.Container(
            expand=True,
            padding=10,
            content=self.month_view
        )

        self.controls = [
            self.sidebar,
            ft.VerticalDivider(width=1),
            self.content_area
        ]

    def set_view(self, view_name):
        """Переключает вид в зависимости от выбора в сайдбаре"""
        if view_name == "Month":
            self.content_area.content = self.month_view
        elif view_name == "Day":
            self.day_view.render_view() # Refresh
            self.content_area.content = self.day_view
        elif view_name == "Week":
            self.week_view.render_view() # Refresh
            self.content_area.content = self.week_view
        elif view_name == "Account":
            if self.account_view:
                self.content_area.content = self.account_view
        elif view_name == "Diet":  # ✅ НОВАЯ СТРАНИЦА
            # Пересоздаём diet_view чтобы обновить данные
            self.diet_view = DietView(self.page, self.user_info)
            self.content_area.content = self.diet_view
        
        self.content_area.update()

    def go_to_day(self, date):
        """Переход к дневному виду с выбранной датой"""
        self.day_view.current_date = date
        self.set_view("Day")
        # Update sidebar selection if possible, or just let it be
        # self.sidebar.view_selector.value = "Day" # If we had access to change it
        self.sidebar.update()

    def update_filters(self, filters):
        """Обновляет фильтры событий/задач"""
        self.filters = filters
        self.refresh_active_view()

    def refresh_active_view(self, filters=None):
        """Обновляет текущий активный вид"""
        # ✅ ИСПРАВЛЕНО: Принимаем filters и обновляем self.filters
        if filters is not None:
            self.filters = filters
        
        # Re-render the current view
        if self.content_area.content == self.month_view:
            self.month_view.update_filter(self.filters) # This triggers render
        elif self.content_area.content == self.week_view:
            self.week_view.filters = self.filters
            self.week_view.render_view()
            self.week_view.update()
        elif self.content_area.content == self.day_view:
            self.day_view.filters = self.filters
            self.day_view.render_view()
            self.day_view.update()
        elif self.content_area.content == self.diet_view:
            # Пересоздаём diet_view для обновления данных
            self.diet_view = DietView(self.page, self.user_info)
            self.content_area.content = self.diet_view
            self.content_area.update()
        else:
            self.content_area.update()

    def toggle_sidebar(self):
        """Скрывает/показывает сайдбар"""
        if self.sidebar.width == 0:
            self.sidebar.width = 250
        else:
            self.sidebar.width = 0
        self.sidebar.update()