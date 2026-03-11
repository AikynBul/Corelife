import flet as ft
import datetime
from data.store import store

class AddMealToCalendarDialog(ft.AlertDialog):
    """
    Диалог для добавления блюда из diet plan в календарь
    """
    def __init__(self, page: ft.Page, meal_name: str, day: str, meal_type: str, on_dismiss=None):
        self.page_ref = page
        self.meal_name = meal_name
        self.day = day  # monday, tuesday, etc.
        self.meal_type = meal_type  # breakfast, lunch, dinner
        self.on_dismiss_callback = on_dismiss
        
        # Вычисляем дату (понедельник текущей недели + offset)
        self.target_date = self.get_date_for_day(day)
        
        # Определяем время по типу приёма пищи
        default_times = {
            "breakfast": ("08:00", "09:00"),
            "lunch": ("12:00", "13:00"),
            "dinner": ("18:00", "19:00"),
            "snack": ("15:00", "15:30")
        }
        
        default_start, default_end = default_times.get(meal_type, ("12:00", "13:00"))
        
        # Date Picker
        self.date_picker = ft.DatePicker(
            on_change=self.change_date,
            first_date=datetime.datetime(2024, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
            value=self.target_date
        )
        
        self.date_field = ft.TextField(
            label="Date",
            value=self.target_date.strftime("%Y-%m-%d"),
            read_only=True,
            expand=True,
            suffix=ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                tooltip="Pick date",
                on_click=lambda _: self.page_ref.open(self.date_picker),
            ),
        )
        
        # Time Fields
        self.start_time_field = ft.TextField(
            label="Start Time",
            value=default_start,
            hint_text="HH:MM",
            width=120
        )
        
        self.end_time_field = ft.TextField(
            label="End Time",
            value=default_end,
            hint_text="HH:MM",
            width=120
        )
        
        super().__init__(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, size=24, color=ft.Colors.GREEN_600),
                ft.Text("Add to Calendar", size=18, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.RESTAURANT, size=20, color=ft.Colors.GREY_600),
                            ft.Text(
                                meal_name,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800,
                                expand=True
                            ),
                        ], spacing=10),
                        padding=10,
                        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.GREEN_400),
                        border_radius=8,
                    ),
                    ft.Container(height=15),
                    self.date_field,
                    ft.Row([self.start_time_field, self.end_time_field], spacing=10),
                ],
                width=350,
                spacing=10,
                tight=True
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.close_dialog,
                    style=ft.ButtonStyle(color=ft.Colors.GREY_600)
                ),
                ft.ElevatedButton(
                    "Add to Calendar",
                    icon=ft.Icons.CHECK,
                    on_click=self.add_to_calendar,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN_600,
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def get_date_for_day(self, day_name):
        """Вычисляет дату для дня недели (понедельник текущей недели + offset)"""
        days_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }
        
        today = datetime.date.today()
        # Находим понедельник текущей недели
        monday = today - datetime.timedelta(days=today.weekday())
        
        # Добавляем offset
        offset = days_map.get(day_name.lower(), 0)
        target_date = monday + datetime.timedelta(days=offset)
        
        return target_date
    
    def change_date(self, e):
        if not self.date_picker.value:
            return
        selected = self.date_picker.value
        if isinstance(selected, datetime.datetime):
            selected = selected.date()
        self.date_field.value = selected.strftime("%Y-%m-%d")
        self.date_field.update()
    
    def add_to_calendar(self, e):
        """Добавляет блюдо в календарь как событие"""
        # Validate Time Format
        import re
        time_pattern = re.compile(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
        
        if not time_pattern.match(self.start_time_field.value):
            self.start_time_field.error_text = "Invalid (HH:MM)"
            self.start_time_field.update()
            return
            
        if not time_pattern.match(self.end_time_field.value):
            self.end_time_field.error_text = "Invalid (HH:MM)"
            self.end_time_field.update()
            return
        
        # Combine date and time
        start_dt = f"{self.date_field.value} {self.start_time_field.value}"
        end_dt = f"{self.date_field.value} {self.end_time_field.value}"
        
        # Создаём событие в календаре
        store.add_event(
            title=self.meal_name,
            start_date=start_dt,
            end_date=end_dt,
            description=f"Meal from diet plan ({self.meal_type})",
            event_type="event",
            category="Food"
        )
        
        # Показываем уведомление
        snack = ft.SnackBar(
            content=ft.Text(f"✅ {self.meal_name} added to calendar!"),
            bgcolor=ft.Colors.GREEN_400
        )
        self.page_ref.open(snack)
        
        self.close_dialog(e)
    
    def close_dialog(self, e):
        self.page_ref.close(self)
        self.page_ref.update()
        if self.on_dismiss_callback:
            self.on_dismiss_callback()