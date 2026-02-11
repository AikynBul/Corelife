import flet as ft
import random
from data.store import store
from services.ai_service import AIService
from services.task_scheduler import TaskScheduler  # ✅ НОВЫЙ ИМПОРТ

class ChatWidget(ft.Column):
    MOTIVATION_QUOTES = [
    "💡 'The only way to do great work is to love what you do.' - Steve Jobs",
    "🎯 'Success is not final, failure is not fatal: it is the courage to continue that counts.' - Winston Churchill",
    "⚡ 'The future depends on what you do today.' - Mahatma Gandhi",
    "🚀 'Don't watch the clock; do what it does. Keep going.' - Sam Levenson",
    "💪 'Believe you can and you're halfway there.' - Theodore Roosevelt",
    "🌟 'The secret of getting ahead is getting started.' - Mark Twain",
    "📚 'Education is the most powerful weapon which you can use to change the world.' - Nelson Mandela",
    "🔥 'It does not matter how slowly you go as long as you do not stop.' - Confucius",
    "✨ 'Your time is limited, don't waste it living someone else's life.' - Steve Jobs",
    "🎓 'The expert in anything was once a beginner.' - Helen Hayes",
    "🏆 'The only impossible journey is the one you never begin.' - Tony Robbins",
    "💎 'Quality is not an act, it is a habit.' - Aristotle",
    ]

    def __init__(self, page: ft.Page, on_refresh=None):
        super().__init__()
        self.page_ref = page
        self.on_refresh = on_refresh
        self.calendar_ref = None
        self.ai_service = AIService()
        self.task_scheduler = TaskScheduler()  # ✅ НОВЫЙ ПЛАНИРОВЩИК
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
        
        # ✅ НОВОЕ ПРИВЕТСТВИЕ С ПЛАНИРОВЩИКОМ
        self.add_message(
            "👋 Welcome to Corelife!\n\n"
            "⏰ Did you know? Proper time management can:\n"
            "• Reduce stress by 47%\n"
            "• Boost productivity by 100%\n"
            "• Improve your mood by 65%\n\n"
            "🎯 I'm here to help you:\n"
            "✓ Schedule smart - I'll find the best time\n"
            "✓ Stay organized - Never miss a deadline\n"
            "✓ Balance life - Work, study, rest in harmony\n\n"
            "💪 What's on your mind? 💡\n"
            "Share your tasks for today, and I'll schedule them efficiently!",
            is_user=False,
            update=False
        )

        if random.random() < 1.0:  # 100% шанс показать цитату
            self.add_message(
                random.choice(self.MOTIVATION_QUOTES),
                is_user=False,
                update=False
            )

    def find_event_by_title(self, title_to_find):
        """Ищет событие по частичному совпадению названия в текущем и следующих 2 месяцах"""
        from datetime import datetime

        title_lower = (title_to_find or "").lower()
        if not title_lower:
            return None

        now = datetime.now()

        # Проверяем текущий месяц и следующие 2 месяца
        for month_offset in range(3):
            month = now.month + month_offset
            year = now.year

            # Корректируем год если месяц больше 12
            while month > 12:
                month -= 12
                year += 1

            events = store.get_events_for_month(year, month)

            for event in events:
                if title_lower in event["title"].lower():
                    return event
        return None
    
    def smart_schedule_event(self, result):
        """
        Умное распределение события по календарю
        Находит лучшее время на основе категории, приоритета и свободных слотов
        """
        from datetime import datetime, timedelta
        
        # Извлекаем информацию
        title = result["title"]
        category = result.get("category", "Personal")
        priority = result.get("priority", "Medium")
        duration_hours = result.get("duration_hours", 1)
        
        # Получаем оптимальное время для категории
        optimal_time = store.OPTIMAL_TIMES.get(category, {"start": 9, "end": 17})
        
        # Определяем дату (если не указана - сегодня)
        if "start" in result and result["start"] != "AUTO":
            # Используем указанную дату
            try:
                event_date = datetime.strptime(result["start"].split(" ")[0], "%Y-%m-%d")
            except:
                event_date = datetime.now()
        else:
            event_date = datetime.now()
        
        date_str = event_date.strftime("%Y-%m-%d")
        
        # Получаем события на этот день
        existing_events = store.get_events_for_date(date_str)
        
        # Находим лучший свободный слот
        best_slot = self.find_best_time_slot(
            existing_events,
            optimal_time["start"],
            optimal_time["end"],
            duration_hours,
            event_date
        )
        
        final_start = f"{date_str} {best_slot['start']}"
        final_end = f"{date_str} {best_slot['end']}"
        
        # Создаем событие
        store.add_event(
            title=title,
            start_date=final_start,
            end_date=final_end,
            description=result.get("description", ""),
            event_type=result.get("type", "event"),
            priority=priority,
            category=category
        )
        
        # Формируем умное сообщение
        category_emoji = store.CATEGORIES.get(category, "📌")
        
        if priority == "High":
            priority_msg = "🔥 High priority"
        elif priority == "Low":
            priority_msg = "✨ Low priority"
        else:
            priority_msg = ""
        
        response = f"{category_emoji} Scheduled: **{title}**\n"
        response += f"📅 {date_str} at {best_slot['start']}\n"
        if priority_msg:
            response += f"{priority_msg}\n"
        response += f"💡 I found the optimal time based on your schedule!"
        
        self.add_message(response, is_user=False)
        
        # НЕ обновляем здесь - обновление произойдет в process_command после всех задач
    
    def find_best_time_slot(self, existing_events, preferred_start, preferred_end, duration_hours, target_date):
        """Находит лучший свободный слот для события"""
        from datetime import datetime, timedelta
        
        # Создаем список занятых интервалов
        busy_intervals = []
        for event in existing_events:
            try:
                start_str = event["start"].split(" ")[1] if " " in event["start"] else "09:00"
                end_str = event["end"].split(" ")[1] if " " in event["end"] else "10:00"
                
                start_time = datetime.strptime(start_str, "%H:%M")
                end_time = datetime.strptime(end_str, "%H:%M")
                
                busy_intervals.append((start_time.hour * 60 + start_time.minute,
                                     end_time.hour * 60 + end_time.minute))
            except:
                continue
        
        # Ищем свободный слот в предпочтительном диапазоне
        duration_minutes = int(duration_hours * 60)
        
        for hour in range(preferred_start, preferred_end):
            start_minutes = hour * 60
            end_minutes = start_minutes + duration_minutes
            
            # Проверяем пересечения
            is_free = True
            for busy_start, busy_end in busy_intervals:
                if not (end_minutes <= busy_start or start_minutes >= busy_end):
                    is_free = False
                    break
            
            if is_free:
                start_time = f"{hour:02d}:00"
                end_hour = (hour + int(duration_hours))
                end_minute = int((duration_hours % 1) * 60)
                end_time = f"{end_hour:02d}:{end_minute:02d}"
                return {"start": start_time, "end": end_time}
        
        # Если не нашли в предпочтительном диапазоне, используем первый доступный слот
        default_start = f"{preferred_start:02d}:00"
        default_end_hour = preferred_start + int(duration_hours)
        default_end = f"{default_end_hour:02d}:00"
        return {"start": default_start, "end": default_end}
    
    def show_daily_schedule(self, date_str):
        """Показать краткое расписание на день"""
        from datetime import datetime
        
        events = store.get_events_for_date(date_str)
        
        if not events:
            return "📅 No events scheduled for this day."
        
        # Сортируем по времени
        events.sort(key=lambda e: e["start"])
        
        schedule_text = f"📅 Schedule for {date_str}:\n\n"
        
        for event in events[:5]:  # Показываем максимум 5 событий
            try:
                time_part = event["start"].split(" ")[1] if " " in event["start"] else "09:00"
                hour = time_part.split(":")[0]
                category_emoji = store.CATEGORIES.get(event.get("category", "Personal"), "📌")
                schedule_text += f"{hour}:00 - {category_emoji} {event['title']}\n"
            except (ValueError, IndexError, KeyError):
                continue
        
        if len(events) > 5:
            schedule_text += f"\n...and {len(events) - 5} more events"
        
        return schedule_text

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
        """
        ✅ ОБНОВЛЕНО: Теперь использует task_scheduler для планирования дня
        """
        try:
            # ✅ ИСПРАВЛЕНО: Проверяем хочет ли пользователь запланировать весь день
            # НЕ перехватываем "plan a meeting", "plan a workout" и т.д.
            text_lower = text.lower()
            
            # Проверяем ТОЧНЫЕ фразы для планирования дня
            is_day_planning = (
                "plan my day" in text_lower or
                "schedule my day" in text_lower or
                "план my day" in text_lower or
                "запланируй день" in text_lower or
                "распредели задачи" in text_lower or
                "мои задачи на сегодня" in text_lower or
                "что мне делать сегодня" in text_lower or
                # Специальный случай: "plan something" БЕЗ конкретики
                (text_lower.strip() == "plan something") or
                (text_lower.strip() == "plan my tasks")
            )
            
            if is_day_planning:
                # Используем task_scheduler для планирования всего дня
                from datetime import datetime
                current_date = datetime.now()
                
                result = self.task_scheduler.parse_tasks_from_text(text, current_date)
                
                # Создаём автоматически запланированные задачи
                for task in result["auto_scheduled"]:
                    store.add_event(
                        title=task["title"],
                        start_date=task["start"],
                        end_date=task["end"],
                        description=task.get("description", ""),
                        event_type=task.get("type", "event"),
                        priority=task.get("priority", "Medium"),
                        category=task.get("category", "Personal")
                    )
                
                # Формируем ответ
                response = "✅ I've scheduled your day!\n\n"
                response += "📅 **Auto-scheduled:**\n"
                for task in result["auto_scheduled"]:
                    emoji = store.CATEGORIES.get(task["category"], "📌")
                    time_str = task["start"].split(" ")[1] if " " in task["start"] else "09:00"
                    response += f"• {time_str} - {emoji} {task['title']}\n"
                
                if result["needs_clarification"]:
                    response += "\n⏰ **Need your input:**\n"
                    for task in result["needs_clarification"]:
                        emoji = store.CATEGORIES.get(task["category"], "📌")
                        suggested = task.get("suggested_start", "").split(" ")[1] if " " in task.get("suggested_start", "") else "Not set"
                        response += f"• {emoji} {task['title']}\n  Suggested: {suggested}\n"
                    response += "\nPlease specify when you'd like to do these tasks!"
                
                self.add_message(response, is_user=False)
                self.refresh_calendar()
                return
            
            # ✅ ОБЫЧНАЯ ЛОГИКА: Используем AI для разбора отдельных команд
            result = self.ai_service.process_message(text)
            
            # Проверяем формат ответа
            if isinstance(result, list):
                # Множественные задачи
                created_count = 0
                smart_scheduled_count = 0  # ✅ ДОБАВЛЕНО: счётчик умно запланированных
                
                for item in result:
                    if item.get("action") == "create":
                        # Проверяем нужно ли умное распределение
                        auto_schedule = item.get("auto_schedule", False)
                        
                        if auto_schedule or item.get("start") == "AUTO" or "AUTO" in str(item.get("start", "")):
                            # Используем умное распределение
                            self.smart_schedule_event(item)
                            smart_scheduled_count += 1  # ✅ ДОБАВЛЕНО
                        else:
                            # Обычное создание события с указанным временем
                            store.add_event(
                                title=item["title"],
                                start_date=item["start"],
                                end_date=item["end"],
                                description=item.get("description", ""),
                                event_type=item.get("type", "event"),
                                priority=item.get("priority", "Medium"),
                                category=item.get("category", "Personal")
                            )
                        
                        created_count += 1
                
                # Показываем итоговое сообщение
                if created_count > 0:
                    # ✅ ИСПРАВЛЕНО: НЕ дублируем если smart_schedule_event уже отправил
                    if smart_scheduled_count == 0:
                        # Только если НЕ использовали умное планирование
                        if created_count == 1:
                            first_item = result[0]
                            response_msg = first_item.get("response_message", f"✅ Event created! Check your calendar.")
                            self.add_message(response_msg, is_user=False)
                        else:
                            self.add_message(
                                f"✅ Created {created_count} tasks! Check your calendar.",
                                is_user=False
                            )
                    
                    # Обновляем календарь
                    self.refresh_calendar()
                
                return
            
            # Одиночное действие (dict)
            if result.get("action") == "chat":
                # Проверяем специальные команды
                user_text = text.lower()
                
                if "schedule" in user_text or "what's today" in user_text or "today's plan" in user_text:
                    from datetime import datetime
                    today = datetime.now().strftime("%Y-%m-%d")
                    schedule = self.show_daily_schedule(today)
                    self.add_message(schedule, is_user=False)
                else:
                    # Обычный чат
                    self.add_message(result.get("response_message", "I'm here to help!"), is_user=False)
            
            elif result.get("action") == "create":
                # Единичная задача
                auto_schedule = result.get("auto_schedule", False)
                
                if auto_schedule or result.get("start") == "AUTO":
                    self.smart_schedule_event(result)
                else:
                    store.add_event(
                        title=result["title"],
                        start_date=result["start"],
                        end_date=result["end"],
                        description=result.get("description", ""),
                        event_type=result.get("type", "event"),
                        priority=result.get("priority", "Medium"),
                        category=result.get("category", "Personal")
                    )
                    self.add_message(
                        f"✅ Scheduled: {result['title']} at {result['start']}",
                        is_user=False
                    )
                
                self.refresh_calendar()
            
            elif result.get("action") == "delete":
                title = result.get("title", "")
                event = self.find_event_by_title(title)
                
                if event:
                    store.delete_event(event["id"])
                    self.add_message(
                        result.get("response_message", f"✅ Deleted: {title}"),
                        is_user=False
                    )
                    self.refresh_calendar()
                else:
                    self.add_message(
                        f"❌ Event '{title}' not found. Please check the name and try again.",
                        is_user=False
                    )
            
            elif result.get("action") == "reschedule":
                title = result.get("title", "")
                event = self.find_event_by_title(title)
                
                if event:
                    store.update_event(
                        event["id"],
                        {
                            "start": result.get("new_start"),
                            "end": result.get("new_end")
                        }
                    )
                    self.add_message(
                        result.get("response_message", f"✅ Rescheduled: {title}"),
                        is_user=False
                    )
                    self.refresh_calendar()
                else:
                    self.add_message(
                        f"❌ Event '{title}' not found. Please check the name and try again.",
                        is_user=False
                    )
        
        except Exception as e:
            print(f"Error in process_command: {e}")
            import traceback
            traceback.print_exc()
            self.add_message(
                "❌ Sorry, I encountered an error. Please try again.",
                is_user=False
            )
    
    def refresh_calendar(self):
        """Обновляет календарь после изменений"""
        if self.on_refresh:
            self.on_refresh()