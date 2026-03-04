import flet as ft
from data.store import store


class CartPanel(ft.AlertDialog):
    def __init__(self, page, user_info, cart, grocery_data, on_purchase_complete):
        self.page_ref = page
        self.user_info = user_info
        self.cart = cart
        self.grocery_data = grocery_data
        self.on_purchase_complete = on_purchase_complete
        self.subtotal = self._calc_subtotal()
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

    def _calc_subtotal(self):
        total = 0
        for product_id, data in self.cart.items():
            if "product" in data and isinstance(data["product"], dict):
                price = data["product"].get("price", 0)
                if price == 0:
                    from data.products import get_product_by_id
                    full = get_product_by_id(product_id)
                    if full:
                        price = full.get("price", 0)
                        data["product"]["price"] = price
                total += price * data.get("quantity", 0)
        return total

    def build_content(self):
        if not self.cart:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=64, color=ft.Colors.GREY_400),
                    ft.Text("Your cart is empty", size=16, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=40,
            )
        items = []
        for product_id, data in self.cart.items():
            if "product" not in data or not isinstance(data["product"], dict):
                continue
            product = data["product"]
            quantity = data.get("quantity", 0)
            price = product.get("price", 0)
            if price == 0:
                from data.products import get_product_by_id
                full = get_product_by_id(product_id)
                if full:
                    price = full.get("price", 0)
                    product["price"] = price
            total_item = price * quantity
            items.append(ft.Container(
                content=ft.Row([
                    ft.Text(product.get("icon", "?"), size=22),
                    ft.Column([
                        ft.Text(product.get("name", "Unknown"), size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{quantity} x {price:,} T", size=12, color=ft.Colors.GREY_600),
                    ], spacing=2, expand=True),
                    ft.Text(f"{total_item:,} T", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_size=20, icon_color=ft.Colors.RED_400,
                        tooltip="Remove", on_click=lambda _, pid=product_id: self.remove_item(pid)),
                ], spacing=8),
                padding=10, border=ft.border.all(1, ft.Colors.GREY_200), border_radius=8,
            ))
        summary = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("Subtotal:", size=14), ft.Container(expand=True),
                        ft.Text(f"{self.subtotal:,} T", size=14, weight=ft.FontWeight.BOLD)]),
                ft.Row([ft.Text("Budget:", size=14, color=ft.Colors.GREY_600), ft.Container(expand=True),
                        ft.Text(f"{self.budget:,} T", size=14, color=ft.Colors.GREY_600)]),
                ft.Divider(),
                ft.Row([ft.Text("Remaining after purchase:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Text(f"{self.remaining:,} T", size=16, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_600 if self.remaining >= 0 else ft.Colors.RED_600)]),
            ], spacing=6),
            padding=15, border_radius=8, bgcolor=ft.Colors.GREY_50,
        )
        extra = []
        if self.remaining < 0:
            extra = [ft.Container(height=8), ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED_600, size=20),
                    ft.Text("Over budget!", size=13, color=ft.Colors.RED_600)], spacing=8),
                padding=10, border_radius=8, bgcolor=ft.Colors.RED_50,
                border=ft.border.all(1, ft.Colors.RED_200))]
        return ft.Container(
            content=ft.Column([
                ft.Column(items, spacing=8, scroll=ft.ScrollMode.AUTO, height=min(len(items)*65, 280)),
                ft.Container(height=12), summary,
            ] + extra, spacing=0),
            width=480,
        )

    def build_actions(self):
        actions = [ft.TextButton("Close", on_click=lambda _: self.page_ref.close(self))]
        if self.cart:
            actions.append(ft.TextButton("Clear Cart", on_click=self.clear_cart,
                style=ft.ButtonStyle(color=ft.Colors.RED_600)))
            actions.append(ft.ElevatedButton("Confirm Purchase", icon=ft.Icons.CHECK,
                on_click=self.confirm_purchase, disabled=self.remaining < 0,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600, padding=15)))
        return actions

    def remove_item(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
        self._save_pending_cart()
        self.subtotal = self._calc_subtotal()
        self.remaining = self.budget - self.subtotal
        self.content = self.build_content()
        self.actions = self.build_actions()
        self.update()

    def clear_cart(self, e):
        self.cart.clear()
        self._save_pending_cart()
        self.page_ref.close(self)
        self._snack("Cart cleared", ft.Colors.ORANGE_600)

    def _save_pending_cart(self):
        cart_items = []
        for pid, data in self.cart.items():
            if "product" not in data:
                continue
            p = data["product"]
            q = data["quantity"]
            price = p.get("price", 0)
            cart_items.append({"product_id": pid, "name": p.get("name",""), "quantity": q,
                "unit": p.get("unit",""), "price_per_unit": price, "total": price*q})
        store.update_cart(self.user_info["id"], cart_items)

    def confirm_purchase(self, e):
        dialog = ft.AlertDialog(
            modal=True, title=ft.Text("Confirm Purchase"),
            content=ft.Column([
                ft.Text("You are about to spend:"),
                ft.Text(f"{self.subtotal:,} T", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
                ft.Container(height=8),
                ft.Text(f"Remaining budget: {self.remaining:,} T", color=ft.Colors.GREY_600),
                ft.Container(height=8),
                ft.Text("Purchased items will be saved to your list.", size=12, color=ft.Colors.GREY_500),
            ], tight=True, width=300),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.page_ref.close(dialog)),
                ft.ElevatedButton("Confirm", on_click=lambda _: self._finalize(dialog),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600)),
            ],
        )
        self.page_ref.open(dialog)

    def _finalize(self, confirm_dialog):
        # store.confirm_purchase:
        #   - spent += subtotal
        #   - purchased_cart = existing_purchased + current_cart
        #   - cart = [], subtotal = 0
        # => нижняя панель исчезнет (cart пуст), Clear больше не затронет баланс
        success = store.confirm_purchase(self.user_info["id"])
        self.page_ref.close(confirm_dialog)
        self.page_ref.close(self)
        if success:
            self._snack(f"Purchase confirmed! Spent: {self.subtotal:,} T", ft.Colors.GREEN_600, duration=3000)
            if self.on_purchase_complete:
                self.on_purchase_complete()
        else:
            self._snack("Purchase failed. Please try again.", ft.Colors.RED_600)

    def _snack(self, text, color, duration=2000):
        snack = ft.SnackBar(content=ft.Text(text), bgcolor=color, duration=duration)
        self.page_ref.overlay.append(snack)
        snack.open = True
        self.page_ref.update()