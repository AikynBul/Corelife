import flet as ft
import calendar
import datetime
from data.store import store
from utils.translations import translations
from components.event_dialog import EventDialog
from components.event_details_dialog import EventDetailsDialog

class MonthView(ft.Column):
    def __init__(self, on_day_click=None):
        super().__init__()
        self.on_day_click = on_day_click
        self.expand = True
        self.current_date = datetime.date.today()
        self.filters = {"events": True, "tasks": True}
        self.events_cache = []
        self.is_loading = True # Start loading immediately, did_mount will fetch
        self.calendar_grid = ft.Column(expand=True, spacing=1)
        self.controls = [
            self.build_header(),
            self.calendar_grid
        ]
        self.render_calendar()

    def build_header(self):
        days = translations.get("weekdays_short")
        
        # Navigation Header
        month_name = translations.get("months")[self.current_date.month - 1]
        nav_header = ft.Row(
            [
                ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=self.prev_month),
                ft.Text(f"{month_name} {self.current_date.year}", size=20, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=self.next_month),
            ],
            alignment=ft.MainAxisAlignment.START
        )

        days_header = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(day, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                    expand=True,
                    alignment=ft.alignment.center
                ) for day in days
            ]
        )
        
        return ft.Column([nav_header, days_header])

    def did_mount(self):
        self.load_events()

    def load_events(self):
        self.is_loading = True
        self.render_calendar() # Show loading state
        self.page.run_task(self._fetch_events)

    async def _fetch_events(self):
        year = self.current_date.year
        month = self.current_date.month
        # Run in executor to avoid blocking main thread
        import asyncio
        loop = asyncio.get_running_loop()
        self.events_cache = await loop.run_in_executor(None, store.get_events_for_month, year, month)
        self.is_loading = False
        self.render_calendar()
        self.update()

    def render_calendar(self):
        if self.is_loading:
            self.calendar_grid.controls = [
                ft.Container(
                    content=ft.ProgressRing(),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]
            # Don't return here if called from init, but we need to ensure controls are set
            # If called from init, page might not be ready, so we just set controls
            return

        year = self.current_date.year
        month = self.current_date.month
        
        # Get calendar matrix
        cal = calendar.monthcalendar(year, month)
        
        grid_rows = []
        for week in cal:
            row_controls = []
            for day in week:
                if day == 0:
                    # Empty day from other month
                    row_controls.append(
                        ft.Container(
                            expand=True,
                            bgcolor=ft.Colors.SURFACE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_50,
                            border=ft.border.all(0.5, ft.Colors.GREY_300),
                        )
                    )
                else:
                    is_today = (day == datetime.date.today().day and 
                                month == datetime.date.today().month and 
                                year == datetime.date.today().year)
                    
                    # Filter events from cache
                    day_events = [
                        e for e in self.events_cache 
                        if int(e["start"].split(" ")[0].split("-")[2]) == day and 
                        (
                            (e.get("type") == "task" and self.filters.get("tasks", True)) or 
                            (e.get("type") != "task" and self.filters.get("events", True))
                        )
                    ]

                    day_content = ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    str(day), 
                                    size=12, 
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.ON_SURFACE if not is_today else ft.Colors.WHITE
                                ),
                                bgcolor=ft.Colors.BLUE if is_today else None,
                                border_radius=15,
                                padding=5,
                                alignment=ft.alignment.center,
                                width=30,
                                height=30,
                                margin=5
                            ),
                            # Events
                            ft.Column(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            e["title"], 
                                            size=10, 
                                            color=ft.Colors.WHITE, 
                                            no_wrap=True, 
                                            overflow=ft.TextOverflow.ELLIPSIS
                                        ),
                                        bgcolor=ft.Colors.RED_400 if e.get("type") == "task" else ft.Colors.BLUE_400,
                                        border_radius=4,
                                        padding=ft.padding.symmetric(horizontal=4, vertical=2),
                                        width=100,
                                        on_click=lambda e, ev=e: self.open_event_details(ev),
                                        ink=True,
                                    ) for e in day_events
                                ],
                                spacing=2
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=2
                    )
                    
                    row_controls.append(
                        ft.Container(
                            content=day_content,
                            expand=True,
                            bgcolor=ft.Colors.SURFACE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
                            border=ft.border.all(0.5, ft.Colors.OUTLINE_VARIANT),
                            padding=0,
                            alignment=ft.alignment.top_center,
                            on_click=lambda e, d=day, m=month, y=year: self.handle_day_click(y, m, d),
                            ink=True
                        )
                    )
            
            grid_rows.append(
                ft.Row(
                    controls=row_controls,
                    expand=True,
                    spacing=1
                )
            )
            
        self.calendar_grid.controls = grid_rows

    def prev_month(self, e):
        # Go back one month
        month = self.current_date.month - 1
        year = self.current_date.year
        if month < 1:
            month = 12
            year -= 1
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        
        # Update header text
        # Update header text
        month_name = translations.get("months")[month - 1]
        self.controls[0].controls[0].controls[1].value = f"{month_name} {year}"
        
        self.load_events()
        self.update()

    def next_month(self, e):
        # Go forward one month
        month = self.current_date.month + 1
        year = self.current_date.year
        if month > 12:
            month = 1
            year += 1
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        
        # Update header text
        # Update header text
        month_name = translations.get("months")[month - 1]
        self.controls[0].controls[0].controls[1].value = f"{month_name} {year}"
        
        self.load_events()
        self.update()

    def open_event_details(self, event):
        dialog = EventDetailsDialog(self.page, event, on_dismiss=self.refresh_calendar)
        self.page.open(dialog)

    def refresh_calendar(self):
        self.render_calendar()
        self.update()

    def update_filter(self, filters):
        self.filters = filters
        self.render_calendar()
        self.update()

    def handle_day_click(self, year, month, day):
        if self.on_day_click:
            self.on_day_click(datetime.date(year, month, day))
