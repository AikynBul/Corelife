import flet as ft

from data.store import store


class BugReportDialog(ft.AlertDialog):
    """Dialog for submitting user bug reports."""

    def __init__(self, page: ft.Page, user_info: dict):
        super().__init__()
        self.page_ref = page
        self.user_info = user_info

        self.bug_type_dropdown = ft.Dropdown(
            label="Issue Type",
            width=350,
            options=[
                ft.dropdown.Option("lag", "App is lagging / slow"),
                ft.dropdown.Option("crash", "App crashed / froze"),
                ft.dropdown.Option("feature_not_working", "Feature not working properly"),
                ft.dropdown.Option("visual_bug", "Visual glitch / UI issue"),
                ft.dropdown.Option("data_loss", "Lost data / events"),
                ft.dropdown.Option("login_issue", "Can't login / register"),
                ft.dropdown.Option("other", "Other issue"),
            ],
            hint_text="Select the type of issue",
        )
        self.description_field = ft.TextField(
            label="Describe the issue",
            multiline=True,
            min_lines=5,
            max_lines=10,
            hint_text=(
                "Please provide details:\n"
                "- What were you doing when it happened?\n"
                "- What did you expect to happen?\n"
                "- What actually happened?\n"
                "- Can you reproduce it?"
            ),
            border_color=ft.Colors.BLUE_200,
        )

        self.modal = True
        self.title = ft.Row(
            [
                ft.Icon(ft.Icons.BUG_REPORT, color=ft.Colors.RED_600, size=28),
                ft.Text("Report a Problem", size=20, weight=ft.FontWeight.BOLD),
            ],
            spacing=10,
        )
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Help us improve Corelife by reporting issues",
                        size=14,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Container(height=15),
                    self.bug_type_dropdown,
                    ft.Container(height=10),
                    self.description_field,
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLUE, size=16),
                            ft.Text(
                                "Your report helps us fix bugs faster!",
                                size=12,
                                color=ft.Colors.BLUE_700,
                                italic=True,
                            ),
                        ],
                        spacing=5,
                    ),
                ]
            ),
            width=450,
        )
        self.actions = [
            ft.TextButton("Cancel", on_click=self.close_dialog),
            ft.ElevatedButton(
                "Submit Report",
                icon=ft.Icons.SEND,
                on_click=self.submit_report,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_600),
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def submit_report(self, e):
        bug_type = self.bug_type_dropdown.value
        description = self.description_field.value

        if not bug_type:
            self.show_error("Please select an issue type")
            return
        if not description or len(description.strip()) < 10:
            self.show_error("Please provide a detailed description (at least 10 characters)")
            return

        success = store.save_bug_report(
            user_id=self.user_info["id"],
            bug_type=bug_type,
            description=description.strip(),
        )
        if success:
            self.show_thank_you()
        else:
            self.show_error("Failed to submit report. Please try again.")

    def show_thank_you(self):
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=60),
                    ft.Container(height=20),
                    ft.Text(
                        "Report Submitted!",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Thank you for helping us improve Corelife.\n"
                        "Our team will review your report soon.",
                        size=14,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=450,
            padding=20,
        )
        self.actions = [
            ft.ElevatedButton(
                "Close",
                on_click=self.close_dialog,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600),
            )
        ]
        self.safe_update()

    def show_error(self, message: str):
        self.page_ref.open(ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.RED_400))

    def close_dialog(self, e):
        self.page_ref.close(self)

    def safe_update(self):
        try:
            self.update()
        except AssertionError:
            # Dialog may be configured before being attached to page.
            pass
