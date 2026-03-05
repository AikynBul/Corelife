import flet as ft
import datetime
import calendar
from components.event_dialog import EventDialog
from utils.translations import translations

class Sidebar(ft.Container):
    def __init__(self, on_view_change=None, on_filter_change=None, on_refresh=None, on_date_click=None):
        super().__init__()
        self.on_view_change = on_view_change
        self.on_filter_change = on_filter_change
        self.on_refresh = on_refresh
        self.on_date_click = on_date_click  # ✅ НОВЫЙ callback для клика на дату
        self.width = 250
        self.padding = 10
        self.current_date = datetime.date.today()
        self.current_calendar_view = "Month"  # ✅ Отслеживаем текущий вид
        
        # ✅ Создаём expansion tile для календаря
        self.calendar_expansion = self.build_calendar_expansion()
        
        self.content = ft.Column(
            controls=[
                self.build_create_button(),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.calendar_expansion,  # ✅ ИЗМЕНЕНО: вместо build_view_switcher()
                ft.TextButton(
                    "🛒 Grocery Store",
                    on_click=lambda e: self.on_view_change("Grocery") if self.on_view_change else None,
                    icon=ft.Icons.SHOPPING_CART
                ),
                ft.TextButton(
                    translations.get("diet_view"), 
                    on_click=lambda e: self.on_view_change("Diet") if self.on_view_change else None, 
                    icon=ft.Icons.RESTAURANT_MENU
                ),
                ft.TextButton(
                    "FAQ",
                    on_click=lambda e: self.on_view_change("FAQ") if self.on_view_change else None,
                    icon=ft.Icons.HELP_CENTER,
                ),

                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.build_mini_calendar(),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.build_my_calendars(),
            ],
            scroll=ft.ScrollMode.AUTO,  # ✅ ДОБАВЛЕНО
        )

    def build_calendar_expansion(self):
        """✅ НОВЫЙ МЕТОД: Создаёт выпадающее меню для видов календаря"""
        # Текст для отображения текущего выбранного вида
        self.calendar_view_text = ft.Text(
            self.get_view_label(self.current_calendar_view),
            size=14,
            weight=ft.FontWeight.W_500
        )
        
        # Контейнер с иконкой и текстом
        self.expansion_tile = ft.ExpansionTile(
            title=ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH, size=20),
                self.calendar_view_text,
            ], spacing=10),
            subtitle=None,
            initially_expanded=False,
            controls=[
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CALENDAR_MONTH, size=20),
                    title=ft.Text(translations.get("month_view")),
                    on_click=lambda e: self.switch_calendar_view("Month")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.VIEW_WEEK, size=20),
                    title=ft.Text(translations.get("week_view")),
                    on_click=lambda e: self.switch_calendar_view("Week")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.TODAY, size=20),
                    title=ft.Text(translations.get("day_view")),
                    on_click=lambda e: self.switch_calendar_view("Day")
                ),
            ],
        )
        
        return self.expansion_tile
    
    def get_view_label(self, view_name):
        """Возвращает локализованное название вида"""
        labels = {
            "Month": translations.get("month_view"),
            "Week": translations.get("week_view"),
            "Day": translations.get("day_view"),
        }
        return labels.get(view_name, view_name)
    
    def switch_calendar_view(self, view_name):
        """✅ НОВЫЙ МЕТОД: Переключает вид календаря"""
        self.current_calendar_view = view_name
        self.calendar_view_text.value = self.get_view_label(view_name)
        self.calendar_view_text.update()
        
        # Закрываем expansion tile
        self.expansion_tile.initially_expanded = False
        self.expansion_tile.update()
        
        # Вызываем callback для переключения вида
        if self.on_view_change:
            self.on_view_change(view_name)

    def build_create_button(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ADD, color=ft.Colors.ON_PRIMARY_CONTAINER),
                    ft.Text(translations.get("create"), color=ft.Colors.ON_PRIMARY_CONTAINER, weight=ft.FontWeight.W_500),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            border_radius=16,
            padding=ft.padding.symmetric(vertical=12, horizontal=20),
            width=140,
            on_click=self.open_create_dialog,
            ink=True,
        )

    def open_create_dialog(self, e):
        print("Create button clicked")
        try:
            dialog = EventDialog(e.page, on_dismiss=self.on_refresh)
            e.page.open(dialog)
            print("Dialog opened via page.open()")
        except Exception as ex:
            print(f"Error opening create dialog: {ex}")
            import traceback
            traceback.print_exc()
            e.page.snack_bar = ft.SnackBar(ft.Text(f"Error opening dialog: {ex}"))
            e.page.snack_bar.open = True
            e.page.update()

    def build_mini_calendar(self):
        """✅ ИЗМЕНЕНО: Мини-календарь теперь кликабельный, неделя с Monday"""
        today = datetime.date.today()
        
        # ✅ ИСПРАВЛЕНО: Устанавливаем первый день недели = Monday (0)
        calendar.setfirstweekday(calendar.MONDAY)
        cal = calendar.monthcalendar(today.year, today.month)
        
        month_name = translations.get("months")[today.month - 1]
        
        rows = [
            ft.Text(f"{month_name} {today.year}", weight=ft.FontWeight.BOLD, size=14),
            # ✅ ИСПРАВЛЕНО: Неделя начинается с Monday
            ft.Row([ft.Text(d, size=10, width=20, text_align=ft.TextAlign.CENTER) for d in ["M", "T", "W", "T", "F", "S", "S"]], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]
        
        for week in cal:
            week_row = []
            for day in week:
                if day == 0:
                    week_row.append(ft.Container(width=20))
                else:
                    is_today = day == self.current_date.day and self.current_date.month == datetime.date.today().month and self.current_date.year == datetime.date.today().year
                    
                    # ✅ ИЗМЕНЕНО: Добавлен обработчик клика
                    selected_date = datetime.date(today.year, today.month, day)
                    
                    week_row.append(
                        ft.Container(
                            content=ft.Text(str(day), size=10, color=ft.Colors.ON_PRIMARY if is_today else None),
                            width=20,
                            height=20,
                            bgcolor=ft.Colors.PRIMARY if is_today else None,
                            border_radius=10,
                            alignment=ft.alignment.center,
                            on_click=lambda e, date=selected_date: self.handle_date_click(date),  # ✅ ДОБАВЛЕНО
                            ink=True  # ✅ ДОБАВЛЕНО: эффект клика
                        )
                    )
            rows.append(ft.Row(week_row, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        return ft.Column(rows, spacing=5)
    
    def handle_date_click(self, date):
        """✅ НОВЫЙ МЕТОД: Обрабатывает клик на дату в мини-календаре"""
        print(f"Date clicked: {date}")
        
        # Переключаем на дневной вид
        self.current_calendar_view = "Day"
        self.calendar_view_text.value = self.get_view_label("Day")
        self.calendar_view_text.update()
        
        # Вызываем callback с выбранной датой
        if self.on_date_click:
            self.on_date_click(date)

    def build_my_calendars(self):
        self.events_checkbox = ft.Checkbox(label=translations.get("events"), value=True, on_change=self.trigger_filter)
        self.tasks_checkbox = ft.Checkbox(label=translations.get("tasks"), value=True, on_change=self.trigger_filter)
        
        return ft.Column(
            controls=[
                ft.Text(translations.get("my_calendars"), weight=ft.FontWeight.BOLD),
                self.events_checkbox,
                self.tasks_checkbox,
            ]
        )

    def trigger_filter(self, e):
        if self.on_filter_change:
            filters = {
                "events": self.events_checkbox.value,
                "tasks": self.tasks_checkbox.value
            }
            self.on_filter_change(filters)

