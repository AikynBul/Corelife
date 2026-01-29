import flet as ft
from data.store import store, EventStore

class DayEventsDialog(ft.AlertDialog):
    """
    Диалог для показа всех событий конкретного дня
    Используется когда пользователь кликает на "+N ещё" в календаре
    """
    def __init__(self, page: ft.Page, date, events, on_dismiss=None):
        self.page_ref = page
        self.date = date  # datetime.date объект
        self.events = events
        self.on_dismiss_callback = on_dismiss
        
        # Форматируем дату для заголовка
        from utils.translations import translations
        day = self.date.day
        month_name = translations.get("months")[self.date.month - 1]
        year = self.date.year
        
        # Создаём список событий
        events_list = ft.Column(
            controls=[
                self._create_event_card(event)
                for event in self.events
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )
        
        super().__init__(
            modal=True,
            title=ft.Text(f"📅 {day} {month_name} {year}", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=events_list,
                width=450,
                height=400,
                padding=10,
            ),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=self.close_dialog,
                    style=ft.ButtonStyle(
                        color=ft.Colors.PRIMARY,
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _create_event_card(self, event):
        """Создаёт красивую карточку события"""
        # Получаем иконку категории
        category = event.get("category", "Personal")
        icon = EventStore.CATEGORIES.get(category, "📌")
        
        # Определяем цвет в зависимости от типа
        is_task = event.get("type") == "task"
        card_color = ft.Colors.RED_100 if is_task else ft.Colors.BLUE_100
        text_color = ft.Colors.RED_900 if is_task else ft.Colors.BLUE_900
        
        # Извлекаем время
        start_time = "Весь день"
        if " " in event.get("start", ""):
            start_time = event["start"].split(" ")[1][:5]  # HH:MM
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Иконка и время слева
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(icon, size=24),
                                ft.Text(
                                    start_time,
                                    size=11,
                                    color=ft.Colors.GREY_700,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=2,
                        ),
                        width=60,
                        alignment=ft.alignment.center,
                    ),
                    
                    # Вертикальная линия
                    ft.Container(
                        width=2,
                        height=50,
                        bgcolor=ft.Colors.GREY_300,
                    ),
                    
                    # Контент события справа
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    event["title"],
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=text_color,
                                ),
                                ft.Text(
                                    event.get("description", "") or "Нет описания",
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            spacing=4,
                        ),
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=card_color,
            border_radius=8,
            padding=12,
            ink=True,
            on_click=lambda e, ev=event: self.open_event_details(ev),
        )
    
    def open_event_details(self, event):
        """Открывает детали события"""
        from components.event_details_dialog import EventDetailsDialog
        
        # Закрываем текущий диалог
        self.page_ref.close(self)
        
        # Открываем диалог деталей
        details_dialog = EventDetailsDialog(
            self.page_ref,
            event,
            on_dismiss=self.on_dismiss_callback
        )
        self.page_ref.open(details_dialog)
        self.page_ref.update()
    
    def close_dialog(self, e):
        """Закрывает диалог"""
        self.page_ref.close(self)
        self.page_ref.update()
        if self.on_dismiss_callback:
            self.on_dismiss_callback()