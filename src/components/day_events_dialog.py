import flet as ft
from data.store import store, EventStore


class DayEventsDialog(ft.AlertDialog):
    """
    Диалог списка событий дня — habit tracker стиль.
    Рядом с каждым событием — квадрат-чекбокс для отметки выполнения.
    """

    def __init__(self, page: ft.Page, date, events, on_dismiss=None):
        self.page_ref = page
        self.date = date
        self.events = events
        self.on_dismiss_callback = on_dismiss
        self._event_rows = {}   # event_id -> (checkbox_ref, row_container_ref)

        from utils.translations import translations
        day = self.date.day
        month_name = translations.get("months")[self.date.month - 1]
        year = self.date.year

        events_list = ft.Column(
            controls=[self._create_event_row(ev) for ev in self.events],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

        super().__init__(
            modal=True,
            title=ft.Row([
                ft.Container(
                    content=ft.Text(str(day), size=22, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.BLUE_600,
                    border_radius=12,
                    width=44, height=44,
                    alignment=ft.alignment.center,
                ),
                ft.Column([
                    ft.Text(f"{month_name} {year}", size=16,
                            weight=ft.FontWeight.BOLD),
                    ft.Text(f"{len(events)} event{'s' if len(events) != 1 else ''}",
                            size=12, color=ft.Colors.GREY_500),
                ], spacing=0),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            content=ft.Container(
                content=events_list,
                width=480,
                height=min(60 + len(events) * 72, 450),
                padding=4,
            ),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=self.close_dialog,
                    style=ft.ButtonStyle(color=ft.Colors.PRIMARY),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=16),
        )

    def _create_event_row(self, event):
        """Карточка события с квадратом-чекбоксом для habit tracking."""
        from components.calendar import CATEGORY_COLORS

        category = event.get("category", "Personal")
        is_task = event.get("type") == "task"
        is_completed = event.get("completed", False)

        accent = CATEGORY_COLORS.get(category, ft.Colors.BLUE_400)
        if is_task:
            accent = ft.Colors.RED_400
        icon_emoji = EventStore.CATEGORIES.get(category, "📌")

        # Время
        start = event.get("start", "")
        time_str = "All day"
        if " " in start:
            time_str = start.split(" ")[1][:5]

        event_id = event.get("id", "")

        # Чекбокс-квадрат (habit tracker ячейка)
        checkbox = ft.Checkbox(
            value=is_completed,
            active_color=ft.Colors.GREEN_600,
            check_color=ft.Colors.WHITE,
            on_change=lambda e, ev=event: self._toggle_completion(e, ev),
        )

        # Контейнер строки (будет обновляться при изменении статуса)
        row_container = ft.Container(
            content=ft.Row([
                # Левая полоска-акцент
                ft.Container(
                    width=4,
                    border_radius=ft.border_radius.only(top_left=8, bottom_left=8),
                    bgcolor=ft.Colors.with_opacity(0.4 if is_completed else 1.0, accent),
                    height=56,
                ),
                # Иконка
                ft.Container(
                    content=ft.Text(icon_emoji, size=22,
                                    opacity=0.4 if is_completed else 1.0),
                    width=40,
                    alignment=ft.alignment.center,
                ),
                # Контент
                ft.Column([
                    ft.Text(
                        event["title"],
                        size=14,
                        weight=ft.FontWeight.W_500,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        opacity=0.45 if is_completed else 1.0,
                        spans=[ft.TextSpan(
                            style=ft.TextStyle(
                                decoration=ft.TextDecoration.LINE_THROUGH
                                if is_completed else ft.TextDecoration.NONE
                            )
                        )],
                    ),
                    ft.Row([
                        ft.Icon(ft.Icons.ACCESS_TIME, size=12,
                                color=ft.Colors.GREY_400),
                        ft.Text(time_str, size=11, color=ft.Colors.GREY_500),
                        ft.Container(width=6),
                        ft.Container(
                            content=ft.Text(
                                category, size=10,
                                color=ft.Colors.WHITE if not is_completed else ft.Colors.GREY_400,
                                weight=ft.FontWeight.W_500,
                            ),
                            bgcolor=ft.Colors.with_opacity(
                                0.3 if is_completed else 0.85, accent),
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        ),
                    ], spacing=4),
                ], spacing=3, expand=True),
                # Habit tracker квадрат (справа)
                ft.Container(
                    content=checkbox,
                    width=48,
                    alignment=ft.alignment.center,
                ),
            ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(
                0.04 if is_completed else 0.07, accent),
            border=ft.border.all(
                1, ft.Colors.with_opacity(0.2 if is_completed else 0.35, accent)),
            border_radius=10,
            padding=ft.padding.only(right=4),
            ink=True,
            on_click=lambda e, ev=event: self._open_details(ev),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

        self._event_rows[event_id] = (checkbox, row_container, event)
        return row_container

    def _toggle_completion(self, e, event):
        """Отметить/снять отметку выполнения — обновить в БД и перерисовать строку."""
        completed = e.control.value
        event_id = event.get("id", "")

        recurrence = event.get("recurrence")
        date_str = (event.get("start") or "").split(" ")[0]
        if recurrence and recurrence != "none":
            store.mark_recurring_completion(event_id, date_str, completed)
        else:
            store.mark_event_completed(event_id, completed)
        event["completed"] = completed

        # Перестраиваем строку с новым статусом
        new_row = self._create_event_row(event)
        if event_id in self._event_rows:
            _, old_container, _ = self._event_rows[event_id]
            # Найдём позицию в Column
            col = self.content.content
            for i, ctrl in enumerate(col.controls):
                if ctrl is old_container:
                    col.controls[i] = new_row
                    col.update()
                    break

        # Уведомить календарь (он перерисует ячейку)
        if self.on_dismiss_callback:
            self.on_dismiss_callback()

    def _open_details(self, event):
        """Открыть детальный диалог события."""
        from components.event_details_dialog import EventDetailsDialog
        self.page_ref.close(self)
        details = EventDetailsDialog(
            self.page_ref, event,
            on_dismiss=self.on_dismiss_callback
        )
        self.page_ref.open(details)
        self.page_ref.update()

    def close_dialog(self, e):
        self.page_ref.close(self)
        self.page_ref.update()
        if self.on_dismiss_callback:
            self.on_dismiss_callback()
