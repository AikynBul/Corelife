import flet as ft


class ChatMealSelectionDialog(ft.AlertDialog):
    """
    Диалог для выбора блюда из AI-предложенных вариантов
    """

    def __init__(self, page: ft.Page, meals: list, on_select):
        self.page_ref = page
        self.meals = meals
        self.on_select_callback = on_select
        self.selected_meal = None

        # ✅ ИСПРАВЛЕНО: Используем RadioGroup
        meal_radios = []
        
        for i, meal in enumerate(meals):
            radio = ft.Radio(
                value=str(i),
                label=f"{meal['name']} ({meal['calories']} kcal | P:{meal['protein']}g | C:{meal['carbs']}g | F:{meal['fats']}g)",
            )
            meal_radios.append(radio)
        
        # Создаём RadioGroup
        self.radio_group = ft.RadioGroup(
            content=ft.Column(meal_radios, spacing=8),
            on_change=self.on_radio_change
        )

        # День и тип приёма пищи
        self.day_dropdown = ft.Dropdown(
            label="Day",
            options=[
                ft.dropdown.Option("monday", "Monday"),
                ft.dropdown.Option("tuesday", "Tuesday"),
                ft.dropdown.Option("wednesday", "Wednesday"),
                ft.dropdown.Option("thursday", "Thursday"),
                ft.dropdown.Option("friday", "Friday"),
                ft.dropdown.Option("saturday", "Saturday"),
                ft.dropdown.Option("sunday", "Sunday"),
            ],
            value="monday",
            width=150,
        )

        self.meal_type_dropdown = ft.Dropdown(
            label="Meal Type",
            options=[
                ft.dropdown.Option("breakfast", "Breakfast"),
                ft.dropdown.Option("lunch", "Lunch"),
                ft.dropdown.Option("dinner", "Dinner"),
                ft.dropdown.Option("snack", "Snack"),
            ],
            value="lunch",
            width=150,
        )

        confirm_btn_ref: ft.Ref[ft.ElevatedButton] = ft.Ref[ft.ElevatedButton]()

        super().__init__(
            modal=True,
            title=ft.Text("Choose Your Meal", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.Text("Select one of these options:", size=14, color=ft.Colors.GREY_700),
                    ft.Container(height=10),
                    # ✅ ИСПРАВЛЕНО: Используем RadioGroup
                    ft.Container(
                        content=self.radio_group,
                        height=250,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                        padding=10,
                    ),
                    ft.Container(height=15),
                    ft.Text(
                        "When would you like to add it?",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=5),
                    ft.Row([self.day_dropdown, self.meal_type_dropdown], spacing=10),
                ],
                spacing=5,
                tight=True,
                width=450,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.ElevatedButton(
                    "Add to Calendar",
                    icon=ft.Icons.CHECK,
                    on_click=self.confirm_selection,
                    disabled=True,  # Включается после выбора
                    ref=confirm_btn_ref,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Сохраняем ссылку на кнопку подтверждения
        self.confirm_btn = confirm_btn_ref.current
    
    def on_radio_change(self, e):
        """Обработчик изменения выбора радио-кнопки"""
        if e.control.value:
            index = int(e.control.value)
            self.select_meal(index)

    def select_meal(self, index):
        """Выбор блюда"""
        self.selected_meal = self.meals[index]
        if self.confirm_btn is not None:
            self.confirm_btn.disabled = False
            self.confirm_btn.update()

    def confirm_selection(self, e):
        """Подтверждение выбора"""
        if not self.selected_meal:
            return

        day = self.day_dropdown.value
        meal_type = self.meal_type_dropdown.value

        self.page_ref.close(self)

        if self.on_select_callback:
            self.on_select_callback(self.selected_meal, day, meal_type)

    def close_dialog(self, e):
        self.page_ref.close(self)
