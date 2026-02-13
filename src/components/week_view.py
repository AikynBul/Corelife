import flet as ft
import datetime
from data.store import store

# ✅ НОВОЕ: Цвета для категорий (копия из calendar.py)
CATEGORY_COLORS = {
    "Routine": ft.Colors.GREY_600,
    "Sleep": ft.Colors.INDIGO_400,
    "Food": ft.Colors.ORANGE_600,
    "Study": ft.Colors.BLUE_600,
    "Exercise": ft.Colors.GREEN_600,
    "Work": ft.Colors.BLUE_GREY_600,
    "Social": ft.Colors.PINK_400,
    "Health": ft.Colors.RED_600,
    "Personal": ft.Colors.PURPLE_600,
    "Entertainment": ft.Colors.CYAN_400,
}

def get_event_color(event: dict) -> str:
    """Возвращает цвет события на основе категории"""
    # Задачи всегда красные
    if event.get("type") == "task":
        return ft.Colors.RED_400
    
    # Получаем цвет по категории
    category = event.get("category", "Personal")
    return CATEGORY_COLORS.get(category, ft.Colors.BLUE_400)


def group_overlapping_events(events: list) -> list:
    """
    Группирует пересекающиеся события для отображения рядом
    
    Returns:
        list: Список событий с дополнительными полями:
            - column: номер колонки (0, 1, 2...)
            - total_columns: всего колонок в группе
    """
    # Сортируем по времени начала
    sorted_events = sorted(events, key=lambda e: e.get("start", ""))
    
    # Результат
    result = []
    
    for event in sorted_events:
        # Парсим время события
        try:
            start_parts = event["start"].split(" ")
            if len(start_parts) > 1:
                time_parts = start_parts[1].split(":")
                event_start_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
            else:
                event_start_minutes = 0
            
            # Вычисляем конец
            if "end" in event and " " in event["end"]:
                end_parts = event["end"].split(" ")
                if len(end_parts) > 1:
                    time_parts = end_parts[1].split(":")
                    event_end_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
                else:
                    event_end_minutes = event_start_minutes + 60
            else:
                event_end_minutes = event_start_minutes + 60
            
            # Проверяем пересечения с уже размещёнными
            column = 0
            max_columns = 1
            
            for placed in result:
                placed_start = placed["_start_minutes"]
                placed_end = placed["_end_minutes"]
                
                # Проверяем пересечение
                if not (event_end_minutes <= placed_start or event_start_minutes >= placed_end):
                    # Есть пересечение
                    if placed["column"] == column:
                        column += 1
                    
                    if placed["total_columns"] > max_columns:
                        max_columns = placed["total_columns"]
            
            # Сохраняем данные
            event["column"] = column
            event["total_columns"] = max(column + 1, max_columns)
            event["_start_minutes"] = event_start_minutes
            event["_end_minutes"] = event_end_minutes
            
            # Обновляем total_columns для пересекающихся
            for placed in result:
                placed_start = placed["_start_minutes"]
                placed_end = placed["_end_minutes"]
                
                if not (event_end_minutes <= placed_start or event_start_minutes >= placed_end):
                    placed["total_columns"] = max(placed["total_columns"], event["total_columns"])
                    event["total_columns"] = max(placed["total_columns"], event["total_columns"])
            
            result.append(event)
        
        except Exception as ex:
            print(f"Error grouping event {event.get('title')}: {ex}")
            event["column"] = 0
            event["total_columns"] = 1
            event["_start_minutes"] = 0
            event["_end_minutes"] = 60
            result.append(event)
    
    return result

