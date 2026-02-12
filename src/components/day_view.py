import flet as ft
import datetime
from data.store import store
from utils.translations import translations

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
        
        # ✅ НОВОЕ: Группируем пересекающиеся события
        grouped_events = group_overlapping_events(day_events)

        for e in grouped_events:
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
                
                # ✅ НОВОЕ: Вычисляем left и width на основе колонок
                column = e.get("column", 0)
                total_columns = e.get("total_columns", 1)
                
                AVAILABLE_WIDTH = 900  # Доступная ширина после времени
                column_width = AVAILABLE_WIDTH / total_columns
                left = 60 + (column * column_width)
                width = column_width - 5  # 5px отступ между колонками
                
                # Event Card
                event_card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(e["title"], weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.WHITE, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"{start_str} - {end_str if 'end' in e else ''}", size=10, color=ft.Colors.WHITE70),
                        ],
                        spacing=2
                    ),
                    bgcolor=get_event_color(e),  # ✅ ИЗМЕНЕНО: используем цвет по категории
                    border_radius=6,
                    padding=5,
                    top=top,
                    left=left,  # ✅ ИЗМЕНЕНО: динамический left
                    height=height,
                    width=width,  # ✅ ИЗМЕНЕНО: динамический width
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