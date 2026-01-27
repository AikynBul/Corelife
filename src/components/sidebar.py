import flet as ft
import datetime
import calendar
from components.event_dialog import EventDialog
from utils.translations import translations

class Sidebar(ft.Container):
    def __init__(self, on_view_change=None, on_filter_change=None, on_refresh=None):
        super().__init__()
        self.on_view_change = on_view_change
        self.on_filter_change = on_filter_change
        self.on_refresh = on_refresh
        self.width = 250
        self.padding = 10
        self.current_date = datetime.date.today()
        self.content = ft.Column(
            controls=[
                self.build_create_button(),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.build_view_switcher(),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.build_mini_calendar(),
                ft.Divider(),
                self.build_my_calendars(),
            ]
        )

    def build_view_switcher(self):
        return ft.Column(
            [
                ft.TextButton(translations.get("month_view"), on_click=lambda e: self.on_view_change("Month") if self.on_view_change else None, icon=ft.Icons.CALENDAR_MONTH),
                ft.TextButton(translations.get("week_view"), on_click=lambda e: self.on_view_change("Week") if self.on_view_change else None, icon=ft.Icons.VIEW_WEEK),
                ft.TextButton(translations.get("day_view"), on_click=lambda e: self.on_view_change("Day") if self.on_view_change else None, icon=ft.Icons.TODAY),
            ]
        )

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
        # Simple static mini calendar for now
        today = datetime.date.today()
        cal = calendar.monthcalendar(today.year, today.month)
        
        month_name = translations.get("months")[today.month - 1]
        
        rows = [
            ft.Text(f"{month_name} {today.year}", weight=ft.FontWeight.BOLD, size=14),
            ft.Row([ft.Text(d, size=10, width=20, text_align=ft.TextAlign.CENTER) for d in ["S", "M", "T", "W", "T", "F", "S"]], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]
        
        for week in cal:
            week_row = []
            for day in week:
                if day == 0:
                    week_row.append(ft.Container(width=20))
                else:
                    is_today = day == self.current_date.day and self.current_date.month == datetime.date.today().month and self.current_date.year == datetime.date.today().year
                    week_row.append(
                        ft.Container(
                            content=ft.Text(str(day), size=10, color=ft.Colors.ON_PRIMARY if is_today else None),
                            width=20,
                            height=20,
                            bgcolor=ft.Colors.PRIMARY if is_today else None,
                            border_radius=10,
                            alignment=ft.alignment.center,
                        )
                    )
            rows.append(ft.Row(week_row, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        return ft.Column(rows, spacing=5)

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
