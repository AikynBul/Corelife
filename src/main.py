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
    
    # вњ… РРЎРџР РђР’Р›Р•РќРћ: РџСЂР°РІРёР»СЊРЅР°СЏ СѓСЃС‚Р°РЅРѕРІРєР° РёРєРѕРЅРєРё РґР»СЏ Flet РїСЂРёР»РѕР¶РµРЅРёСЏ
    # Flet С‚СЂРµР±СѓРµС‚ РїСѓС‚СЊ Рє .ico РёР»Рё .png С„Р°Р№Р»Сѓ
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "photos", "Logo_Corelife.png"))
    
    # РџСЂРѕРІРµСЂСЏРµРј СЂР°Р·РЅС‹Рµ РІР°СЂРёР°РЅС‚С‹ РёРјРµРЅРё С„Р°Р№Р»Р°
    if not os.path.exists(icon_path):
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "photos", "Logo Corelife.png"))
    
    if not os.path.exists(icon_path):
        # РџСЂРѕР±СѓРµРј РІ РєРѕСЂРЅРµ РїСЂРѕРµРєС‚Р°
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "photos", "Logo_Corelife.png"))
    
    # вњ… РџР РђР’РР›Р¬РќР«Р™ РЎРџРћРЎРћР‘ СѓСЃС‚Р°РЅРѕРІРєРё РёРєРѕРЅРєРё РІ Flet
    if os.path.exists(icon_path):
        try:
            # Р”Р»СЏ desktop РїСЂРёР»РѕР¶РµРЅРёР№
            page.window_icon = icon_path
            print(f"вњ… Logo loaded: {icon_path}")
        except Exception as e:
            print(f"вљ пёЏ Could not set icon: {e}")
    else:
        print(f"вќЊ Logo file not found. Tried: {icon_path}")
        print("рџ“Ѓ Please ensure Logo_Corelife.png is in the photos/ folder")
    
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
        """РћР±СЂР°Р±РѕС‚РєР° РІС…РѕРґР° РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""
        store.set_user(user_info["id"])
        

        if user_info.get("username") in ["admin", "administrator", "support"]:
            print("[Admin] privileged account detected")
            store.grant_admin_privileges(user_info["id"])
        
        # Р’С‹РґР°С‘Рј 500 СЃС‚Р°СЂС‚РѕРІС‹С… РєСЂРµРґРёС‚РѕРІ РµСЃР»Рё РїРѕР»СЏ credits РµС‰С‘ РЅРµС‚
        store.ensure_starter_credits(user_info["id"])
        
        # вњ… РРЎРџР РђР’Р›Р•РќРћ: РџРѕР»РЅРѕСЃС‚СЊСЋ РѕС‡РёС‰Р°РµРј СЃС‚СЂР°РЅРёС†Сѓ РїРµСЂРµРґ РїРѕРєР°Р·РѕРј РѕРЅР±РѕСЂРґРёРЅРіР°
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
        """РћР±СЂР°Р±РѕС‚РєР° РІС‹С…РѕРґР° РёР· РїСЂРёР»РѕР¶РµРЅРёСЏ"""
        store.set_user(None)
        page.clean()
        page.appbar = None
        show_login()

    def show_login():
        """РџРѕРєР°Р·С‹РІР°РµС‚ СЌРєСЂР°РЅ РІС…РѕРґР°"""
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
        """РџРѕРєР°Р·С‹РІР°РµС‚ СЌРєСЂР°РЅ РѕРЅР±РѕСЂРґРёРЅРіР° (РІС‹Р±РѕСЂ С†РµР»РµР№)"""
        page.current_user_info = user_info
        
        # вњ… РРЎРџР РђР’Р›Р•РќРћ: РџРѕР»РЅРѕСЃС‚СЊСЋ РѕС‡РёС‰Р°РµРј СЃС‚СЂР°РЅРёС†Сѓ
        page.clean()
        page.appbar = None
        page.update()
        
        def on_onboarding_complete(selected_goals):
            """РћР±СЂР°Р±РѕС‚РєР° Р·Р°РІРµСЂС€РµРЅРёСЏ РІС‹Р±РѕСЂР° С†РµР»РµР№"""
            # РЎРѕС…СЂР°РЅСЏРµРј С†РµР»Рё РІ Р‘Р”
            store.save_user_goals(user_info["id"], selected_goals)
            
            # вњ… РРЎРџР РђР’Р›Р•РќРћ: РџРѕР»РЅРѕСЃС‚СЊСЋ РѕС‡РёС‰Р°РµРј РїРµСЂРµРґ РїРµСЂРµС…РѕРґРѕРј
            page.clean()
            page.appbar = None
            page.update()
            
            # Р•СЃР»Рё РІС‹Р±СЂР°РЅР° РґРёРµС‚Р° - РїРѕРєР°Р·С‹РІР°РµРј С‚РµСЃС‚
            if "diet" in selected_goals:
                show_diet_quiz(user_info)
            else:
                # РЎСЂР°Р·Сѓ РїРѕРєР°Р·С‹РІР°РµРј РїСЂРёР»РѕР¶РµРЅРёРµ
                show_app(user_info)
        
        onboarding_view = OnboardingView(page, user_info, on_onboarding_complete)
        page.add(onboarding_view)
        page.update()

    def show_diet_quiz(user_info):
        """РџРѕРєР°Р·С‹РІР°РµС‚ С‚РµСЃС‚ РЅР° РїСЂРµРґРїРѕС‡С‚РµРЅРёСЏ РґРёРµС‚С‹"""
        # вњ… РРЎРџР РђР’Р›Р•РќРћ: РџРѕР»РЅРѕСЃС‚СЊСЋ РѕС‡РёС‰Р°РµРј СЃС‚СЂР°РЅРёС†Сѓ
        page.clean()
        page.appbar = None
        page.update()
        
        def on_quiz_complete():
            """РћР±СЂР°Р±РѕС‚РєР° Р·Р°РІРµСЂС€РµРЅРёСЏ С‚РµСЃС‚Р°"""
            # вњ… РРЎРџР РђР’Р›Р•РќРћ: РџРѕР»РЅРѕСЃС‚СЊСЋ РѕС‡РёС‰Р°РµРј РїРµСЂРµРґ РїРѕРєР°Р·РѕРј РїСЂРёР»РѕР¶РµРЅРёСЏ
            page.clean()
            page.appbar = None
            page.update()
            
            # РџРѕРєР°Р·С‹РІР°РµРј РїСЂРёР»РѕР¶РµРЅРёРµ РїРѕСЃР»Рµ С‚РµСЃС‚Р°
            show_app(user_info)
        
        quiz_view = DietQuizView(page, user_info, on_quiz_complete)
        page.add(quiz_view)
        page.update()

    def show_app(user_info):
        """РџРѕРєР°Р·С‹РІР°РµС‚ РѕСЃРЅРѕРІРЅРѕРµ РїСЂРёР»РѕР¶РµРЅРёРµ"""
        # вњ… РРЎРџР РђР’Р›Р•РќРћ: РџРѕР»РЅРѕСЃС‚СЊСЋ РѕС‡РёС‰Р°РµРј СЃС‚СЂР°РЅРёС†Сѓ РїРµСЂРµРґ РїРѕРєР°Р·РѕРј РїСЂРёР»РѕР¶РµРЅРёСЏ
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
            user_info=user_info,        # вњ… FIX: РїРµСЂРµРґР°С‘Рј РёРјСЏ РґР»СЏ Р°РІР°С‚Р°СЂР°
        )
        
        # Use Stack to overlay ChatWidget
        # chat_fab_container С…СЂР°РЅРёС‚СЃСЏ РєР°Рє ref С‡С‚РѕР±С‹ GroceryStore РјРѕРі РјРµРЅСЏС‚СЊ bottom
        chat_fab_container = ft.Container(
            content=ChatWidget(page, on_refresh=app_layout.refresh_active_view),
            right=20,
            bottom=20,
        )

        def on_grocery_panel_show():
            """РџРѕРґРЅСЏС‚СЊ chat FAB РІС‹С€Рµ РЅРёР¶РЅРµР№ РїР°РЅРµР»Рё РјР°РіР°Р·РёРЅР° (80px + РѕС‚СЃС‚СѓРї)"""
            chat_fab_container.bottom = 110
            try:
                page.update()
            except Exception:
                pass

        def on_grocery_panel_hide():
            """Р’РµСЂРЅСѓС‚СЊ chat FAB РЅР° РѕР±С‹С‡РЅСѓСЋ РїРѕР·РёС†РёСЋ"""
            chat_fab_container.bottom = 20
            try:
                page.update()
            except Exception:
                pass

        # РџРµСЂРµРґР°С‘Рј callbacks РІ GroceryStore
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


