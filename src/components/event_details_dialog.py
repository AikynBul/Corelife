import flet as ft
from data.store import store


class EventDetailsDialog(ft.AlertDialog):
    """Красивый диалог деталей события с возможностью отметить как выполненное."""

    def __init__(self, page: ft.Page, event, on_dismiss=None):
        self.page_ref = page
        self.event = event
        self.on_dismiss_callback = on_dismiss

        is_task = event.get("type") == "task"
        category = event.get("category", "Personal")
        is_completed = event.get("completed", False)

        # Цвет по категории
        from components.calendar import CATEGORY_COLORS
        accent = CATEGORY_COLORS.get(category, ft.Colors.BLUE_400)

        # Иконка
        from data.store import EventStore
        icon_emoji = EventStore.CATEGORIES.get(category, "📌")

        # Время
        start = event.get("start", "")
        end = event.get("end", "")
        time_str = ""
        if " " in start:
            time_str = start.split(" ")[1][:5]
            if end and " " in end:
                time_str += f" – {end.split(' ')[1][:5]}"
        date_str = start.split(" ")[0] if start else ""

        # Чекбокс выполнено
        self._done_checkbox = ft.Checkbox(
            value=is_completed,
            label="Mark as completed",
            active_color=ft.Colors.GREEN_600,
            on_change=self._on_completion_change,
        )

        # Статус badge
        self._status_badge = self._build_status_badge(is_completed)
        self._status_ref = ft.Ref[ft.Container]()

        type_label = "Task" if is_task else "Event"
        type_color = ft.Colors.RED_400 if is_task else accent

        content = ft.Column(
            [
                # Header strip with emoji + title
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(icon_emoji, size=32),
                            width=52, height=52,
                            border_radius=12,
                            bgcolor=ft.Colors.with_opacity(0.12, accent),
                            alignment=ft.alignment.center,
                        ),
                        ft.Column([
                            ft.Text(
                                event["title"],
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(
                                        type_label,
                                        size=11,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=type_color,
                                    border_radius=10,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        category,
                                        size=11,
                                        color=accent,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    border=ft.border.all(1, accent),
                                    border_radius=10,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                ),
                            ], spacing=6),
                        ], spacing=4, expand=True),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=8),
                ),

                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

                # Date & time row
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.GREY_500),
                    ft.Text(date_str, size=13, color=ft.Colors.GREY_700),
                    ft.Container(width=12),
                    ft.Icon(ft.Icons.ACCESS_TIME, size=16, color=ft.Colors.GREY_500),
                    ft.Text(time_str or "All day", size=13, color=ft.Colors.GREY_700),
                ], spacing=4),

                # Description
                ft.Container(
                    content=ft.Column([
                        ft.Text("Description", size=12,
                                color=ft.Colors.GREY_500, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            event.get("description") or "No description",
                            size=14,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ], spacing=4),
                    padding=ft.padding.symmetric(vertical=8),
                ),

                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),

                # Completion section
                ft.Container(
                    content=ft.Row([
                        self._done_checkbox,
                        ft.Container(expand=True),
                        self._status_badge,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=4),
                ),
            ],
            spacing=8,
            tight=True,
            width=420,
        )

        super().__init__(
            modal=True,
            title=None,
            content=ft.Container(content=content, padding=16),
            actions=[
                ft.TextButton(
                    "Edit",
                    icon=ft.Icons.EDIT_OUTLINED,
                    on_click=self.edit_event,
                    style=ft.ButtonStyle(color=ft.Colors.BLUE_600),
                ),
                ft.TextButton(
                    "Delete",
                    icon=ft.Icons.DELETE_OUTLINE,
                    on_click=self.delete_event,
                    style=ft.ButtonStyle(color=ft.Colors.RED_400),
                ),
                ft.ElevatedButton(
                    "Close",
                    on_click=self.close_dialog,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600,
                        padding=ft.padding.symmetric(horizontal=20),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=16),
        )

    def _build_status_badge(self, completed: bool):
        if completed:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color=ft.Colors.WHITE),
                    ft.Text("Done", size=12, color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD),
                ], spacing=4, tight=True),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
            )
        else:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.RADIO_BUTTON_UNCHECKED, size=14,
                            color=ft.Colors.GREY_500),
                    ft.Text("Pending", size=12, color=ft.Colors.GREY_500),
                ], spacing=4, tight=True),
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
            )

    def _on_completion_change(self, e):
        """Обновляет статус выполнения в БД и обновляет badge."""
        completed = e.control.value
        event_id = self.event.get("id")
        if event_id:
            store.mark_event_completed(event_id, completed)
            self.event["completed"] = completed

        # Обновляем badge
        new_badge = self._build_status_badge(completed)
        # Заменяем старый badge в Row
        try:
            completion_row = self.content.content.controls[-1].content
            completion_row.controls[-1] = new_badge
            completion_row.update()
        except Exception:
            pass

        # Уведомляем календарь об изменении
        if self.on_dismiss_callback:
            self.on_dismiss_callback()

    def edit_event(self, e):
        from components.event_dialog import EventDialog
        self.page_ref.close(self)
        edit_dialog = EventDialog(
            self.page_ref,
            on_dismiss=self.on_dismiss_callback,
            event=self.event
        )
        self.page_ref.open(edit_dialog)
        self.page_ref.update()

    def delete_event(self, e):
        store.delete_event(self.event["id"])
        self.page_ref.close(self)
        self.page_ref.update()
        if self.on_dismiss_callback:
            self.on_dismiss_callback()

    def close_dialog(self, e):
        self.page_ref.close(self)
        self.page_ref.update()
        if self.on_dismiss_callback:
            self.on_dismiss_callback()  