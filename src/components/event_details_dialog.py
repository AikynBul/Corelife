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
                ft.TextButton("Delete", on_click=self.delete_event, style=ft.ButtonStyle(color=ft.Colors.RED)),
                ft.TextButton("Close", on_click=self.close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def delete_event(self, e):
        store.delete_event(self.event["id"])
        self.page_ref.close(self)
        self.page_ref.update()
        if self.on_dismiss_callback:
            self.on_dismiss_callback()

    def close_dialog(self, e):
        self.page_ref.close(self)
        self.page_ref.update()
