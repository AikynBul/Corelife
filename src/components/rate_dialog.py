import flet as ft

from data.store import store


class RateDialog(ft.AlertDialog):
    """Dialog for collecting app rating and optional feedback."""

    def __init__(self, page: ft.Page, user_info: dict):
        super().__init__()
        self.page_ref = page
        self.user_info = user_info
        self.selected_rating = 0

        # Stars with half-click support
        self.star_containers = []
        for i in range(1, 6):
            left_half = ft.Container(
                content=ft.Icon(ft.Icons.STAR_HALF, size=40, color=ft.Colors.GREY_400),
                on_click=lambda e, rating=i - 0.5: self.set_rating(rating),
                on_hover=lambda e, rating=i - 0.5: self.hover_rating(e, rating),
                width=20,
                height=40,
                ink=True,
            )

            right_half = ft.Container(
                content=ft.Icon(
                    ft.Icons.STAR_HALF,
                    size=40,
                    color=ft.Colors.GREY_400,
                ),
                on_click=lambda e, rating=float(i): self.set_rating(rating),
                on_hover=lambda e, rating=float(i): self.hover_rating(e, rating),
                width=20,
                height=40,
                ink=True,
            )

            star_container = ft.Row(
                [left_half, right_half],
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            self.star_containers.append({"left": left_half, "right": right_half, "container": star_container})

        self.comment_field = ft.TextField(
            label="What do you like? (optional)",
            multiline=True,
            min_lines=2,
            max_lines=4,
            hint_text="Tell us what you enjoy about Corelife...",
            visible=False,
        )

        self.improvements_field = ft.TextField(
            label="Suggestions for improvement (optional)",
            multiline=True,
            min_lines=2,
            max_lines=4,
            hint_text="What could we improve? Any features you'd like to see?",
            border_color=ft.Colors.BLUE_200,
            visible=False,
        )

        self.modal = True
        self.title = ft.Row(
            [
                ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER, size=28),
                ft.Text("Rate Corelife", size=20, weight=ft.FontWeight.BOLD),
            ],
            spacing=10,
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "How would you rate your experience?",
                        size=14,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        [s["container"] for s in self.star_containers],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=2,
                    ),
                    ft.Container(height=20),
                    self.comment_field,
                    ft.Container(height=10),
                    self.improvements_field,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=450,
        )

        self.actions = [
            ft.TextButton("Cancel", on_click=self.close_dialog),
            ft.ElevatedButton(
                "Submit",
                on_click=self.submit_rating,
                disabled=True,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.AMBER_600),
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def set_rating(self, rating: float):
        """Set selected rating, including .5 steps."""
        self.selected_rating = rating
        self.update_stars(rating)
        self.comment_field.visible = True
        self.improvements_field.visible = True
        self.actions[1].disabled = False
        self.safe_update()

    def hover_rating(self, e, rating: float):
        """Hover effect for star halves."""
        if e.data == "true":
            self.update_stars(rating, is_hover=True)
        else:
            self.update_stars(self.selected_rating)

    def update_stars(self, rating: float, is_hover: bool = False):
        """Refresh star halves according to selected or hovered rating."""
        for i, star_data in enumerate(self.star_containers, start=1):
            left_half = star_data["left"]
            right_half = star_data["right"]

            active_color = ft.Colors.AMBER_400 if is_hover else ft.Colors.AMBER_600
            inactive_color = ft.Colors.GREY_400

            left_half.content.color = active_color if rating >= i - 0.5 else inactive_color
            right_half.content.color = active_color if rating >= i else inactive_color

            self.safe_control_update(left_half)
            self.safe_control_update(right_half)

    def submit_rating(self, e):
        """Submit selected rating and optional notes."""
        if self.selected_rating == 0:
            return

        comment = self.comment_field.value or ""
        improvements = self.improvements_field.value or ""

        full_comment = ""
        if comment:
            full_comment += f"Likes: {comment}"
        if improvements:
            if full_comment:
                full_comment += "\n\n"
            full_comment += f"Suggestions: {improvements}"

        success = store.save_user_rating(
            user_id=self.user_info["id"],
            rating=self.selected_rating,
            comment=full_comment,
        )

        if success:
            self.show_thank_you()
        else:
            self.show_error()

    def show_thank_you(self):
        """Show thank-you state after successful submit."""
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=60),
                    ft.Container(height=20),
                    ft.Text(
                        "Thank you for your feedback!",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"You rated us {self.selected_rating}/5 *",
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

    def show_error(self):
        self.page_ref.open(
            ft.SnackBar(
                content=ft.Text("Failed to submit rating. Please try again."),
                bgcolor=ft.Colors.RED_400,
            )
        )

    def close_dialog(self, e):
        self.page_ref.close(self)

    def safe_update(self):
        try:
            self.update()
        except AssertionError:
            pass

    @staticmethod
    def safe_control_update(control):
        try:
            control.update()
        except AssertionError:
            pass
