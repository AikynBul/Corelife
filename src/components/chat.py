import flet as ft
from datetime import datetime, timedelta
from data.store import store
import re

class ChatWidget(ft.Column):
    def __init__(self, page: ft.Page, on_refresh=None):
        super().__init__()
        self.page_ref = page
        self.on_refresh = on_refresh
        self.horizontal_alignment = ft.CrossAxisAlignment.END
        self.spacing = 10
        
        self.chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.input_field = ft.TextField(
            hint_text="Ask me to schedule something...",
            expand=True,
            on_submit=self.send_message,
            border_radius=20,
            content_padding=10,
            text_style=ft.TextStyle(color=ft.Colors.BLACK),
            cursor_color=ft.Colors.BLACK,
            hint_style=ft.TextStyle(color=ft.Colors.GREY_600)
        )
        
        self.chat_window = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text("AI Assistant", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE,
                        padding=10,
                        border_radius=ft.border_radius.only(top_left=10, top_right=10)
                    ),
                    ft.Container(
                        content=self.chat_history,
                        expand=True,
                        padding=10,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                self.input_field,
                                ft.IconButton(ft.Icons.SEND, on_click=self.send_message, icon_color=ft.Colors.BLUE)
                            ]
                        ),
                        padding=10,
                        border=ft.border.only(top=ft.border.BorderSide(1, ft.Colors.GREY_300))
                    )
                ],
                spacing=0
            ),
            width=350,
            height=500,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
            visible=False,
            animate_opacity=300,
        )

        self.fab = ft.FloatingActionButton(
            icon=ft.Icons.CHAT,
            on_click=self.toggle_chat,
            bgcolor=ft.Colors.BLUE,
        )

        self.controls = [
            self.chat_window,
            self.fab
        ]
        
        # Initial greeting
        self.add_message("Hello! I can help you manage your calendar. Try saying 'Meeting with John tomorrow at 2pm'.", is_user=False, update=False)

    def toggle_chat(self, e):
        self.chat_window.visible = not self.chat_window.visible
        self.update()

    def add_message(self, text, is_user=True, update=True):
        self.chat_history.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(text, color=ft.Colors.WHITE if is_user else ft.Colors.BLACK),
                        bgcolor=ft.Colors.BLUE if is_user else ft.Colors.GREY_200,
                        padding=10,
                        border_radius=10,
                        width=250 if len(text) > 30 else None
                    )
                ],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            )
        )
        if update:
            self.update()

    def send_message(self, e):
        text = self.input_field.value
        if not text:
            return
        
        self.add_message(text, is_user=True)
        self.input_field.value = ""
        self.update()
        
        # Process command
        self.process_command(text)

    def process_command(self, text):
        # Enhanced parsing logic
        try:
            title = "New Event"
            target_date = datetime.now()
            hour = 9
            
            lower_text = text.lower()
            
            # Parse relative days
            if "tomorrow" in lower_text:
                target_date += timedelta(days=1)
                title = lower_text.split("tomorrow")[0].strip()
            elif "today" in lower_text:
                target_date = datetime.now()
                title = lower_text.split("today")[0].strip()
            elif "next week" in lower_text:
                target_date += timedelta(weeks=1)
                title = lower_text.split("next week")[0].strip()
            elif "in" in lower_text and "days" in lower_text:
                # "in 3 days"
                days_match = re.search(r"in (\d+) days", lower_text)
                if days_match:
                    days = int(days_match.group(1))
                    target_date += timedelta(days=days)
                    title = lower_text.split("in")[0].strip()
            
            # Parse time
            time_match = re.search(r"at (\d+)", lower_text)
            if time_match:
                hour = int(time_match.group(1))
                if hour < 8: 
                    hour += 12
            
            # Clean up title
            title = title.replace("schedule", "").replace("add", "").replace("create", "").strip()
            if not title:
                title = "New Event"
            
            # Format with time
            start_str = f"{target_date.year}-{target_date.month:02d}-{target_date.day:02d} {hour:02d}:00"
            
            # Determine type
            event_type = "task" if "remind" in lower_text or "task" in lower_text else "event"
            
            # Create event
            store.add_event(
                title=title.title(),
                start_date=start_str,
                end_date=start_str,
                description=f"Created via AI from: '{text}'",
                event_type=event_type
            )
            
            type_str = "Task" if event_type == "task" else "Event"
            self.add_message(f"I've scheduled {type_str} '{title.title()}' for {start_str} at {hour}:00.", is_user=False)
            
            if self.on_refresh:
                self.on_refresh()
            else:
                self.page_ref.update()
            
        except Exception as e:
            self.add_message("Sorry, I didn't understand that. Try 'Meeting tomorrow at 10' or 'Lunch in 3 days'.", is_user=False)
            print(e)
