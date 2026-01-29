import flet as ft
from data.store import store

class EventDetailsDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, event, on_dismiss=None):
        self.page_ref = page
        self.event = event
        self.on_dismiss_callback = on_dismiss
        
        super().__init__(
            modal=True,
            title=ft.Text(event["title"]),
            content=ft.Column(
                [
                    ft.Text(f"Date: {event['start']}"),
                    ft.Text(f"Description: {event['description'] or 'No description'}"),
                ],
                width=400,
                height=200,
                tight=True
            ),
            actions=[
                ft.TextButton("Edit", on_click=self.edit_event, style=ft.ButtonStyle(color=ft.Colors.BLUE)),
                ft.TextButton("Delete", on_click=self.delete_event, style=ft.ButtonStyle(color=ft.Colors.RED)),
                ft.TextButton("Close", on_click=self.close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def edit_event(self, e):
        from components.event_dialog import EventDialog
        
        # Закрываем текущий диалог
        self.page_ref.close(self)
        
        # Открываем диалог редактирования с предзаполненными данными
        edit_dialog = EventDialog(
            self.page_ref,
            on_dismiss=self.on_dismiss_callback,
            event=self.event  # Передаём существующее событие
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
