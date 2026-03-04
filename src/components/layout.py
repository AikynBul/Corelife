import flet as ft
from components.sidebar import Sidebar
from components.calendar import MonthView
from components.day_view import DayView
from components.week_view import WeekView
from components.account_view import AccountView
from components.diet_view import DietView
from components.grocery_store import GroceryStore  # ✅ НОВЫЙ ИМПОРТ

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
                on_filter_change=self.refresh_active_view,
                on_date_click=self.go_to_day,   # ✅ FIX: передаём клик на дату в sidebar
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
        self.account_view = AccountView(self.user_info, self.on_logout, page=self.page)
        self.diet_view = DietView(self.page, self.user_info)
        self.grocery_view = GroceryStore(page=self.page, user_info=self.user_info, on_refresh=lambda: self.refresh_grocery())  # ✅ CALLBACK

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
        # ✅ КРИТИЧНО: ВСЕГДА очищаем bottom panel при любом переходе
        if hasattr(self, 'grocery_view'):
            print(f"SET_VIEW: Clearing bottom panel for view_name={view_name}")
            self.grocery_view.clear_bottom_panel()
        
        if view_name == "Month":
            self.content_area.content = self.month_view
        elif view_name == "Day":
            self.day_view.render_view()
            self.content_area.content = self.day_view
        elif view_name == "Week":
            self.week_view.render_view()
            self.content_area.content = self.week_view
        elif view_name == "Account":
            if self.account_view:
                self.content_area.content = self.account_view
        elif view_name == "Grocery":
            self.content_area.content = self.grocery_view
            # ✅ Показываем bottom panel если корзина не пустая И view_mode == "shop"
            if self.grocery_view.cart and self.grocery_view.view_mode == "shop":
                print(f"SET_VIEW: Building bottom panel for Grocery")
                self.grocery_view.build_bottom_panel()
        elif view_name == "Diet":
            self.diet_view = DietView(self.page, self.user_info)
            self.content_area.content = self.diet_view
        
        self.content_area.update()

    def go_to_day(self, date):
        """Переход к дневному виду с выбранной датой"""
        self.day_view.current_date = date
        self.set_view("Day")
        self.sidebar.update()

    def update_filters(self, filters):
        """Обновляет фильтры событий/задач"""
        self.filters = filters
        self.refresh_active_view()

    def refresh_active_view(self, filters=None):
        """Обновляет текущий активный вид"""
        if filters is not None:
            self.filters = filters
        
        if self.content_area.content == self.month_view:
            self.month_view.update_filter(self.filters)
        elif self.content_area.content == self.week_view:
            self.week_view.filters = self.filters
            self.week_view.render_view()
            self.week_view.update()
        elif self.content_area.content == self.day_view:
            self.day_view.filters = self.filters
            self.day_view.render_view()
            self.day_view.update()
        elif self.content_area.content == self.diet_view:
            self.diet_view = DietView(self.page, self.user_info)
            self.content_area.content = self.diet_view
            self.content_area.update()
        elif self.content_area.content == self.grocery_view:
            # Пересоздаём grocery view с обновлёнными данными
            self.grocery_view = GroceryStore(page=self.page, user_info=self.user_info, on_refresh=lambda: self.refresh_grocery())
            self.content_area.content = self.grocery_view
        else:
            self.content_area.update()
    
    def refresh_grocery(self):
        """✅ НОВОЕ: Обновить grocery view"""
        self.grocery_view.build_ui()
        self.content_area.update()

    def toggle_sidebar(self):
        """Скрывает/показывает сайдбар"""
        if self.sidebar.width == 0:
            self.sidebar.width = 250
        else:
            self.sidebar.width = 0
        self.sidebar.update()