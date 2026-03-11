import os
import flet as ft
from components.layout import AppLayout
from components.header import Header
from components.chat import ChatWidget
from components.login_view import LoginView
from components.onboarding_view import OnboardingView
from components.diet_quiz_view import DietQuizView
from utils.translations import translations
from data.store import store

def main(page: ft.Page):
    page.title = "Corelife"
    
    # ✅ ИСПРАВЛЕНО: Правильная установка иконки для Flet приложения
    # Flet требует путь к .ico или .png файлу
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "photos", "Logo_Corelife.png"))
    
    # Проверяем разные варианты имени файла
    if not os.path.exists(icon_path):
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "photos", "Logo Corelife.png"))
    
    if not os.path.exists(icon_path):
        # Пробуем в корне проекта
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "photos", "Logo_Corelife.png"))
    
    # ✅ ПРАВИЛЬНЫЙ СПОСОБ установки иконки в Flet
    if os.path.exists(icon_path):
        try:
            # Для desktop приложений
            page.window_icon = icon_path
            print(f"✅ Logo loaded: {icon_path}")
        except Exception as e:
            print(f"⚠️ Could not set icon: {e}")
    else:
        print(f"❌ Logo file not found. Tried: {icon_path}")
        print("📁 Please ensure Logo_Corelife.png is in the photos/ folder")
    
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Load saved language preference
    saved_language = page.client_storage.get("language")
    if saved_language:
        translations.set_language(saved_language)
    
    # Set Google Calendar-like colors
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    def on_login(user_info):
        """Обработка входа пользователя"""
        store.set_user(user_info["id"])
        
        # ✅ НОВОЕ: Проверка на gamemode аккаунт (модератор)
        if user_info.get("username") == "gamemode":
            print("🔑 Gamemode account detected - granting unlimited privileges")
            store.grant_gamemode_privileges(user_info["id"])
        
        # Выдаём 500 стартовых кредитов если поля credits ещё нет
        store.ensure_starter_credits(user_info["id"])
        
        # ✅ ИСПРАВЛЕНО: Полностью очищаем страницу перед показом онбординга
        page.clean()
        page.appbar = None
        page.update()
        
        try:
            has_onboarding = store.has_completed_onboarding(user_info["id"])
            
            if not has_onboarding:
                show_onboarding(user_info)
            else:
                show_app(user_info)
                
        except Exception as e:
            import traceback
            page.add(
                ft.Column([
                    ft.Text("An error occurred:", color=ft.Colors.RED, size=20),
                    ft.Text(str(e), color=ft.Colors.RED),
                    ft.Text(traceback.format_exc(), color=ft.Colors.RED, font_family="Consolas")
                ], scroll=ft.ScrollMode.AUTO)
            )
            page.update()

    def on_logout(e):
        """Обработка выхода из приложения"""
        store.set_user(None)
        page.clean()
        page.appbar = None
        show_login()

    def show_login():
        """Показывает экран входа"""
        page.clean()
        page.appbar = None
        login_view = LoginView(on_login=on_login)
        page.add(login_view)
        page.update()

    def refresh_ui():
        """Refresh all UI components when language changes"""
        page.clean()
        if hasattr(page, 'current_user_info'):
            show_app(page.current_user_info)
        else:
            show_login()

    def show_onboarding(user_info):
        """Показывает экран онбординга (выбор целей)"""
        page.current_user_info = user_info
        
        # ✅ ИСПРАВЛЕНО: Полностью очищаем страницу
        page.clean()
        page.appbar = None
        page.update()
        
        def on_onboarding_complete(selected_goals):
            """Обработка завершения выбора целей"""
            # Сохраняем цели в БД
            store.save_user_goals(user_info["id"], selected_goals)
            
            # ✅ ИСПРАВЛЕНО: Полностью очищаем перед переходом
            page.clean()
            page.appbar = None
            page.update()
            
            # Если выбрана диета - показываем тест
            if "diet" in selected_goals:
                show_diet_quiz(user_info)
            else:
                # Сразу показываем приложение
                show_app(user_info)
        
        onboarding_view = OnboardingView(page, user_info, on_onboarding_complete)
        page.add(onboarding_view)
        page.update()

    def show_diet_quiz(user_info):
        """Показывает тест на предпочтения диеты"""
        # ✅ ИСПРАВЛЕНО: Полностью очищаем страницу
        page.clean()
        page.appbar = None
        page.update()
        
        def on_quiz_complete():
            """Обработка завершения теста"""
            # ✅ ИСПРАВЛЕНО: Полностью очищаем перед показом приложения
            page.clean()
            page.appbar = None
            page.update()
            
            # Показываем приложение после теста
            show_app(user_info)
        
        quiz_view = DietQuizView(page, user_info, on_quiz_complete)
        page.add(quiz_view)
        page.update()

    def show_app(user_info):
        """Показывает основное приложение"""
        # ✅ ИСПРАВЛЕНО: Полностью очищаем страницу перед показом приложения
        page.clean()
        page.appbar = None
        page.update()
        
        # Store user info for language change refresh
        page.current_user_info = user_info
        
        # Initialize the main layout
        app_layout = AppLayout(page, user_info, on_logout)
        
        # Header needs to know about account click to switch view
        def on_account_click():
            app_layout.set_view("Account")

        def on_language_change():
            """Handle language change - refresh entire UI"""
            refresh_ui()

        def on_menu_click(e):
            """Handle menu button click to toggle sidebar"""
            app_layout.toggle_sidebar()

        page.appbar = Header(
            page,
            on_account_click,
            on_language_change=on_language_change,
            on_menu_click=on_menu_click,
            on_theme_change=on_language_change,
            user_info=user_info,        # ✅ FIX: передаём имя для аватара
        )
        
        # Use Stack to overlay ChatWidget
        # chat_fab_container хранится как ref чтобы GroceryStore мог менять bottom
        chat_fab_container = ft.Container(
            content=ChatWidget(page, on_refresh=app_layout.refresh_active_view),
            right=20,
            bottom=20,
        )

        def on_grocery_panel_show():
            """Поднять chat FAB выше нижней панели магазина (80px + отступ)"""
            chat_fab_container.bottom = 110
            try:
                page.update()
            except Exception:
                pass

        def on_grocery_panel_hide():
            """Вернуть chat FAB на обычную позицию"""
            chat_fab_container.bottom = 20
            try:
                page.update()
            except Exception:
                pass

        # Передаём callbacks в GroceryStore
        app_layout.grocery_view.on_panel_show = on_grocery_panel_show
        app_layout.grocery_view.on_panel_hide = on_grocery_panel_hide

        main_stack = ft.Stack(
            [app_layout, chat_fab_container],
            expand=True
        )
        
        page.add(main_stack)
        page.update()

        # Refresh credits badge now that appbar is on page
        # (ensure_starter_credits ran before header was built)
        try:
            if page.appbar and hasattr(page.appbar, 'refresh_credits'):
                page.appbar.refresh_credits()
        except Exception:
            pass

    # Start with login
    show_login()

if __name__ == "__main__":
    ft.app(target=main)