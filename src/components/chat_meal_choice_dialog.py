import flet as ft


class ChatMealChoiceDialog(ft.AlertDialog):
    """
    Диалог подтверждения: заменить блюдо или добавить как дополнительное.
    Работает с nutrition dict (name, calories, protein, carbs, fats).
    """

    def __init__(
        self,
        page: ft.Page,
        new_meal: dict,
        day: str,
        meal_type: str,
        existing_meal: dict,
        on_replace,
        on_add_extra,
    ):
        self.page_ref = page
        self.new_meal = new_meal or {}
        self.day = day
        self.meal_type = meal_type
        self.existing_meal = existing_meal or {}
        self.on_replace = on_replace
        self.on_add_extra = on_add_extra

        new_name = self.new_meal.get("name", "New meal")
        new_cal = self.new_meal.get("calories", "?")

        existing_name = self.existing_meal.get("name", "Existing meal")
        existing_cal = self.existing_meal.get("calories", "?")

        content = ft.Column(
            [
                ft.Text(
                    "This meal slot already has a dish.",
                    size=14,
                    color=ft.Colors.GREY_700,
                ),
                ft.Container(height=10),
                ft.Text("Current meal:", size=13, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"{existing_name} ({existing_cal} kcal)",
                    size=14,
                    color=ft.Colors.RED_500,
                ),
                ft.Container(height=10),
                ft.Text("New meal:", size=13, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"{new_name} ({new_cal} kcal)",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREEN_600,
                ),
                ft.Container(height=15),
                ft.Text(
                    f"Day: {day.capitalize()}, meal: {meal_type}",
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
            ],
            spacing=4,
            tight=True,
            width=400,
        )

        super().__init__(
            modal=True,
            title=ft.Text("Replace existing meal?", size=18, weight=ft.FontWeight.BOLD),
            content=content,
            actions=[
                ft.TextButton("Cancel", on_click=self._on_cancel),
                ft.TextButton("Add as extra", on_click=self._on_add_extra),
                ft.ElevatedButton(
                    "Replace",
                    icon=ft.Icons.SWAP_HORIZ,
                    on_click=self._on_replace,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _on_replace(self, e):
        if self.on_replace:
            self.on_replace()
        self.page_ref.close(self)

    def _on_add_extra(self, e):
        if self.on_add_extra:
            self.on_add_extra()
        self.page_ref.close(self)

    def _on_cancel(self, e):
        self.page_ref.close(self)

