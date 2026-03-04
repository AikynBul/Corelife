import flet as ft
import calendar
import datetime
from data.store import store, EventStore
from utils.translations import translations
from components.event_dialog import EventDialog
from components.event_details_dialog import EventDetailsDialog
from components.day_events_dialog import DayEventsDialog  # ✅ НОВЫЙ ИМПОРТ

# ✅ НОВОЕ: Словарь цветов для категорий событий
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
    """
    Возвращает цвет события на основе категории
    
    Args:
        event: Событие с полями category и type
    
    Returns:
        Цвет для отображения
    """
    # Задачи всегда красные
    if event.get("type") == "task":
        return ft.Colors.RED_400
    
    # Получаем цвет по категории
    category = event.get("category", "Personal")
    return CATEGORY_COLORS.get(category, ft.Colors.BLUE_400)

class MonthView(ft.Column):
    def __init__(self, on_day_click=None):
        super().__init__()
        self.on_day_click = on_day_click
        self.expand = True
        self.current_date = datetime.date.today()
        self.filters = {"events": True, "tasks": True}
        self.events_cache = []
        self.is_loading = True
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
        self.render_calendar()
        self.page.run_task(self._fetch_events)

    async def _fetch_events(self):
        year = self.current_date.year
        month = self.current_date.month
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
            return

        year = self.current_date.year
        month = self.current_date.month
        
        cal = calendar.monthcalendar(year, month)
        
        grid_rows = []
        for week in cal:
            row_controls = []
            for day in week:
                if day == 0:
                    # Пустая ячейка из другого месяца
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
                    
                    # Фильтруем события для этого дня
                    day_events = [
                        e for e in self.events_cache 
                        if int(e["start"].split(" ")[0].split("-")[2]) == day and 
                        (
                            (e.get("type") == "task" and self.filters.get("tasks", True)) or 
                            (e.get("type") != "task" and self.filters.get("events", True))
                        )
                    ]
                    
                    # ✅ НОВАЯ ЛОГИКА: Показываем максимум 2 события + индикатор
                    MAX_VISIBLE_EVENTS = 2
                    visible_events = day_events[:MAX_VISIBLE_EVENTS]
                    remaining_count = len(day_events) - MAX_VISIBLE_EVENTS
                    
                    # Создаём список контролов для событий
                    event_controls = []
                    
                    # Добавляем видимые события
                    for ev in visible_events:
                        _completed = ev.get("completed", False)
                        _color = get_event_color(ev)
                        event_controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(
                                        f"{EventStore.CATEGORIES.get(ev.get('category', 'Personal'), '📌')} {ev['title']}",
                                        size=10,
                                        color=ft.Colors.WHITE if not _completed else ft.Colors.WHITE60,
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        expand=True,
                                    ),
                                    # ✅ HABIT TRACKER: галочка если выполнено
                                    ft.Icon(
                                        ft.Icons.CHECK_CIRCLE,
                                        size=10,
                                        color=ft.Colors.WHITE,
                                        visible=_completed,
                                    ) if _completed else ft.Container(width=0),
                                ], spacing=2, tight=True),
                                # Выполненные — полупрозрачные, невыполненные — яркие
                                bgcolor=ft.Colors.with_opacity(0.4 if _completed else 1.0, _color),
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=4, vertical=2),
                                width=100,
                                on_click=lambda e, ev2=ev: self.open_event_details(ev2),
                                ink=True,
                                tooltip="✅ Completed" if _completed else None,
                            )
                        )
                    
                    # ✅ Добавляем индикатор "+N ещё" если событий больше
                    if remaining_count > 0:
                        event_controls.append(
                            ft.Container(
                                content=ft.Text(
                                    f"+{remaining_count} ещё",
                                    size=9,
                                    color=ft.Colors.PRIMARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=ft.Colors.PRIMARY_CONTAINER,
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                width=100,
                                on_click=lambda e, d=day, m=month, y=year, events=day_events: self.show_all_events(y, m, d, events),
                                ink=True,
                                tooltip=f"Показать все {len(day_events)} событий",
                            )
                        )

                    day_content = ft.Column(
                        controls=[
                            # Номер дня
                            ft.Container(
                                content=ft.Text(
                                    str(day),
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.ON_SURFACE if not is_today else ft.Colors.WHITE,
                                ),
                                bgcolor=ft.Colors.BLUE if is_today else None,
                                border_radius=15,
                                padding=5,
                                alignment=ft.alignment.center,
                                width=30,
                                height=30,
                                margin=5,
                            ),
                            # ✅ События с ограничением высоты
                            ft.Container(
                                content=ft.Column(
                                    controls=event_controls,
                                    spacing=2,
                                ),
                                # Ограничиваем высоту контейнера с событиями
                                height=70,  # Примерно 2 события + индикатор
                                alignment=ft.alignment.top_center,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=2,
                    )
                    
                    cell_bgcolor = ft.Colors.SURFACE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE
                    
                    row_controls.append(
                        ft.Container(
                            content=day_content,
                            expand=True,
                            bgcolor=cell_bgcolor,
                            border=ft.border.all(0.5, ft.Colors.GREY_300),
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
        month = self.current_date.month - 1
        year = self.current_date.year
        if month < 1:
            month = 12
            year -= 1
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        
        month_name = translations.get("months")[month - 1]
        self.controls[0].controls[0].controls[1].value = f"{month_name} {year}"
        
        self.load_events()
        self.update()

    def next_month(self, e):
        month = self.current_date.month + 1
        year = self.current_date.year
        if month > 12:
            month = 1
            year += 1
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        
        month_name = translations.get("months")[month - 1]
        self.controls[0].controls[0].controls[1].value = f"{month_name} {year}"
        
        self.load_events()
        self.update()

    def open_event_details(self, event):
        """Открывает детали одного события"""
        dialog = EventDetailsDialog(self.page, event, on_dismiss=self.refresh_calendar)
        self.page.open(dialog)

    def show_all_events(self, year, month, day, events):
        """
        ✅ НОВЫЙ МЕТОД: Открывает диалог со всеми событиями дня
        Вызывается при клике на "+N ещё"
        """
        date = datetime.date(year, month, day)
        dialog = DayEventsDialog(
            page=self.page,
            date=date,
            events=events,
            on_dismiss=self.refresh_calendar
        )
        self.page.open(dialog)

    def refresh_calendar(self):
        """Перезагружает календарь после изменений"""
        self.load_events()

    def update_filter(self, filters):
        """Обновляет фильтры событий/задач"""
        self.filters = filters
        self.render_calendar()
        self.update()

    def handle_day_click(self, year, month, day):
        """Обработчик клика на день"""
        if self.on_day_click:
            self.on_day_click(datetime.date(year, month, day))