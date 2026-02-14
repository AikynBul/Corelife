import flet as ft
from data.products import BUDGET_SUGGESTIONS

class BudgetDialog(ft.AlertDialog):
    """Диалог установки недельного бюджета на продукты"""
    
    def __init__(self, page: ft.Page, on_confirm, current_diet_goal=None):
        self.page_ref = page
        self.on_confirm_callback = on_confirm
        
        # Рекомендуемый бюджет на основе diet goal
        suggested_budget = 15000  # по умолчанию
        if current_diet_goal and current_diet_goal in BUDGET_SUGGESTIONS:
            suggested_budget = BUDGET_SUGGESTIONS[current_diet_goal]
        
        # Поле ввода бюджета
        self.budget_field = ft.TextField(
            label="Your weekly budget",
            value=str(suggested_budget),
            suffix_text="₸",
            keyboard_type=ft.KeyboardType.NUMBER,
            text_size=24,
            border_radius=10,
            filled=True,
            width=300,
            text_align=ft.TextAlign.CENTER,
            autofocus=True,
        )
        
        # Быстрые кнопки выбора
        quick_buttons = ft.Row([
            ft.OutlinedButton(
                "10,000 ₸",
                on_click=lambda _: self.set_quick_budget(10000),
                width=90,
            ),
            ft.OutlinedButton(
                "15,000 ₸",
                on_click=lambda _: self.set_quick_budget(15000),
                width=90,
            ),
            ft.OutlinedButton(
                "20,000 ₸",
                on_click=lambda _: self.set_quick_budget(20000),
                width=90,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        
        super().__init__(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=28, color=ft.Colors.GREEN_600),
                ft.Text("Set Weekly Budget", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "How much can you spend on groceries this week?",
                        size=14,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=15),
                    
                    self.budget_field,
                    
                    ft.Container(height=10),
                    ft.Text("Quick select:", size=12, color=ft.Colors.GREY_600),
                    quick_buttons,
                    
                    ft.Container(height=15),
                    
                    # Info box
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=ft.Colors.BLUE_600),
                                ft.Text("Budget Tips", size=12, weight=ft.FontWeight.BOLD),
                            ], spacing=8),
                            ft.Container(height=5),
                            ft.Text("• Recommended: 12,000-18,000 ₸/week", size=11),
                            ft.Text("• About ~$30-40 USD per week", size=11),
                            ft.Text("• You can change this anytime", size=11),
                        ], spacing=3),
                        padding=12,
                        border_radius=8,
                        bgcolor=ft.Colors.BLUE_50,
                        border=ft.border.all(1, ft.Colors.BLUE_200),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                width=400,
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda _: self.page_ref.close(self),
                ),
                ft.ElevatedButton(
                    "Set Budget",
                    icon=ft.Icons.CHECK,
                    on_click=self.confirm_budget,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN_600,
                        padding=15,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def set_quick_budget(self, amount):
        """Установить бюджет быстрой кнопкой"""
        self.budget_field.value = str(amount)
        self.budget_field.update()
    
    def confirm_budget(self, e):
        """Подтвердить бюджет"""
        try:
            budget = int(self.budget_field.value.replace(",", "").replace(" ", ""))
            
            if budget <= 0:
                self.budget_field.error_text = "Budget must be positive"
                self.budget_field.update()
                return
            
            if budget < 5000:
                self.budget_field.error_text = "Too low (min 5,000 ₸)"
                self.budget_field.update()
                return
            
            self.page_ref.close(self)
            
            if self.on_confirm_callback:
                self.on_confirm_callback(budget)
        
        except ValueError:
            self.budget_field.error_text = "Invalid number"
            self.budget_field.update()