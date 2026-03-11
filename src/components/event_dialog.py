import flet as ft
import datetime
from data.store import store

class EventDialog(ft.AlertDialog):
    """✅ УЛУЧШЕННЫЙ ДИЗАЙН: Современный диалог создания/редактирования событий"""
    
    def __init__(self, page: ft.Page, on_dismiss=None, event=None):
        self.page_ref = page
        self.on_dismiss_callback = on_dismiss
        self.event = event
        self.is_editing = event is not None

        is_light_theme = self.page_ref.theme_mode == ft.ThemeMode.LIGHT
        label_color = ft.Colors.BLACK if is_light_theme else ft.Colors.GREY_300
        cancel_color = ft.Colors.BLACK if is_light_theme else ft.Colors.GREY_400
        
        # Парсим данные события
        if event:
            start_str = event.get("start", "")
            end_str = event.get("end", "")
            
            if " " in start_str:
                start_date, start_time = start_str.split(" ", 1)
            else:
                start_date, start_time = start_str, "09:00"
            
            if " " in end_str:
                _, end_time = end_str.split(" ", 1)
            else:
                end_time = "10:00"
            
            title_value = event.get("title", "")
            description_value = event.get("description", "") or ""
            category_value = event.get("category", "Personal")
            recurrence_value = event.get("recurrence") or "none"
            is_task_value = event.get("type") == "task"
            priority_value = event.get("priority", "Medium")
        else:
            title_value = ""
            start_date = datetime.date.today().isoformat()
            start_time = "09:00"
            end_time = "10:00"
            description_value = ""
            category_value = "Personal"
            recurrence_value = "none"
            is_task_value = False
            priority_value = "Medium"
        
        # ===== ПОЛЯ ФОРМЫ =====
        
        # Заголовок события
        self.title_field = ft.TextField(
            label="Event title" if not self.is_editing else "Title",
            value=title_value,
            autofocus=True,
            text_size=18,
            border_radius=10,
            filled=True,
            prefix_icon=ft.Icons.EDIT_NOTE,
        )
        
        # Date Picker
        self.date_picker = ft.DatePicker(
            on_change=self.change_date,
            first_date=datetime.datetime(2023, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )
        
        self.date_field = ft.TextField(
            label="Date",
            value=start_date,
            read_only=True,
            expand=True,
            border_radius=10,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            suffix=ft.IconButton(
                icon=ft.Icons.ARROW_DROP_DOWN,
                tooltip="Pick date",
                on_click=lambda _: self.page_ref.open(self.date_picker),
            ),
        )
        
        # Time Fields
        self.start_time_field = ft.TextField(
            label="Start",
            value=start_time,
            hint_text="HH:MM",
            expand=True,
            border_radius=10,
            filled=True,
            prefix_icon=ft.Icons.ACCESS_TIME,
        )
        
        self.end_time_field = ft.TextField(
            label="End",
            value=end_time,
            hint_text="HH:MM",
            expand=True,
            border_radius=10,
            filled=True,
            prefix_icon=ft.Icons.ACCESS_TIME_FILLED,
        )
        
        # Category Dropdown
        self.category_dropdown = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("Routine", "🔄 Routine"),
                ft.dropdown.Option("Sleep", "😴 Sleep"),
                ft.dropdown.Option("Food", "🍽️ Food"),
                ft.dropdown.Option("Study", "📚 Study"),
                ft.dropdown.Option("Exercise", "💪 Exercise"),
                ft.dropdown.Option("Work", "💼 Work"),
                ft.dropdown.Option("Social", "👥 Social"),
                ft.dropdown.Option("Health", "🏥 Health"),
                ft.dropdown.Option("Personal", "👤 Personal"),
                ft.dropdown.Option("Entertainment", "🎮 Entertainment"),
            ],
            value=category_value,
            border_radius=10,
            filled=True,
        )
        
        # Description
        self.description_field = ft.TextField(
            label="Description (optional)",
            value=description_value,
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=10,
            filled=True,
        )
        
        # Repeat
        self.recurrence_dropdown = ft.Dropdown(
            label="Repeat",
            options=[
                ft.dropdown.Option("none", "Does not repeat"),
                ft.dropdown.Option("daily", "Every day"),
                ft.dropdown.Option("workdays", "Every working day (Mon-Fri)"),
                ft.dropdown.Option("weekends", "Every weekend (Sat-Sun)"),
                ft.dropdown.Option("monthly", "Every month"),
                ft.dropdown.Option("yearly", "Every year"),
            ],
            value=recurrence_value,
            border_radius=10,
            filled=True,
        )
        
        # Task checkbox
        self.is_task_checkbox = ft.Checkbox(
            label="Mark as Task",
            value=is_task_value,
            on_change=self.toggle_task_mode
        )
        
        # ✅ ИЗМЕНЕНО: Priority для ВСЕХ событий (4 уровня)
        self.priority_dropdown = ft.Dropdown(
            label="Priority / Importance",
            options=[
                ft.dropdown.Option("Critical", "🔴 Critical"),
                ft.dropdown.Option("High", "🔥 High"),
                ft.dropdown.Option("Medium", "⚡ Medium"),
                ft.dropdown.Option("Low", "✨ Low"),
            ],
            value=priority_value,
            border_radius=10,
            filled=True,
            # ✅ visible=True всегда (убран visible=is_task_value)
        )
        
        # ===== LAYOUT =====
        
        super().__init__(
            modal=True,
            title=ft.Row([
                ft.Icon(
                    ft.Icons.EDIT_CALENDAR if self.is_editing else ft.Icons.ADD_CIRCLE_OUTLINE,
                    size=28,
                    color=ft.Colors.BLUE_600
                ),
                ft.Text(
                    "Edit Event" if self.is_editing else "Create Event",
                    size=22,
                    weight=ft.FontWeight.BOLD
                ),
            ], spacing=12),
            content=ft.Container(
                content=ft.Column(
                    [
                        # Заголовок
                        self.title_field,
                        ft.Container(height=15),
                        
                        # ✅ When - отдельный блок
                        ft.Container(
                            content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=18, color=ft.Colors.BLUE_700),
                                        ft.Text("When", size=14, weight=ft.FontWeight.BOLD, color=label_color),
                                    ], spacing=8),
                                ft.Container(height=8),
                                self.date_field,
                                ft.Container(height=8),
                                ft.Row([self.start_time_field, self.end_time_field], spacing=10),
                            ]),
                            padding=15,
                            border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.BLUE_400),
                            border=ft.border.all(1, ft.Colors.BLUE_200),
                        ),
                        
                        ft.Container(height=15),
                        
                        # ✅ Category + Priority рядом
                        ft.Row([
                            # Category
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.LABEL, size=18, color=ft.Colors.PURPLE_700),
                                        ft.Text("Category", size=14, weight=ft.FontWeight.BOLD, color=label_color),
                                    ], spacing=8),
                                    ft.Container(height=8),
                                    self.category_dropdown,
                                ]),
                                padding=15,
                                border_radius=10,
                                bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.PURPLE_400),
                                border=ft.border.all(1, ft.Colors.PURPLE_200),
                                expand=True,
                            ),
                            
                            ft.Container(width=10),
                            
                            # Priority
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.FLAG, size=18, color=ft.Colors.ORANGE_700),
                                        ft.Text("Priority", size=14, weight=ft.FontWeight.BOLD, color=label_color),
                                    ], spacing=8),
                                    ft.Container(height=8),
                                    self.priority_dropdown,
                                ]),
                                padding=15,
                                border_radius=10,
                                bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.ORANGE_400),
                                border=ft.border.all(1, ft.Colors.ORANGE_200),
                                expand=True,
                            ),
                        ], spacing=0),
                        
                        ft.Container(height=15),
                        
                        # Description
                        self.description_field,
                        ft.Container(height=15),
                        
                        # Repeat
                        self.recurrence_dropdown,
                        ft.Container(height=15),
                        
                        # ✅ Task checkbox внизу
                        ft.Container(
                            content=self.is_task_checkbox,
                            padding=10,
                            border_radius=8,
                            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREY_400),
                        ),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=500,
                height=600,
                padding=15,
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.close_dialog,
                    style=ft.ButtonStyle(
                        color=cancel_color,
                    )
                ),
                ft.ElevatedButton(
                    "Save Event" if not self.is_editing else "Update",
                    icon=ft.Icons.CHECK_CIRCLE,
                    on_click=self.save_event,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                        padding=15,
                        elevation=2,
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def toggle_task_mode(self, e):
        """✅ УПРОЩЕНО: Task checkbox теперь просто переключатель"""
        # Можно добавить дополнительную логику если нужно
        pass
    
    def change_date(self, e):
        if not self.date_picker.value:
            return
        selected = self.date_picker.value
        if isinstance(selected, datetime.datetime):
            selected = selected.date()
        self.date_field.value = selected.isoformat()
        self.date_field.update()
    
    def close_dialog(self, e):
        self.open = False
        self.page_ref.close(self)
        self.page_ref.update()
        if self.on_dismiss_callback:
            self.on_dismiss_callback()
    
    def save_event(self, e):
        # Валидация заголовка
        if not self.title_field.value:
            self.title_field.error_text = "Title is required"
            self.title_field.update()
            return
        
        # Валидация времени
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
        
        # Комбинируем дату и время
        start_dt = f"{self.date_field.value} {self.start_time_field.value}"
        end_dt = f"{self.date_field.value} {self.end_time_field.value}"
        
        if self.is_editing and self.event:
            # Обновляем существующее событие
            updates = {
                "title": self.title_field.value,
                "start": start_dt,
                "end": end_dt,
                "description": self.description_field.value,
                "category": self.category_dropdown.value,
                "type": "task" if self.is_task_checkbox.value else "event",
                "priority": self.priority_dropdown.value,  # ✅ ИЗМЕНЕНО: всегда сохраняем
                "recurrence": self.recurrence_dropdown.value if self.recurrence_dropdown.value != "none" else None
            }
            store.update_event(self.event["id"], updates)
        else:
            # Создаём новое событие
            store.add_event(
                title=self.title_field.value,
                start_date=start_dt,
                end_date=end_dt,
                description=self.description_field.value,
                category=self.category_dropdown.value,
                event_type="task" if self.is_task_checkbox.value else "event",
                priority=self.priority_dropdown.value,  # ✅ ИЗМЕНЕНО: всегда сохраняем
                recurrence=self.recurrence_dropdown.value if self.recurrence_dropdown.value != "none" else None
            )
        
        self.close_dialog(e)
