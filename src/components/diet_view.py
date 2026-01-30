import flet as ft
from data.store import store
from components.diet_goal_dialog import DietGoalDialog

class DietView(ft.Column):
    """
    Страница диеты с возможностью редактирования предпочтений.
    + НОВОЕ: Отображение цели диеты и место для таблицы питания
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
            # ✅ НОВОЕ: Добавляем заготовку для таблицы питания
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
        
        # Заголовок секции с предпочтениями
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
        meal_pref = self.temp_changes.get("meal_preference", self.preferences.get("meal_preference", []))
        if isinstance(meal_pref, str):
            meal_pref = [meal_pref]
        
        cuisines = self.temp_changes.get("cuisine_preference", self.preferences.get("cuisine_preference", []))
        avoid = self.temp_changes.get("avoid_foods", self.preferences.get("avoid_foods", []))
        meal_freq = self.temp_changes.get("meal_frequency", self.preferences.get("meal_frequency", "3"))
        medical = self.temp_changes.get("medical_notes", self.preferences.get("medical_notes", ""))
        diet_goal = self.temp_changes.get("diet_goal", self.preferences.get("diet_goal", ""))  # ✅ НОВОЕ
        
        # ========== СЕКЦИЯ 0: ЦЕЛЬ ДИЕТЫ (✅ НОВАЯ СЕКЦИЯ) ==========
        if diet_goal:
            goal_labels = {
                "weight_loss": ("⚖️ Weight Loss", ft.Colors.ORANGE_600),
                "muscle_gain": ("💪 Muscle Gain", ft.Colors.PURPLE_600),
                "healthy_lifestyle": ("🏃 Healthy Lifestyle", ft.Colors.GREEN_600),
                "meal_planning": ("🍽️ Regular Meal Planning", ft.Colors.BLUE_600),
            }
            
            goal_label, goal_color = goal_labels.get(diet_goal, ("📋 Not Set", ft.Colors.GREY_600))
            
            goal_section = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Diet Goal", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Row([
                                ft.Text(
                                    goal_label,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                ft.Container(width=5),
                                ft.Icon(
                                    ft.Icons.EDIT,
                                    size=16,
                                    color=ft.Colors.WHITE
                                ),
                            ]),
                            bgcolor=goal_color,
                            padding=ft.padding.symmetric(horizontal=15, vertical=8),
                            border_radius=20,
                            ink=True,
                            on_click=lambda e: self.show_goal_dialog(),  # ✅ НОВЫЙ МЕТОД
                            tooltip="Click to change goal"
                        )
                    ])
                ]),
                padding=15,
                border=ft.border.all(2, goal_color),
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.1, goal_color)
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
        
        # ========== СЕКЦИЯ 3: Избегаемые продукты ==========
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
        
        # Добавляем контейнер с предпочтениями
        self.controls.append(preferences_container)
        
        # ========== КНОПКИ ДЕЙСТВИЙ ==========
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
                    style=ft.ButtonStyle(
                        padding=15
                    )
                ),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER
        )
        
        self.controls.append(ft.Container(height=10))
        self.controls.append(action_buttons)
    
    def add_meal_plan_section(self):
        """
        ✅ НОВАЯ СЕКЦИЯ: Таблица плана питания на неделю
        Пока заготовка, будет заполняться AI в следующем шаге
        """
        self.controls.append(ft.Container(height=30))
        self.controls.append(ft.Divider())
        
        # Заголовок секции
        meal_plan_header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=24, color=ft.Colors.GREEN_600),
                    ft.Text(
                        "Your Weekly Meal Plan",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_900
                    ),
                    ft.Container(expand=True),
                    # ✅ КНОПКА ДЛЯ ГЕНЕРАЦИИ (будет работать после Extended Mode)
                    ft.ElevatedButton(
                        text="Generate Meal Plan",
                        icon=ft.Icons.AUTO_AWESOME,
                        on_click=self.generate_meal_plan,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.GREEN_600,
                        )
                    )
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
        
        self.controls.append(meal_plan_header)
        
        # ✅ ЗАГОТОВКА: Пустая таблица или placeholder
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
    
    def generate_meal_plan(self, e):
        """
        ✅ ЗАГОТОВКА: Генерация плана питания через AI
        Будет реализована в Extended Mode
        """
        snack = ft.SnackBar(
            content=ft.Text("🚧 AI meal plan generation coming soon! (Needs Extended Mode)"),
            bgcolor=ft.Colors.BLUE_400
        )
        self.page_ref.open(snack)
        
        # TODO: После Extended Mode здесь будет:
        # 1. Вызов diet_ai_service.py для генерации плана
        # 2. Отображение таблицы 7x3 (неделя x приёмы пищи)
        # 3. Возможность добавить в календарь
    
    # ========== МЕТОДЫ ДЛЯ ОБРАБОТКИ ИЗМЕНЕНИЙ ==========
    
    def toggle_meal_type(self, value):
        """Переключение типа питания (макс 2)"""
        meal_pref = list(self.temp_changes.get("meal_preference", self.preferences.get("meal_preference", [])))
        if isinstance(meal_pref, str):
            meal_pref = [meal_pref]
        
        if value in meal_pref:
            meal_pref.remove(value)
        else:
            if len(meal_pref) >= 2:
                snack = ft.SnackBar(
                    content=ft.Text("You can select maximum 2 meal types!"),
                    bgcolor=ft.Colors.ORANGE_400
                )
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
    
    def show_goal_dialog(self):
        """✅ НОВЫЙ МЕТОД: Показывает диалог изменения цели диеты"""
        current_goal = self.temp_changes.get("diet_goal", self.preferences.get("diet_goal", ""))
        
        def on_goal_change(new_goal):
            """Callback при изменении цели"""
            self.temp_changes["diet_goal"] = new_goal
            self.rebuild_ui()
            
            # Показываем уведомление
            snack = ft.SnackBar(
                content=ft.Text(f"✅ Diet goal changed! Don't forget to save."),
                bgcolor=ft.Colors.BLUE_400
            )
            self.page_ref.open(snack)
        
        # Открываем диалог
        dialog = DietGoalDialog(
            self.page_ref,
            current_goal,
            on_goal_change
        )
        self.page_ref.open(dialog)
        self.page_ref.update()

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