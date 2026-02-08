import flet as ft
from data.store import store
from components.diet_goal_dialog import DietGoalDialog

class DietView(ft.Column):
    """
    Страница диеты с AI генерацией планов питания.
    """
    def __init__(self, page: ft.Page, user_info: dict):
        super().__init__()
        self.page_ref = page
        self.user_info = user_info
        
        self.expand = True
        self.spacing = 20
        self.scroll = ft.ScrollMode.AUTO
        
        # Получаем предпочтения из БД
        self.preferences = store.get_diet_preferences(user_info["id"])
        
        # Получаем сохранённый план питания
        self.meal_plan = store.get_weekly_meal_plan(user_info["id"])
        
        # Временные изменения (до нажатия Save)
        self.temp_changes = {}
        
        # Создаём UI
        self.build_ui()
    
    def build_ui(self):
        """Строит интерфейс страницы диеты"""
        # Заголовок страницы
        header = ft.Row(
            controls=[
                ft.Text(
                    "🍽️ Your Diet Plan",
                    size=28,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(expand=True),
            ]
        )
        
        self.controls.append(header)
        self.controls.append(ft.Divider())
        
        # Если предпочтений нет - показываем приглашение пройти тест
        if not self.preferences:
            self.show_empty_state()
        else:
            self.show_editable_preferences()
            # Добавляем секцию с планом питания
            self.add_meal_plan_section()
    
    def show_empty_state(self):
        """Показывает пустое состояние (тест не пройден)"""
        empty_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.RESTAURANT_MENU, size=80, color=ft.Colors.GREY_400),
                    ft.Container(height=20),
                    ft.Text(
                        "No diet preferences set",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_700
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Take our quick quiz to get personalized diet recommendations!",
                        size=14,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                        width=400
                    ),
                    ft.Container(height=30),
                    ft.ElevatedButton(
                        text="Take Diet Quiz",
                        icon=ft.Icons.QUIZ,
                        on_click=self.take_quiz,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.GREEN_600,
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        
        self.controls.append(empty_container)
    
    def show_editable_preferences(self):
        """Показывает предпочтения с возможностью редактирования"""
        
        # Заголовок секции
        preferences_header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=24, color=ft.Colors.BLUE_600),
                    ft.Text(
                        "Your Diet Preferences",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900
                    ),
                ],
                spacing=10
            ),
            padding=ft.padding.symmetric(vertical=15, horizontal=20),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
            border=ft.border.only(
                left=ft.BorderSide(3, ft.Colors.BLUE_400),
                right=ft.BorderSide(1, ft.Colors.BLUE_200),
                top=ft.BorderSide(1, ft.Colors.BLUE_200),
            )
        )
        
        self.controls.append(preferences_header)
        
        # Контейнер с предпочтениями
        preferences_container = ft.Container(
            content=ft.Column(
                controls=[],
                spacing=15
            ),
            padding=20,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
            bgcolor=ft.Colors.WHITE
        )
        
        # Получаем текущие значения
        goal = self.temp_changes.get("diet_goal", self.preferences.get("diet_goal", "meal_planning"))
        meal_pref = self.temp_changes.get("meal_preference", self.preferences.get("meal_preference", []))
        if isinstance(meal_pref, str):
            meal_pref = [meal_pref]
        
        cuisines = self.temp_changes.get("cuisine_preference", self.preferences.get("cuisine_preference", []))
        avoid = self.temp_changes.get("avoid_foods", self.preferences.get("avoid_foods", []))
        meal_freq = self.temp_changes.get("meal_frequency", self.preferences.get("meal_frequency", "3"))
        medical = self.temp_changes.get("medical_notes", self.preferences.get("medical_notes", ""))
        
        # ========== СЕКЦИЯ 0: Цель диеты (✅ УЛУЧШЕННЫЙ ДИЗАЙН) ==========
        goal_data = {
            "weight_loss": {
                "label": "Weight Loss",
                "emoji": "⚖️",
                "icon": ft.Icons.TRENDING_DOWN,
                "color": ft.Colors.ORANGE_600,
                "light_color": ft.Colors.ORANGE_50,
                "border_color": ft.Colors.ORANGE_300,
            },
            "muscle_gain": {
                "label": "Muscle Gain",
                "emoji": "💪",
                "icon": ft.Icons.FITNESS_CENTER,
                "color": ft.Colors.PURPLE_600,
                "light_color": ft.Colors.PURPLE_50,
                "border_color": ft.Colors.PURPLE_300,
            },
            "healthy_lifestyle": {
                "label": "Healthy Lifestyle",
                "emoji": "🏃",
                "icon": ft.Icons.FAVORITE,
                "color": ft.Colors.GREEN_600,
                "light_color": ft.Colors.GREEN_50,
                "border_color": ft.Colors.GREEN_300,
            },
            "meal_planning": {
                "label": "Regular Meal Planning",
                "emoji": "🍽️",
                "icon": ft.Icons.RESTAURANT_MENU,
                "color": ft.Colors.BLUE_600,
                "light_color": ft.Colors.BLUE_50,
                "border_color": ft.Colors.BLUE_300,
            }
        }
        
        current_goal_info = goal_data.get(goal, goal_data["meal_planning"])
        
        goal_section = ft.Container(
            content=ft.Column([
                # Заголовок с кнопкой Edit
                ft.Row([
                    ft.Text("Diet Goal", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                    ft.Container(expand=True),
                    ft.TextButton(
                        "Edit",
                        icon=ft.Icons.EDIT,
                        on_click=self.open_goal_dialog,
                        style=ft.ButtonStyle(color=current_goal_info["color"])
                    )
                ]),
                ft.Container(height=10),
                
                # ✅ НОВАЯ КРАСИВАЯ КАРТОЧКА
                ft.Container(
                    content=ft.Row([
                        # Левая часть: Emoji + Icon
                        ft.Container(
                            content=ft.Column([
                                ft.Text(current_goal_info["emoji"], size=36),
                                ft.Icon(
                                    current_goal_info["icon"],
                                    size=28,
                                    color=current_goal_info["color"]
                                ),
                            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            width=80,
                            padding=15,
                            bgcolor=current_goal_info["light_color"],
                            border_radius=ft.border_radius.only(top_left=12, bottom_left=12),
                        ),
                        
                        # Центр: Текст
                        ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    current_goal_info["label"],
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=current_goal_info["color"]
                                ),
                                ft.Text(
                                    "Your current diet objective",
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                    italic=True
                                ),
                            ], spacing=5),
                            expand=True,
                            padding=ft.padding.symmetric(horizontal=20, vertical=15)
                        ),
                        
                        # Правая часть: Чекмарк
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.CHECK_CIRCLE_ROUNDED,
                                size=36,
                                color=current_goal_info["color"]
                            ),
                            width=60,
                            alignment=ft.alignment.center
                        ),
                    ], spacing=0),
                    border=ft.border.all(2, current_goal_info["border_color"]),
                    border_radius=12,
                    bgcolor=ft.Colors.WHITE,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=8,
                        color=ft.Colors.with_opacity(0.15, current_goal_info["color"]),
                        offset=ft.Offset(0, 2)
                    ),
                )
            ]),
            padding=15,
            bgcolor=current_goal_info["light_color"],
            border_radius=10,
        )
        
        preferences_container.content.controls.append(goal_section)
        
        # ========== СЕКЦИЯ 1: Тип питания ==========
        meal_labels = {
            "vegetarian": "🥗 Vegetarian",
            "vegan": "🌱 Vegan",
            "pescatarian": "🐟 Pescatarian",
            "meat": "🍖 Meat-based",
            "balanced": "⚖️ Balanced"
        }
        
        meal_cards = ft.Row(controls=[], wrap=True, spacing=10)
        
        for value, label in meal_labels.items():
            is_selected = value in meal_pref
            
            card = ft.Container(
                content=ft.Text(label, size=14, text_align=ft.TextAlign.CENTER),
                width=120,
                height=50,
                border=ft.border.all(2, ft.Colors.GREEN_400 if is_selected else ft.Colors.GREY_300),
                border_radius=10,
                bgcolor=ft.Colors.GREEN_50 if is_selected else None,
                padding=10,
                on_click=lambda e, v=value: self.toggle_meal_type(v),
                ink=True
            )
            meal_cards.controls.append(card)
        
        meal_section = ft.Container(
            content=ft.Column([
                ft.Text("Meal Type (Select 1-2)", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                meal_cards
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=8,
            bgcolor=ft.Colors.GREY_50
        )
        
        preferences_container.content.controls.append(meal_section)
        
        # ========== СЕКЦИЯ 2: Любимые кухни ==========
        cuisine_labels = {
            "asian": "🍜 Asian",
            "italian": "🍝 Italian",
            "mexican": "🌮 Mexican",
            "mediterranean": "🫒 Mediterranean",
            "american": "🍔 American",
            "indian": "🍛 Indian"
        }
        
        cuisine_chips = ft.Row(controls=[], wrap=True, spacing=10)
        
        for value, label in cuisine_labels.items():
            is_selected = value in cuisines
            
            chip = ft.Container(
                content=ft.Text(label, size=14),
                padding=10,
                border=ft.border.all(2, ft.Colors.BLUE_400 if is_selected else ft.Colors.GREY_300),
                border_radius=20,
                bgcolor=ft.Colors.BLUE_50 if is_selected else None,
                on_click=lambda e, v=value: self.toggle_cuisine(v),
                ink=True
            )
            cuisine_chips.controls.append(chip)
        
        cuisine_section = ft.Container(
            content=ft.Column([
                ft.Text("Favorite Cuisines", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                cuisine_chips
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=8,
            bgcolor=ft.Colors.GREY_50
        )
        
        preferences_container.content.controls.append(cuisine_section)
        
        # ========== СЕКЦИЯ 3: Продукты для избегания ==========
        avoid_labels = {
            "dairy": "🥛 Dairy",
            "gluten": "🌾 Gluten",
            "nuts": "🥜 Nuts",
            "seafood": "🦐 Seafood",
            "spicy": "🌶️ Spicy",
            "none": "❌ None"
        }
        
        avoid_chips = ft.Row(controls=[], wrap=True, spacing=10)
        
        for value, label in avoid_labels.items():
            is_selected = value in avoid
            
            chip = ft.Container(
                content=ft.Text(label, size=14),
                padding=10,
                border=ft.border.all(2, ft.Colors.RED_400 if is_selected else ft.Colors.GREY_300),
                border_radius=20,
                bgcolor=ft.Colors.RED_50 if is_selected else None,
                on_click=lambda e, v=value: self.toggle_avoid(v),
                ink=True
            )
            avoid_chips.controls.append(chip)
        
        avoid_section = ft.Container(
            content=ft.Column([
                ft.Text("Foods to Avoid", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                avoid_chips
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=8,
            bgcolor=ft.Colors.GREY_50
        )
        
        preferences_container.content.controls.append(avoid_section)
        
        # ========== СЕКЦИЯ 4: Частота приёма пищи ==========
        freq_options = ["2", "3", "4"]
        freq_buttons = ft.Row(controls=[], spacing=10)
        
        for freq in freq_options:
            is_selected = meal_freq == freq
            
            btn = ft.Container(
                content=ft.Text(f"{freq} meals/day", size=14),
                padding=15,
                border=ft.border.all(2, ft.Colors.PURPLE_400 if is_selected else ft.Colors.GREY_300),
                border_radius=10,
                bgcolor=ft.Colors.PURPLE_50 if is_selected else None,
                on_click=lambda e, f=freq: self.set_meal_frequency(f),
                ink=True
            )
            freq_buttons.controls.append(btn)
        
        freq_section = ft.Container(
            content=ft.Column([
                ft.Text("Meals per Day", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                freq_buttons
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=8,
            bgcolor=ft.Colors.GREY_50
        )
        
        preferences_container.content.controls.append(freq_section)
        
        # ========== СЕКЦИЯ 5: Медицинские ограничения ==========
        self.medical_field = ft.TextField(
            label="Medical restrictions (optional)",
            value=medical,
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_color=ft.Colors.ORANGE_300,
            on_change=lambda e: self.update_medical_notes(e.control.value)
        )
        
        medical_section = ft.Container(
            content=ft.Column([
                ft.Text("Medical Restrictions", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                self.medical_field
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.ORANGE_300),
            border_radius=8,
            bgcolor=ft.Colors.ORANGE_50
        )
        
        preferences_container.content.controls.append(medical_section)
        
        # Добавляем контейнер
        self.controls.append(preferences_container)
        
        # Кнопки действий
        action_buttons = ft.Row(
            controls=[
                ft.ElevatedButton(
                    text="Save Changes",
                    icon=ft.Icons.SAVE,
                    on_click=self.save_changes,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN_600,
                        padding=15
                    )
                ),
                ft.OutlinedButton(
                    text="Reset to Saved",
                    icon=ft.Icons.REFRESH,
                    on_click=self.reset_changes,
                    style=ft.ButtonStyle(padding=15)
                ),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER
        )
        
        self.controls.append(ft.Container(height=10))
        self.controls.append(action_buttons)
    
    def add_meal_plan_section(self):
        """✅ НОВОЕ: Добавляет секцию с планом питания"""
        
        # Заголовок секции
        meal_plan_header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CALENDAR_VIEW_WEEK, size=24, color=ft.Colors.GREEN_600),
                    ft.Text(
                        "Weekly Meal Plan",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_900
                    ),
                    ft.Container(expand=True),
                    # ✅ Кнопка генерации
                    ft.ElevatedButton(
                        text="Generate Meal Plan",
                        icon=ft.Icons.AUTO_AWESOME,
                        on_click=self.generate_meal_plan,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.GREEN_600,
                        )
                    ) if not self.meal_plan else ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Regenerate Meal Plan",
                        on_click=self.generate_meal_plan,
                        icon_color=ft.Colors.GREEN_600
                    ),
                ],
                spacing=10
            ),
            padding=ft.padding.symmetric(vertical=15, horizontal=20),
            bgcolor=ft.Colors.GREEN_50,
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
            border=ft.border.only(
                left=ft.BorderSide(3, ft.Colors.GREEN_400),
                right=ft.BorderSide(1, ft.Colors.GREEN_200),
                top=ft.BorderSide(1, ft.Colors.GREEN_200),
            )
        )
        
        self.controls.append(ft.Container(height=20))
        self.controls.append(meal_plan_header)
        
        # Контейнер с планом или заглушкой
        if self.meal_plan:
            self.show_meal_plan_table()
        else:
            self.show_empty_meal_plan()
    
    def show_empty_meal_plan(self):
        """Показывает заглушку если плана нет"""
        meal_plan_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.RESTAURANT, size=60, color=ft.Colors.GREY_400),
                    ft.Container(height=10),
                    ft.Text(
                        "No meal plan generated yet",
                        size=18,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        "Click 'Generate Meal Plan' to get AI-powered recommendations",
                        size=14,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            height=300,
            padding=20,
            border=ft.border.all(1, ft.Colors.GREEN_200),
            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
            bgcolor=ft.Colors.WHITE,
            alignment=ft.alignment.center
        )
        
        self.controls.append(meal_plan_container)
    
    def show_meal_plan_table(self):
        """✅ НОВОЕ: Показывает таблицу с планом питания"""
        plan = self.meal_plan.get("plan", {})
        
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Определяем типы приёмов пищи
        meal_frequency = int(self.preferences.get("meal_frequency", "3"))
        if meal_frequency == 2:
            meal_types = ["breakfast", "dinner"]
        elif meal_frequency == 3:
            meal_types = ["breakfast", "lunch", "dinner"]
        else:
            meal_types = ["breakfast", "lunch", "snack", "dinner"]
        
        # Заголовок таблицы
        table_header = ft.Row(
            controls=[
                ft.Container(content=ft.Text("Day", weight=ft.FontWeight.BOLD), width=100)
            ] + [
                ft.Container(
                    content=ft.Text(meal.capitalize(), weight=ft.FontWeight.BOLD, size=12),
                    expand=True,
                    alignment=ft.alignment.center
                )
                for meal in meal_types
            ],
            spacing=5
        )
        
        # Строки таблицы
        table_rows = []
        
        for day, day_name in zip(days, day_names):
            day_meals = plan.get(day, {})
            
            row_controls = [
                ft.Container(
                    content=ft.Text(day_name, weight=ft.FontWeight.BOLD, size=12),
                    width=100,
                    padding=10,
                    bgcolor=ft.Colors.GREEN_50
                )
            ]
            
            for meal_type in meal_types:
                meal = day_meals.get(meal_type, {})
                
                if meal:
                    # Кнопка замены блюда
                    replace_btn = ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        icon_size=14,
                        tooltip="Replace",
                        on_click=lambda e, d=day, m=meal_type: self.replace_meal(d, m)
                    )
                    
                    meal_card = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(meal.get("name", "—"), size=11, weight=ft.FontWeight.BOLD, expand=True),
                                replace_btn
                            ]),
                            ft.Text(f"{meal.get('calories', 0)} kcal", size=10, color=ft.Colors.GREY_600),
                            ft.Text(
                                f"P: {meal.get('protein', 0)}g | C: {meal.get('carbs', 0)}g | F: {meal.get('fats', 0)}g",
                                size=9,
                                color=ft.Colors.GREY_500
                            ),
                        ], spacing=2),
                        padding=8,
                        border=ft.border.all(1, ft.Colors.GREEN_200),
                        border_radius=5,
                        bgcolor=ft.Colors.WHITE,
                        expand=True
                    )
                else:
                    meal_card = ft.Container(
                        content=ft.Text("—", color=ft.Colors.GREY_400),
                        padding=10,
                        alignment=ft.alignment.center,
                        expand=True
                    )
                
                row_controls.append(meal_card)
            
            table_rows.append(
                ft.Row(controls=row_controls, spacing=5)
            )
        
        # Итоговая таблица
        table_container = ft.Container(
            content=ft.Column(
                controls=[table_header] + table_rows,
                spacing=5,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREEN_200),
            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
            bgcolor=ft.Colors.WHITE
        )
        
        self.controls.append(table_container)
        
        # Итоговая калорийность
        total_calories = sum(
            sum(meal.get("calories", 0) for meal in day_meals.values())
            for day_meals in plan.values()
        ) // 7
        
        summary = ft.Container(
            content=ft.Row([
                ft.Text(f"Average daily calories: {total_calories} kcal", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.TextButton(
                    "Delete Plan",
                    icon=ft.Icons.DELETE_OUTLINE,
                    on_click=self.delete_meal_plan,
                    icon_color=ft.Colors.RED_400
                )
            ]),
            padding=ft.padding.symmetric(vertical=10, horizontal=15),
            bgcolor=ft.Colors.GREEN_50,
            border_radius=5
        )
        
        self.controls.append(ft.Container(height=10))
        self.controls.append(summary)
    
    def generate_meal_plan(self, e):
        """✅ НОВОЕ: Генерирует план питания через AI"""
        # Показываем индикатор загрузки
        loading_snack = ft.SnackBar(
            content=ft.Row([
                ft.ProgressRing(width=16, height=16, stroke_width=2),
                ft.Text("Generating meal plan... Please wait 5-10 seconds"),
            ]),
            bgcolor=ft.Colors.BLUE_400,
            duration=10000
        )
        self.page_ref.open(loading_snack)
        
        # Генерируем план в фоновом потоке
        self.page_ref.run_task(self._generate_plan_async)
    
    async def _generate_plan_async(self):
        """Асинхронная генерация плана"""
        from services.diet_ai_service import DietAIService
        
        diet_ai = DietAIService()
        
        # Получаем актуальные предпочтения
        current_prefs = {**self.preferences, **self.temp_changes}
        medical_notes = current_prefs.get("medical_notes", "")
        
        # Генерируем план
        import asyncio
        loop = asyncio.get_running_loop()
        new_plan = await loop.run_in_executor(None, diet_ai.generate_weekly_plan, current_prefs, medical_notes)
        
        if new_plan:
            # Сохраняем в БД
            store.save_weekly_meal_plan(self.user_info["id"], new_plan)
            
            # Обновляем локальную копию
            self.meal_plan = new_plan
            
            # Перестраиваем UI
            self.controls.clear()
            self.build_ui()
            self.update()
            
            # Показываем успех
            success_snack = ft.SnackBar(
                content=ft.Text("✅ Meal plan generated successfully!"),
                bgcolor=ft.Colors.GREEN_400
            )
            self.page_ref.open(success_snack)
        else:
            # Показываем ошибку
            error_snack = ft.SnackBar(
                content=ft.Text("❌ Failed to generate meal plan. Please try again."),
                bgcolor=ft.Colors.RED_400
            )
            self.page_ref.open(error_snack)
    
    def replace_meal(self, day, meal_type):
        """✅ НОВОЕ: Заменяет конкретное блюдо"""
        loading_snack = ft.SnackBar(
            content=ft.Row([
                ft.ProgressRing(width=16, height=16, stroke_width=2),
                ft.Text(f"Replacing {day}'s {meal_type}..."),
            ]),
            bgcolor=ft.Colors.BLUE_400,
            duration=5000
        )
        self.page_ref.open(loading_snack)
        
        self.page_ref.run_task(self._replace_meal_async, day, meal_type)
    
    async def _replace_meal_async(self, day, meal_type):
        """Асинхронная замена блюда"""
        from services.diet_ai_service import DietAIService
        
        diet_ai = DietAIService()
        
        current_prefs = {**self.preferences, **self.temp_changes}
        medical_notes = current_prefs.get("medical_notes", "")
        
        # Генерируем новое блюдо
        import asyncio
        loop = asyncio.get_running_loop()
        new_meal = await loop.run_in_executor(None, diet_ai.replace_meal, current_prefs, medical_notes, day, meal_type)
        
        if new_meal:
            # Обновляем в БД
            store.replace_meal_in_plan(self.user_info["id"], day, meal_type, new_meal)
            
            # Обновляем локально
            if not self.meal_plan:
                self.meal_plan = store.get_weekly_meal_plan(self.user_info["id"])
            else:
                self.meal_plan["plan"][day][meal_type] = new_meal
            
            # Перестраиваем UI
            self.controls.clear()
            self.build_ui()
            self.update()
            
            success_snack = ft.SnackBar(
                content=ft.Text(f"✅ {day.capitalize()}'s {meal_type} replaced!"),
                bgcolor=ft.Colors.GREEN_400
            )
            self.page_ref.open(success_snack)
        else:
            error_snack = ft.SnackBar(
                content=ft.Text("❌ Failed to replace meal. Please try again."),
                bgcolor=ft.Colors.RED_400
            )
            self.page_ref.open(error_snack)
    
    def delete_meal_plan(self, e):
        """Удаляет план питания"""
        def confirm_delete(e):
            store.delete_meal_plan(self.user_info["id"])
            self.meal_plan = None
            self.page_ref.close(dialog)
            
            self.controls.clear()
            self.build_ui()
            self.update()
            
            snack = ft.SnackBar(content=ft.Text("Meal plan deleted"), bgcolor=ft.Colors.BLUE_400)
            self.page_ref.open(snack)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Delete Meal Plan?"),
            content=ft.Text("This will permanently delete your meal plan. You can generate a new one anytime."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.page_ref.close(dialog)),
                ft.ElevatedButton("Delete", on_click=confirm_delete, bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE),
            ]
        )
        
        self.page_ref.open(dialog)
    
    # ========== МЕТОДЫ ДЛЯ ИЗМЕНЕНИЯ ПРЕДПОЧТЕНИЙ ==========
    
    def open_goal_dialog(self, e):
        """Открывает диалог изменения цели"""
        current_goal = self.temp_changes.get("diet_goal", self.preferences.get("diet_goal", "meal_planning"))
        
        def on_change(new_goal):
            self.temp_changes["diet_goal"] = new_goal
            self.rebuild_ui()
        
        dialog = DietGoalDialog(self.page_ref, current_goal, on_change)
        self.page_ref.open(dialog)
    
    def toggle_meal_type(self, value):
        meal_pref = list(self.temp_changes.get("meal_preference", self.preferences.get("meal_preference", [])))
        if isinstance(meal_pref, str):
            meal_pref = [meal_pref]
        
        if value in meal_pref:
            meal_pref.remove(value)
        else:
            if len(meal_pref) >= 2:
                snack = ft.SnackBar(content=ft.Text("You can select maximum 2 meal types!"), bgcolor=ft.Colors.ORANGE_400)
                self.page_ref.open(snack)
                return
            meal_pref.append(value)
        
        self.temp_changes["meal_preference"] = meal_pref
        self.rebuild_ui()
    
    def toggle_cuisine(self, value):
        cuisines = list(self.temp_changes.get("cuisine_preference", self.preferences.get("cuisine_preference", [])))
        if value in cuisines:
            cuisines.remove(value)
        else:
            cuisines.append(value)
        self.temp_changes["cuisine_preference"] = cuisines
        self.rebuild_ui()
    
    def toggle_avoid(self, value):
        avoid = list(self.temp_changes.get("avoid_foods", self.preferences.get("avoid_foods", [])))
        if value in avoid:
            avoid.remove(value)
        else:
            avoid.append(value)
        self.temp_changes["avoid_foods"] = avoid
        self.rebuild_ui()
    
    def set_meal_frequency(self, freq):
        self.temp_changes["meal_frequency"] = freq
        self.rebuild_ui()
    
    def update_medical_notes(self, notes):
        self.temp_changes["medical_notes"] = notes
    
    def rebuild_ui(self):
        self.controls.clear()
        self.build_ui()
        self.update()
    
    def save_changes(self, e):
        updated_preferences = {**self.preferences, **self.temp_changes}
        success = store.save_diet_preferences(self.user_info["id"], updated_preferences)
        
        if success:
            self.preferences = updated_preferences
            self.temp_changes = {}
            snack = ft.SnackBar(content=ft.Text("✅ Changes saved successfully!"), bgcolor=ft.Colors.GREEN_400)
            self.page_ref.open(snack)
        else:
            snack = ft.SnackBar(content=ft.Text("❌ Failed to save changes!"), bgcolor=ft.Colors.RED_400)
            self.page_ref.open(snack)
    
    def reset_changes(self, e):
        self.temp_changes = {}
        self.rebuild_ui()
        snack = ft.SnackBar(content=ft.Text("Changes reset to saved values"), bgcolor=ft.Colors.BLUE_400)
        self.page_ref.open(snack)
    
    def take_quiz(self, e):
        from components.diet_quiz_view import DietQuizView
        self.page_ref.clean()
        
        def on_complete():
            self.page_ref.clean()
            from components.layout import AppLayout
            from components.header import Header
            from components.chat import ChatWidget
            
            app_layout = AppLayout(self.page_ref, self.user_info, lambda e: None)
            app_layout.set_view("Diet")
            
            self.page_ref.appbar = Header(
                self.page_ref,
                lambda: app_layout.set_view("Account"),
                on_menu_click=lambda e: app_layout.toggle_sidebar()
            )
            
            main_stack = ft.Stack([
                app_layout,
                ft.Container(
                    content=ChatWidget(self.page_ref, on_refresh=app_layout.refresh_active_view),
                    right=20,
                    bottom=20,
                )
            ], expand=True)
            
            self.page_ref.add(main_stack)
            self.page_ref.update()
        
        quiz = DietQuizView(self.page_ref, self.user_info, on_complete)
        self.page_ref.add(quiz)
        self.page_ref.update()