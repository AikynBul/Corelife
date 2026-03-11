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


class WeekView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.current_date = datetime.date.today()
        self.filters = {"events": True, "tasks": True}
        self.scroll = ft.ScrollMode.AUTO
        
        # ✅ НОВОЕ: Кэш событий для оптимизации
        self.events_cache = []
        self.cache_date = None

    def render_view(self):
        """✅ ОПТИМИЗИРОВАНО: Теперь загружает события ОДИН раз для всей недели"""
        self.controls = []
        
        # Calculate start of week (Sunday)
        start_of_week = self.current_date - datetime.timedelta(days=self.current_date.weekday() + 1)
        if self.current_date.weekday() == 6: # If today is Sunday
             start_of_week = self.current_date
        
        week_dates = [start_of_week + datetime.timedelta(days=i) for i in range(7)]
        
        # ✅ КРИТИЧЕСКАЯ ОПТИМИЗАЦИЯ: Загружаем события один раз для всех месяцев недели
        self._load_week_events(week_dates)
        
        # Header Row
        header_row = ft.Row(
            controls=[ft.Container(width=50)] + [ # Time column spacer
                ft.Container(
                    content=ft.Column([
                        ft.Text(d.strftime("%a"), size=12, color=ft.Colors.GREY),
                        ft.Text(str(d.day), size=20, weight=ft.FontWeight.BOLD, 
                               color=ft.Colors.BLUE if d == datetime.date.today() else ft.Colors.GREY_900),
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
        
        # Time Column
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
             
        # Day Columns
        day_columns = []
        for d in week_dates:
            day_stack = ft.Stack(height=TOTAL_HEIGHT, expand=True)
            
            # Background Grid Lines
            for hour in range(24):
                day_stack.controls.append(
                    ft.Container(
                        height=1,
                        bgcolor=ft.Colors.GREY_300,
                        top=hour * PIXELS_PER_HOUR,
                        left=0,
                        right=0
                    )
                )
                
            # ✅ ОПТИМИЗИРОВАНО: Фильтруем события из кэша вместо запроса к БД
            day_events = self._get_day_events_from_cache(d)
            
            # Render Events
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
                    if duration_minutes < 30: 
                        duration_minutes = 30
                    
                    top = (start_minutes_total / 60) * PIXELS_PER_HOUR
                    height = (duration_minutes / 60) * PIXELS_PER_HOUR
                    base_color = get_event_color(e)
                    is_completed = e.get("completed", False)
                    event_bgcolor = ft.Colors.with_opacity(0.4, base_color) if is_completed else base_color
                    text_decoration = (
                        ft.TextDecoration.LINE_THROUGH
                        if is_completed
                        else ft.TextDecoration.NONE
                    )
                    
                    day_stack.controls.append(
                        ft.Container(
                            content=ft.Text(
                                e["title"], 
                                size=10, 
                                color=ft.Colors.WHITE, 
                                style=ft.TextStyle(decoration=text_decoration),
                                no_wrap=True, 
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            bgcolor=event_bgcolor,
                            border_radius=4,
                            padding=2,
                            top=top,
                            left=2,
                            right=2,
                            height=height,
                            on_click=lambda _, ev=e: self._show_event_details(ev)
                        )
                    )
                except Exception as ex:
                    print(f"Error rendering event {e.get('title', 'Unknown')}: {ex}")
                    continue
            
            day_columns.append(
                ft.Container(
                    content=day_stack,
                    expand=True,
                    border=ft.border.all(0.5, ft.Colors.GREY_300)
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
            )
        )
    
    def _load_week_events(self, week_dates: list):
        """
        ✅ НОВЫЙ МЕТОД: Загружает события для всей недели ОДНИМ запросом
        Результат кэшируется для быстрого доступа
        """
        # Определяем какие месяцы нужно загрузить
        months_to_load = set()
        for date in week_dates:
            months_to_load.add((date.year, date.month))
        
        # Загружаем события для всех месяцев
        self.events_cache = []
        for year, month in months_to_load:
            month_events = store.get_events_for_month(year, month)
            self.events_cache.extend(month_events)
        
        # Сохраняем дату кэша
        self.cache_date = datetime.datetime.now()
        
        print(f"✅ Week View: Loaded {len(self.events_cache)} events from {len(months_to_load)} month(s)")
    
    def _get_day_events_from_cache(self, date: datetime.date) -> list:
        """
        ✅ НОВЫЙ МЕТОД: Получает события для конкретного дня из кэша
        Намного быстрее чем запрос к БД!
        """
        day_events = []
        
        for e in self.events_cache:
            try:
                # Парсим дату события
                event_date_str = e["start"].split(" ")[0]
                event_year, event_month, event_day = map(int, event_date_str.split("-"))
                
                # Проверяем совпадение даты
                if event_year == date.year and event_month == date.month and event_day == date.day:
                    # Применяем фильтры
                    if (e.get("type") == "task" and self.filters.get("tasks", True)) or \
                       (e.get("type") != "task" and self.filters.get("events", True)):
                        day_events.append(e)
            except Exception as ex:
                print(f"Error filtering event: {ex}")
                continue
        
        return day_events
    
    def _show_event_details(self, event: dict):
        """
        ✅ НОВЫЙ МЕТОД: Показывает детали события при клике
        """
        # TODO: Открыть диалог с деталями события
        print(f"Clicked: {event.get('title', 'Unknown')}")
        print(f"  Start: {event.get('start', 'N/A')}")
        print(f"  Category: {event.get('category', 'N/A')}")
