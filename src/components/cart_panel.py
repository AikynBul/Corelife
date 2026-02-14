import flet as ft
from data.store import store

class CartPanel(ft.AlertDialog):
    """Панель корзины покупок"""
    
    def __init__(self, page: ft.Page, user_info: dict, cart: dict, grocery_data: dict, on_purchase_complete):
        self.page_ref = page
        self.user_info = user_info
        self.cart = cart
        self.grocery_data = grocery_data
        self.on_purchase_complete = on_purchase_complete
        
        # ✅ ИСПРАВЛЕНО: Расчёты с правильной структурой
        from data.products import get_product_by_id
        
        self.subtotal = 0
        for product_id, data in cart.items():
            if "product" in data and isinstance(data["product"], dict):
                price = data["product"].get("price", 0)
                quantity = data.get("quantity", 0)
            else:
                product = get_product_by_id(product_id)
                price = product.get("price", 0) if product else data.get("price_per_unit", 0)
                quantity = data.get("quantity", 0)
            
            self.subtotal += price * quantity
        
        self.budget = grocery_data.get("weekly_budget", 0) if grocery_data else 0
        self.remaining = self.budget - self.subtotal
        
        super().__init__(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.SHOPPING_CART, size=28, color=ft.Colors.BLUE_600),
                ft.Text("Shopping Cart", size=20, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=self.build_content(),
            actions=self.build_actions(),
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def build_content(self):
        """Построить содержимое"""
        if not self.cart:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=64, color=ft.Colors.GREY_400),
                    ft.Text("Your cart is empty", size=16, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=40,
            )
        
        # Cart items
        items = []
        for product_id, data in self.cart.items():
            # ✅ ЗАЩИТА: Проверяем наличие product и price
            if "product" not in data or not isinstance(data["product"], dict):
                print(f"WARNING: Invalid cart item structure for {product_id}")
                continue
            
            product = data["product"]
            quantity = data.get("quantity", 0)
            
            # ✅ ЗАЩИТА: Проверяем price
            price = product.get("price", 0)
            if price == 0:
                # Если price отсутствует, пытаемся получить из products.py
                from data.products import get_product_by_id
                full_product = get_product_by_id(product_id)
                if full_product:
                    price = full_product.get("price", 0)
                    product["price"] = price  # Обновляем
            
            total = price * quantity
            
            item = ft.Container(
                content=ft.Row([
                    # Icon
                    ft.Text(product.get("icon", "📦"), size=24),
                    
                    # Info
                    ft.Column([
                        ft.Text(product.get("name", "Unknown"), size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{quantity} × {price:,} ₸", size=12, color=ft.Colors.GREY_600),
                    ], spacing=2, expand=True),
                    
                    # Total
                    ft.Text(f"{total:,} ₸", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
                    
                    # Delete
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=20,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Remove",
                        on_click=lambda _, pid=product_id: self.remove_item(pid),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_200),
                border_radius=8,
            )
            items.append(item)
        
        # Summary
        summary = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Subtotal:", size=14),
                    ft.Container(expand=True),
                    ft.Text(f"{self.subtotal:,} ₸", size=14, weight=ft.FontWeight.BOLD),
                ]),
                ft.Row([
                    ft.Text("Budget:", size=14, color=ft.Colors.GREY_600),
                    ft.Container(expand=True),
                    ft.Text(f"{self.budget:,} ₸", size=14, color=ft.Colors.GREY_600),
                ]),
                ft.Divider(),
                ft.Row([
                    ft.Text("Remaining:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text(
                        f"{self.remaining:,} ₸",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_600 if self.remaining >= 0 else ft.Colors.RED_600,
                    ),
                ]),
            ]),
            padding=15,
            border_radius=8,
            bgcolor=ft.Colors.GREY_50,
        )
        
        # Warning if over budget
        warning = None
        if self.remaining < 0:
            warning = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED_600, size=20),
                    ft.Text("Over budget!", size=14, color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                padding=10,
                border_radius=8,
                bgcolor=ft.Colors.RED_50,
                border=ft.border.all(1, ft.Colors.RED_200),
            )
        
        content_list = [
            ft.Column(items, spacing=10, scroll=ft.ScrollMode.AUTO, height=250),
            ft.Container(height=15),
            summary,
        ]
        
        if warning:
            content_list.append(ft.Container(height=10))
            content_list.append(warning)
        
        return ft.Container(
            content=ft.Column(content_list, spacing=0),
            width=500,
        )
    
    def build_actions(self):
        """Построить кнопки действий"""
        return [
            ft.TextButton("Close", on_click=lambda _: self.page_ref.close(self)),
            ft.TextButton(
                "Clear Cart",
                on_click=self.clear_cart,
                style=ft.ButtonStyle(color=ft.Colors.RED_600),
            ) if self.cart else None,
            ft.ElevatedButton(
                "Confirm Purchase",
                icon=ft.Icons.CHECK,
                on_click=self.confirm_purchase,
                disabled=self.remaining < 0 or not self.cart,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREEN_600,
                    padding=15,
                ),
            ) if self.cart else None,
        ]
    
    def remove_item(self, product_id):
        """Удалить товар из корзины"""
        if product_id in self.cart:
            del self.cart[product_id]
        
        # Обновляем в БД
        self.save_cart()
        
        # Перестраиваем UI
        self.content = self.build_content()
        self.actions = self.build_actions()
        self.update()
    
    def clear_cart(self, e):
        """Очистить корзину"""
        self.cart.clear()
        self.save_cart()
        
        self.page_ref.close(self)
        self.page_ref.show_snack_bar(
            ft.SnackBar(content=ft.Text("Cart cleared"), bgcolor=ft.Colors.ORANGE_600)
        )
    
    def confirm_purchase(self, e):
        """Подтвердить покупку"""
        # Показываем диалог подтверждения
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Purchase"),
            content=ft.Column([
                ft.Text(f"You are about to spend:"),
                ft.Text(f"{self.subtotal:,} ₸", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
                ft.Container(height=10),
                ft.Text(f"Remaining budget: {self.remaining:,} ₸", color=ft.Colors.GREY_600),
                ft.Container(height=10),
                ft.Text("This will be your grocery base for this week's diet plan.", size=12),
            ], tight=True, width=300),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.page_ref.close(confirm_dialog)),
                ft.ElevatedButton(
                    "Confirm",
                    on_click=lambda _: self.finalize_purchase(confirm_dialog),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN_600,
                    ),
                ),
            ],
        )
        
        self.page_ref.open(confirm_dialog)
    
    def finalize_purchase(self, confirm_dialog):
        """Завершить покупку"""
        # Подтверждаем в БД
        success = store.confirm_purchase(self.user_info["id"])
        
        self.page_ref.close(confirm_dialog)
        self.page_ref.close(self)
        
        if success:
            # ✅ ИСПРАВЛЕНО: Правильный API для SnackBar в Flet
            snackbar = ft.SnackBar(
                content=ft.Text(f"✅ Purchase confirmed! Spent: {self.subtotal:,} ₸"),
                bgcolor=ft.Colors.GREEN_600,
            )
            self.page_ref.overlay.append(snackbar)
            snackbar.open = True
            self.page_ref.update()
            
            if self.on_purchase_complete:
                self.on_purchase_complete()
        else:
            # ✅ ИСПРАВЛЕНО: Правильный API для SnackBar в Flet
            snackbar = ft.SnackBar(
                content=ft.Text("❌ Purchase failed. Please try again."),
                bgcolor=ft.Colors.RED_600,
            )
            self.page_ref.overlay.append(snackbar)
            snackbar.open = True
            self.page_ref.update()
    
    def save_cart(self):
        """Сохранить корзину в БД"""
        cart_items = []
        
        for product_id, data in self.cart.items():
            product = data["product"]
            quantity = data["quantity"]
            
            cart_items.append({
                "product_id": product_id,
                "name": product["name"],
                "quantity": quantity,
                "unit": product["unit"],
                "price_per_unit": product["price"],
                "total": product["price"] * quantity,
            })
        
        store.update_cart(self.user_info["id"], cart_items)
        
        # Пересчитываем
        self.subtotal = sum(item["total"] for item in cart_items)
        self.remaining = self.budget - self.subtotal