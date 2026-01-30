import flet as ft

class DietGoalDialog(ft.AlertDialog):
    """
    Диалог для изменения цели диеты.
    Показывается при клике на цель в Diet Preferences.
    """
    def __init__(self, page: ft.Page, current_goal: str, on_change):
        self.page_ref = page
        self.current_goal = current_goal
        self.on_change_callback = on_change
        self.selected_goal = current_goal
        
        # Варианты целей
        self.goals = [
            {"value": "weight_loss", "label": "⚖️ Weight Loss", "icon": ft.Icons.TRENDING_DOWN, "color": ft.Colors.ORANGE_600},
            {"value": "muscle_gain", "label": "💪 Muscle Gain", "icon": ft.Icons.FITNESS_CENTER, "color": ft.Colors.PURPLE_600},
            {"value": "healthy_lifestyle", "label": "🏃 Healthy Lifestyle", "icon": ft.Icons.FAVORITE, "color": ft.Colors.GREEN_600},
            {"value": "meal_planning", "label": "🍽️ Regular Meal Planning", "icon": ft.Icons.RESTAURANT_MENU, "color": ft.Colors.BLUE_600},
        ]
        
        # Создаём карточки выбора
        self.cards_container = ft.Column(
            controls=[],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self._render_cards()
        
        super().__init__(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.FLAG, size=24, color=ft.Colors.BLUE_600),
                ft.Text("Change Diet Goal", size=20, weight=ft.FontWeight.BOLD),
            ]),
            content=ft.Container(
                content=self.cards_container,
                width=450,
                padding=ft.padding.symmetric(vertical=10),
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.close_dialog,
                ),
                ft.ElevatedButton(
                    "Save",
                    on_click=self.save_goal,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN_600,
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def _render_cards(self):
        """Рендерит карточки выбора цели"""
        self.cards_container.controls.clear()
        
        for goal in self.goals:
            is_selected = goal["value"] == self.selected_goal
            
            card = ft.Container(
                content=ft.Row(
                    controls=[
                        # Иконка слева
                        ft.Container(
                            content=ft.Icon(
                                goal["icon"],
                                size=32,
                                color=goal["color"] if is_selected else ft.Colors.GREY_600
                            ),
                            width=50,
                            alignment=ft.alignment.center,
                        ),
                        # Текст в центре
                        ft.Text(
                            goal["label"],
                            size=16,
                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                            color=goal["color"] if is_selected else ft.Colors.GREY_700
                        ),
                        # Чекмарк справа
                        ft.Container(expand=True),
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if is_selected else ft.Icons.CIRCLE_OUTLINED,
                            size=24,
                            color=goal["color"] if is_selected else ft.Colors.GREY_400
                        ),
                    ],
                    spacing=15,
                ),
                width=400,
                padding=15,
                border=ft.border.all(
                    3 if is_selected else 2,
                    goal["color"] if is_selected else ft.Colors.GREY_300
                ),
                border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.1, goal["color"]) if is_selected else None,
                ink=True,
                on_click=lambda e, val=goal["value"]: self.select_goal(val),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT)
            )
            
            self.cards_container.controls.append(card)
    
    def select_goal(self, goal_value):
        """Выбор цели"""
        self.selected_goal = goal_value
        self._render_cards()
        self.cards_container.update()
    
    def save_goal(self, e):
        """Сохраняет новую цель"""
        if self.selected_goal != self.current_goal:
            if self.on_change_callback:
                self.on_change_callback(self.selected_goal)
        
        self.page_ref.close(self)
        self.page_ref.update()
    
    def close_dialog(self, e):
        """Закрывает диалог без сохранения"""
        self.page_ref.close(self)
        self.page_ref.update()