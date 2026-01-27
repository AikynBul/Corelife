import flet as ft
import datetime
from data.store import store
from utils.translations import translations

class DayView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.current_date = datetime.date.today()
        self.filters = {"events": True, "tasks": True}
        self.scroll = ft.ScrollMode.AUTO
        self.scroll = ft.ScrollMode.AUTO
        # self.render_view() # Defer rendering to when view is shown

    def prev_day(self, e):
        self.current_date -= datetime.timedelta(days=1)
        self.render_view()
        self.update()

    def next_day(self, e):
        self.current_date += datetime.timedelta(days=1)
        self.render_view()
        self.update()

    def render_view(self):
        self.controls = []
        
        # Header
        header = ft.Row(
            [
                ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=self.prev_day),
                ft.Text(
                    self.current_date.strftime("%A, %B %d, %Y"),
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),
                ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=self.next_day),
            ],
            alignment=ft.MainAxisAlignment.START
        )
        self.controls.append(header)

        # Timeline Container
        PIXELS_PER_HOUR = 60
        TOTAL_HEIGHT = 24 * PIXELS_PER_HOUR
        
        timeline_stack = ft.Stack(height=TOTAL_HEIGHT, width=1000) # Ensure enough width
        
        # 1. Draw Grid Lines and Time Labels
        for hour in range(24):
            top_pos = hour * PIXELS_PER_HOUR
            
            # Time Label
            timeline_stack.controls.append(
                ft.Container(
                    content=ft.Text(f"{hour:02d}:00", size=12, color=ft.Colors.GREY),
                    top=top_pos - 8, # Center vertically relative to line
                    left=0,
                    width=50,
                    alignment=ft.alignment.center_right
                )
            )
            
            # Horizontal Line
            timeline_stack.controls.append(
                ft.Container(
                    height=1,
                    bgcolor=ft.Colors.GREY_200,
                    top=top_pos,
                    left=60,
                    right=0,
                )
            )

        # 2. Place Events
        events = store.get_events_for_month(self.current_date.year, self.current_date.month)
        day_events = [
            e for e in events 
            if int(e["start"].split(" ")[0].split("-")[2]) == self.current_date.day and
            (
                (e.get("type") == "task" and self.filters.get("tasks", True)) or 
                (e.get("type") != "task" and self.filters.get("events", True))
            )
        ]

        for e in day_events:
            try:
                # Parse Start Time
                parts = e["start"].split(" ")
                if len(parts) > 1:
                    start_str = parts[1]
                    start_hour, start_minute = map(int, start_str.split(":"))
                else:
                    start_str = "09:00" # Default start time for all-day/date-only events
                    start_hour, start_minute = 9, 0
                
                start_minutes_total = start_hour * 60 + start_minute
                
                # Parse End Time (or default to 1 hour duration)
                if "end" in e and e["end"]:
                    end_parts = e["end"].split(" ")
                    if len(end_parts) > 1:
                        end_str = end_parts[1]
                        end_hour, end_minute = map(int, end_str.split(":"))
                        end_minutes_total = end_hour * 60 + end_minute
                    else:
                        # If end date exists but no time, assume 1 hour after start or end of day?
                        # Let's just default to 1 hour after start for now
                        end_minutes_total = start_minutes_total + 60
                        end_str = f"{(start_hour + 1):02d}:{start_minute:02d}"
                else:
                    end_minutes_total = start_minutes_total + 60
                    end_str = f"{(start_hour + 1):02d}:{start_minute:02d}"
                
                duration_minutes = end_minutes_total - start_minutes_total
                if duration_minutes < 30: duration_minutes = 30 # Minimum height
                
                # Calculate Position
                top = (start_minutes_total / 60) * PIXELS_PER_HOUR
                height = (duration_minutes / 60) * PIXELS_PER_HOUR
                
                # Event Card
                event_card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(e["title"], weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.WHITE, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"{start_str} - {end_str if 'end' in e else ''}", size=10, color=ft.Colors.WHITE70),
                        ],
                        spacing=2
                    ),
                    bgcolor=ft.Colors.BLUE if e.get("type") != "task" else ft.Colors.RED_400,
                    border_radius=6,
                    padding=5,
                    top=top,
                    left=60, # After time labels
                    height=height,
                    width=200, # Fixed width for now, could be dynamic
                    on_click=lambda _, ev=e: self.show_event_details(ev),
                )
                timeline_stack.controls.append(event_card)
                
            except Exception as ex:
                print(f"Error rendering event {e.get('title')}: {ex}")
                continue

        # Wrap stack in a scrollable container
        self.controls.append(
            ft.Container(
                content=timeline_stack,
                expand=True,
                # height=500, # Let parent control height
            )
        )

    def show_event_details(self, event):
        dlg = ft.AlertDialog(
            title=ft.Text(translations.get("event_details")),
            content=ft.Column([
                ft.Text(f"{translations.get('name')}: {event['title']}", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"{translations.get('time')}: {event['start']} - {event.get('end', '')}"),
                ft.Text(f"{translations.get('description')}: {event.get('description', '')}"),
            ], tight=True),
            actions=[
                ft.TextButton(translations.get("close"), on_click=lambda e: self.close_dialog(dlg))
            ],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def close_dialog(self, dlg):
        dlg.open = False
        self.page.update()
