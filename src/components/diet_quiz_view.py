import flet as ft
from data.store import store

class DietQuizView(ft.Column):
    """
    Тест на определение предпочтений пользователя по диете.
    Собирает информацию о вкусах, аллергиях и медицинских ограничениях.
    """
    def __init__(self, page: ft.Page, user_info: dict, on_complete):
        super().__init__()
        self.page_ref = page
        self.user_info = user_info
        self.on_complete = on_complete
        
        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20
        
        # Текущий вопрос
        self.current_question = 0
        self.answers = {}
        
        # ✅ ОБНОВЛЕНО: Вопрос о цели диеты теперь ПЕРВЫЙ
        self.questions = [
            # ═══ ВОПРОС 1: ЦЕЛЬ ДИЕТЫ (✅ ПЕРЕНЕСЁН НА 1-Е МЕСТО) ═══
            {
                "id": "diet_goal",
                "question": "What is your main diet goal?",
                "type": "single_choice_cards",
                "options": [
                    {"value": "weight_loss", "label": "⚖️ Weight Loss", "icon": ft.Icons.TRENDING_DOWN},
                    {"value": "muscle_gain", "label": "💪 Muscle Gain", "icon": ft.Icons.FITNESS_CENTER},
                    {"value": "healthy_lifestyle", "label": "🏃 Healthy Lifestyle", "icon": ft.Icons.FAVORITE},
                    {"value": "meal_planning", "label": "🍽️ Regular Meal Planning", "icon": ft.Icons.RESTAURANT_MENU},
                ]
            },
            # ═══ ВОПРОС 2: ТИП ПИТАНИЯ ═══
            {
                "id": "meal_preference",
                "question": "What type of meals do you prefer? (Select 1-2 options)",
                "type": "multiple_choice_limited",
                "max_selections": 2,
                "options": [
                    {"value": "vegetarian", "label": "🥗 Vegetarian", "icon": ft.Icons.ECO},
                    {"value": "vegan", "label": "🌱 Vegan", "icon": ft.Icons.GRASS},
                    {"value": "pescatarian", "label": "🐟 Pescatarian", "icon": ft.Icons.SET_MEAL},
                    {"value": "meat", "label": "🍖 Meat-based", "icon": ft.Icons.LUNCH_DINING},
                    {"value": "balanced", "label": "⚖️ Balanced (everything)", "icon": ft.Icons.RESTAURANT},
                ]
            },
            # ═══ ВОПРОС 3: ЛЮБИМЫЕ КУХНИ ═══
            {
                "id": "cuisine_preference",
                "question": "What cuisines do you enjoy? (Select multiple)",
                "type": "checkbox",
                "options": [
                    {"value": "asian", "label": "🍜 Asian"},
                    {"value": "italian", "label": "🍝 Italian"},
                    {"value": "mexican", "label": "🌮 Mexican"},
                    {"value": "mediterranean", "label": "🫒 Mediterranean"},
                    {"value": "american", "label": "🍔 American"},
                    {"value": "indian", "label": "🍛 Indian"},
                ]
            },
            # ═══ ВОПРОС 4: ИЗБЕГАЕМЫЕ ПРОДУКТЫ ═══
            {
                "id": "avoid_foods",
                "question": "Are there any foods you want to avoid?",
                "type": "checkbox",
                "options": [
                    {"value": "dairy", "label": "🥛 Dairy"},
                    {"value": "gluten", "label": "🌾 Gluten"},
                    {"value": "nuts", "label": "🥜 Nuts"},
                    {"value": "seafood", "label": "🦐 Seafood"},
                    {"value": "spicy", "label": "🌶️ Spicy food"},
                    {"value": "none", "label": "❌ None"},
                ]
            },
            # ═══ ВОПРОС 5: ЧАСТОТА ПРИЁМОВ ПИЩИ ═══
            {
                "id": "meal_frequency",
                "question": "How many meals per day?",
                "type": "single_choice",
                "options": [
                    {"value": "2", "label": "2 meals"},
                    {"value": "3", "label": "3 meals"},
                    {"value": "4", "label": "4-5 small meals"},
                ]
            },
        ]
        
        # UI элементы
        self.progress_bar = ft.ProgressBar(
            value=0,
            width=600,
            color=ft.Colors.GREEN_400,
            bgcolor=ft.Colors.GREY_200
        )
        
        self.question_title = ft.Text(
            "",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        self.question_container = ft.Column(
            controls=[],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )
        
        self.medical_notes_field = ft.TextField(
            label="Medical restrictions (optional)",
            hint_text="e.g., diabetes, lactose intolerance, allergies...",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=600,
            visible=False
        )
        
        self.back_button = ft.TextButton(
            text="Back",
            on_click=self.go_back,
            visible=False
        )
        
        self.next_button = ft.ElevatedButton(
            text="Next",
            on_click=self.go_next,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600,
            )
        )
        
        self.controls = [
            ft.Container(height=30),
            
            ft.Text(
                "Let's find your perfect diet! 🍽️",
                size=28,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            
            ft.Container(height=10),
            
            self.progress_bar,
            
            ft.Container(height=30),
            
            self.question_title,
            
            ft.Container(height=20),
            
            self.question_container,
            
            ft.Container(height=20),
            
            self.medical_notes_field,
            
            ft.Container(height=30),
            
            ft.Row(
                controls=[
                    self.back_button,
                    ft.Container(expand=True),
                    self.next_button,
                ],
                width=600,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            
            ft.Container(height=50),
        ]
    
    def did_mount(self):
        """Вызывается когда компонент добавлен на страницу"""
        self.render_question()
    
    def render_question(self):
        """Отображает текущий вопрос"""
        question = self.questions[self.current_question]
        
        # Обновляем прогресс
        self.progress_bar.value = (self.current_question + 1) / len(self.questions)
        self.progress_bar.update()
        
        # Обновляем заголовок вопроса
        self.question_title.value = f"Question {self.current_question + 1}/{len(self.questions)}"
        self.question_title.update()
        
        # Полностью очищаем контейнер
        self.question_container.controls.clear()
        
        # Добавляем текст вопроса
        self.question_container.controls.append(
            ft.Text(
                question["question"],
                size=18,
                text_align=ft.TextAlign.CENTER,
                weight=ft.FontWeight.W_500
            )
        )
        
        self.question_container.controls.append(ft.Container(height=20))
        
        # Рендерим варианты ответов
        if question["type"] == "multiple_choice_limited":
            self.render_multiple_choice_limited(question)
        elif question["type"] == "checkbox":
            self.render_checkbox(question)
        elif question["type"] == "single_choice":
            self.render_single_choice(question)
        elif question["type"] == "single_choice_cards":
            self.render_single_choice_cards(question)
        
        # Показываем кнопку Back если не первый вопрос
        self.back_button.visible = self.current_question > 0
        self.back_button.update()
        
        # Меняем текст кнопки Next на Finish если последний вопрос
        if self.current_question == len(self.questions) - 1:
            self.next_button.text = "Finish"
            self.medical_notes_field.visible = True
        else:
            self.next_button.text = "Next"
            self.medical_notes_field.visible = False
        
        self.next_button.update()
        self.medical_notes_field.update()
        
        # Обновляем весь контейнер
        self.question_container.update()
    
    def render_single_choice_cards(self, question):
        """Карточки для одиночного выбора (для diet_goal)"""
        current_answer = self.answers.get(question["id"])
        
        cards_row = ft.Row(
            controls=[],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            wrap=True
        )
        
        for option in question["options"]:
            is_selected = option["value"] == current_answer
            
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            option.get("icon", ft.Icons.CIRCLE),
                            size=40,
                            color=ft.Colors.BLUE_400 if is_selected else ft.Colors.GREY_600
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            option["label"],
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0
                ),
                width=140,
                height=130,
                border=ft.border.all(
                    3 if is_selected else 2,
                    ft.Colors.BLUE_400 if is_selected else ft.Colors.GREY_300
                ),
                border_radius=10,
                padding=15,
                bgcolor=ft.Colors.BLUE_50 if is_selected else None,
                ink=True,
                on_click=lambda e, val=option["value"]: self.select_option(question["id"], val),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT)
            )
            
            cards_row.controls.append(card)
        
        self.question_container.controls.append(cards_row)
    
    def render_multiple_choice_limited(self, question):
        """Множественный выбор с ограничением (1-2 варианта)"""
        current_answers = self.answers.get(question["id"], [])
        max_selections = question.get("max_selections", 2)
        
        cards_row = ft.Row(
            controls=[],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            wrap=True
        )
        
        for option in question["options"]:
            is_selected = option["value"] in current_answers
            
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            option.get("icon", ft.Icons.CIRCLE),
                            size=40,
                            color=ft.Colors.GREEN_400 if is_selected else ft.Colors.GREY_600
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            option["label"],
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0
                ),
                width=140,
                height=130,
                border=ft.border.all(
                    3 if is_selected else 2,
                    ft.Colors.GREEN_400 if is_selected else ft.Colors.GREY_300
                ),
                border_radius=10,
                padding=15,
                bgcolor=ft.Colors.GREEN_50 if is_selected else None,
                ink=True,
                on_click=lambda e, val=option["value"]: self.toggle_limited_selection(question["id"], val, max_selections),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT)
            )
            
            cards_row.controls.append(card)
        
        self.question_container.controls.append(cards_row)
    
    def toggle_limited_selection(self, question_id, value, max_selections):
        """Переключение с ограничением количества"""
        if question_id not in self.answers:
            self.answers[question_id] = []
        
        if value in self.answers[question_id]:
            self.answers[question_id].remove(value)
        else:
            if len(self.answers[question_id]) < max_selections:
                self.answers[question_id].append(value)
            else:
                snack = ft.SnackBar(
                    content=ft.Text(f"You can select maximum {max_selections} options!"),
                    bgcolor=ft.Colors.ORANGE_400
                )
                self.page_ref.overlay.append(snack); snack.open = True; self.page_ref.update()
        
        self.render_question()
    
    def render_checkbox(self, question):
        """Чекбоксы по центру"""
        current_answers = self.answers.get(question["id"], [])
        
        checkbox_container = ft.Container(
            content=ft.Column(
                controls=[],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.START
            ),
            alignment=ft.alignment.center,
            width=400
        )
        
        for option in question["options"]:
            is_checked = option["value"] in current_answers
            
            checkbox = ft.Checkbox(
                label=option["label"],
                value=is_checked,
                on_change=lambda e, val=option["value"]: self.toggle_checkbox(question["id"], val)
            )
            
            checkbox_container.content.controls.append(checkbox)
        
        self.question_container.controls.append(checkbox_container)
    
    def render_single_choice(self, question):
        """Радио кнопки по центру"""
        current_answer = self.answers.get(question["id"])
        
        radio_column = ft.Column(
            controls=[
                ft.Radio(value=option["value"], label=option["label"])
                for option in question["options"]
            ],
            spacing=10
        )
        
        radio_group = ft.RadioGroup(
            content=radio_column,
            value=current_answer,
            on_change=lambda e: self.select_option(question["id"], e.control.value)
        )
        
        centered_container = ft.Container(
            content=radio_group,
            alignment=ft.alignment.center,
            width=400
        )
        
        self.question_container.controls.append(centered_container)
    
    def select_option(self, question_id, value):
        """Выбор одного варианта ответа"""
        self.answers[question_id] = value
        self.render_question()
    
    def toggle_checkbox(self, question_id, value):
        """Переключение чекбокса"""
        if question_id not in self.answers:
            self.answers[question_id] = []
        
        if value in self.answers[question_id]:
            self.answers[question_id].remove(value)
        else:
            self.answers[question_id].append(value)
    
    def go_back(self, e):
        """Переход к предыдущему вопросу"""
        if self.current_question > 0:
            self.current_question -= 1
            self.render_question()
    
    def go_next(self, e):
        """Переход к следующему вопросу или завершение"""
        question = self.questions[self.current_question]
        
        # Проверяем что ответ дан
        if question["id"] not in self.answers or not self.answers[question["id"]]:
            snack = ft.SnackBar(
                content=ft.Text("Please select at least one option!"),
                bgcolor=ft.Colors.ORANGE_400
            )
            self.page_ref.overlay.append(snack); snack.open = True; self.page_ref.update()
            return
        
        # Если последний вопрос - сохраняем и завершаем
        if self.current_question == len(self.questions) - 1:
            self.save_and_finish()
        else:
            # Переходим к следующему вопросу
            self.current_question += 1
            self.render_question()
    
    def save_and_finish(self):
        """Сохраняет ответы в БД и завершает тест"""
        # Добавляем медицинские ограничения если указаны
        medical_notes = self.medical_notes_field.value.strip()
        if medical_notes:
            self.answers["medical_notes"] = medical_notes
        
        # Сохраняем в БД
        try:
            store.save_diet_preferences(self.user_info["id"], self.answers)
            
            # Показываем успешное сообщение
            snack = ft.SnackBar(
                content=ft.Text("✅ Diet preferences saved successfully!"),
                bgcolor=ft.Colors.GREEN_400
            )
            self.page_ref.overlay.append(snack); snack.open = True; self.page_ref.update()
            
            # Вызываем callback
            if self.on_complete:
                self.on_complete()
                
        except Exception as e:
            print(f"Error saving diet preferences: {e}")
            snack = ft.SnackBar(
                content=ft.Text("❌ Failed to save preferences. Please try again."),
                bgcolor=ft.Colors.RED_400
            )
            self.page_ref.overlay.append(snack); snack.open = True; self.page_ref.update()