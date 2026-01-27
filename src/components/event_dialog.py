import flet as ft
import datetime
from data.store import store

class EventDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, on_dismiss=None):
        self.page_ref = page
        self.on_dismiss_callback = on_dismiss
        
        self.title_field = ft.TextField(label="Add title", autofocus=True, text_size=20, border=ft.InputBorder.UNDERLINE)
        
        # Date Picker
        self.date_picker = ft.DatePicker(
            on_change=self.change_date,
            first_date=datetime.datetime(2023, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )
        
        self.date_field = ft.TextField(
            label="Date",
            value=datetime.date.today().isoformat(),
            read_only=True,
            expand=True,
            suffix=ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                tooltip="Pick date",
                on_click=lambda _: self.page_ref.open(self.date_picker),
            ),
        )

        # Manual Time Fields
        self.start_time_field = ft.TextField(
            label="Start Time",
            value="09:00",
            hint_text="HH:MM",
            expand=True
        )
        
        self.end_time_field = ft.TextField(
            label="End Time",
            value="10:00",
            hint_text="HH:MM",
            expand=True
        )

        self.description_field = ft.TextField(label="Description", multiline=True, min_lines=3)
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
            value="none"
        )
        self.is_task_checkbox = ft.Checkbox(label="Mark as Task", value=False)
        
        super().__init__(
            modal=True,
            title=ft.Text("Add Event"),
            content=ft.Column(
                [
                    self.title_field,
                    ft.Row([self.date_field]),
                    ft.Row([self.start_time_field, self.end_time_field]),
                    self.description_field,
                    self.recurrence_dropdown,
                    self.is_task_checkbox
                ],
                width=400,
                height=400,
                tight=True
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Save", on_click=self.save_event),
            ],
        )

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
        if not self.title_field.value:
            self.title_field.error_text = "Title is required"
            self.title_field.update()
            return
            
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
            
        store.add_event(
            title=self.title_field.value,
            start_date=start_dt,
            end_date=end_dt,
            description=self.description_field.value,
            event_type="task" if self.is_task_checkbox.value else "event",
            recurrence=self.recurrence_dropdown.value if self.recurrence_dropdown.value != "none" else None
        )
        self.close_dialog(e)