class WeekView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.current_date = datetime.date.today()
        self.filters = {"events": True, "tasks": True}
        self.scroll = ft.ScrollMode.AUTO
        self.scroll = ft.ScrollMode.AUTO
        # self.render_view() # Defer rendering to when view is shown

    def render_view(self):
        self.controls = []
        
        # Calculate start of week (Sunday)
        start_of_week = self.current_date - datetime.timedelta(days=self.current_date.weekday() + 1)
        if self.current_date.weekday() == 6: # If today is Sunday
             start_of_week = self.current_date
        
        week_dates = [start_of_week + datetime.timedelta(days=i) for i in range(7)]
        
        # Header Row
        header_row = ft.Row(
            controls=[ft.Container(width=50)] + [ # Time column spacer
                ft.Container(
                    content=ft.Column([
                        ft.Text(d.strftime("%a"), size=12, color=ft.Colors.GREY),
                        ft.Text(str(d.day), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE if d == datetime.date.today() else ft.Colors.ON_SURFACE),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                    expand=True,
                    alignment=ft.alignment.center,
                    padding=10
                ) for d in week_dates
            ],
            spacing=0
        )
        self.controls.append(header_row)
        self.controls.append(ft.Divider(height=1, thickness=1))

        # Timeline Container
        PIXELS_PER_HOUR = 60
        TOTAL_HEIGHT = 24 * PIXELS_PER_HOUR
        
        # Use a Stack for the entire grid
        timeline_stack = ft.Stack(height=TOTAL_HEIGHT)
        
        # 1. Draw Grid Lines and Time Labels
        for hour in range(24):
            top_pos = hour * PIXELS_PER_HOUR
            
            # Time Label
            timeline_stack.controls.append(
                ft.Container(
                    content=ft.Text(f"{hour:02d}:00", size=10, color=ft.Colors.GREY),
                    top=top_pos - 6,
                    left=0,
                    width=50,
                    alignment=ft.alignment.center_right,
                    padding=ft.padding.only(right=5)
                )
            )
            
            # Horizontal Line
            timeline_stack.controls.append(
                ft.Container(
                    height=1,
                    bgcolor=ft.Colors.GREY_200,
                    top=top_pos,
                    left=50,
                    right=0,
                )
            )

        # Vertical Lines for Days
        # We need to calculate width of each day column. 
        # In a Stack, we can't easily use "expand". 
        # We might need to use a Row of Stacks, or just assume fixed width / percentage.
        # A better approach for WeekView in Flet might be a Row of 8 Columns (Time + 7 Days).
        # Each Day Column is a Stack.
        
        # Let's switch strategy: Row of Columns.
        
        time_column = ft.Column(spacing=0, width=50)
        for hour in range(24):
             time_column.controls.append(
                 ft.Container(
                     content=ft.Text(f"{hour:02d}:00", size=10, color=ft.Colors.GREY),
                     height=PIXELS_PER_HOUR,
                     alignment=ft.alignment.top_right,
                     padding=ft.padding.only(right=5)
                 )
             )
             
        day_columns = []
        for d in week_dates:
            day_stack = ft.Stack(height=TOTAL_HEIGHT, expand=True)
            
            # Background Grid Lines
            for hour in range(24):
                day_stack.controls.append(
                    ft.Container(
                        height=1,
                        bgcolor=ft.Colors.GREY_200,
                        top=hour * PIXELS_PER_HOUR,
                        left=0,
                        right=0
                    )
                )
                
            # Events
            # Fetch events for this month (optimization: cache or fetch range)
            # For now, just fetch month.
            events = store.get_events_for_month(d.year, d.month)
            day_events = [
                e for e in events 
                if int(e["start"].split(" ")[0].split("-")[2]) == d.day and
                (
                    (e.get("type") == "task" and self.filters.get("tasks", True)) or 
                    (e.get("type") != "task" and self.filters.get("events", True))
                )
            ]
            
            for e in day_events:
                try:
                    start_str = e["start"].split(" ")[1]
                    start_hour, start_minute = map(int, start_str.split(":"))
                    start_minutes_total = start_hour * 60 + start_minute
                    
                    if "end" in e and e["end"]:
                        end_str = e["end"].split(" ")[1]
                        end_hour, end_minute = map(int, end_str.split(":"))
                        end_minutes_total = end_hour * 60 + end_minute
                    else:
                        end_minutes_total = start_minutes_total + 60
                    
                    duration_minutes = end_minutes_total - start_minutes_total
                    if duration_minutes < 30: duration_minutes = 30
                    
                    top = (start_minutes_total / 60) * PIXELS_PER_HOUR
                    height = (duration_minutes / 60) * PIXELS_PER_HOUR
                    
                    day_stack.controls.append(
                        ft.Container(
                            content=ft.Text(e["title"], size=10, color=ft.Colors.WHITE, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            bgcolor=get_event_color(e),  # ✅ ИСПРАВЛЕНО: event → e
                            border_radius=4,
                            padding=2,
                            top=top,
                            left=2,
                            right=2,
                            height=height,
                            on_click=lambda _, ev=e: print(f"Clicked {ev['title']}")
                        )
                    )
                except:
                    continue
            
            day_columns.append(
                ft.Container(
                    content=day_stack,
                    expand=True,
                    border=ft.border.all(0.5, ft.Colors.GREY_200)
                )
            )
            
        self.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[time_column] + day_columns,
                    spacing=0,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.START
                ),
                expand=True,
                # height=500 # Let parent control
            )
        )