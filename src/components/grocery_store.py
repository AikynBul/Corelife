import flet as ft
from data.store import store
from data.products import PRODUCTS, CATEGORIES
from components.budget_dialog import BudgetDialog
from utils.translations import translations  # ✅ ПРАВИЛЬНЫЙ путь

class GroceryStore(ft.Container):
    """Страница продуктового магазина с бюджетом и корзиной"""
    
    def __init__(self, page: ft.Page, user_info: dict, on_refresh=None,
                 on_panel_show=None, on_panel_hide=None):
        super().__init__()
        self.page_ref = page
        self.user_info = user_info
        self.on_refresh = on_refresh
        # Callbacks для поднятия/опускания chat FAB при появлении нижней панели
        self.on_panel_show = on_panel_show
        self.on_panel_hide = on_panel_hide
        self.expand = True
        self.padding = 20
        
        # Состояние
        self.current_category = "fruits"
        self.view_mode = "shop"  # ✅ НОВОЕ: "shop" или "purchased"
        self.cart = {}  # {product_id: {product, quantity}}
        self.grocery_data = None
        
        # Загружаем данные
        self.load_grocery_data()
        
        # Если нет бюджета - показываем диалог
        if not self.grocery_data or not self.grocery_data.get("weekly_budget"):
            self.page_ref.run_task(self.show_budget_dialog_async)
        
        self.build_ui()
        
        # ✅ ИСПРАВЛЕНО: Показываем bottom panel только если в shop mode И корзина не пустая
        # НО НЕ показываем при инициализации, только при переключении на Grocery
        # (панель будет показана в layout.py при set_view("Grocery"))
    
    async def show_bottom_panel_async(self):
        """Показать bottom panel асинхронно после инициализации"""
        import asyncio
        await asyncio.sleep(0.1)  # Небольшая задержка для UI
        self.build_bottom_panel()
    
    async def show_budget_dialog_async(self):
        """Показать диалог бюджета асинхронно"""
        import asyncio
        await asyncio.sleep(0.3)  # Небольшая задержка для UI
        self.show_budget_dialog()
    
    def load_grocery_data(self):
        """Загрузить данные о бюджете и текущей корзине из БД."""
        self.grocery_data = store.get_user_groceries(self.user_info["id"])
        # initialize_starter_inventory убрана — она перезаписывала purchased_cart
        
        if self.grocery_data:
            # Загружаем корзину
            cart_items = self.grocery_data.get("cart", [])
            self.cart = {}
            
            # ✅ ИСПРАВЛЕНО: Преобразуем структуру из БД в правильный формат
            from data.products import get_product_by_id
            
            for item in cart_items:
                product_id = item["product_id"]
                
                # Пытаемся получить полный продукт из products.py
                full_product = get_product_by_id(product_id)
                
                if full_product:
                    # Используем полные данные из products.py
                    self.cart[product_id] = {
                        "product": {
                            "id": full_product["id"],
                            "name": full_product["name"],
                            "price": full_product["price"],  # ✅ Берём из products.py
                            "unit": full_product["unit"],
                            "icon": full_product.get("icon", "📦"),
                        },
                        "quantity": item["quantity"]
                    }
                else:
                    # Fallback: используем данные из БД
                    self.cart[product_id] = {
                        "product": {
                            "id": product_id,
                            "name": item.get("name", "Unknown"),
                            "price": item.get("price_per_unit", 0),
                            "unit": item.get("unit", ""),
                            "icon": "📦",
                        },
                        "quantity": item["quantity"]
                    }
    
    def build_view_tabs(self):
        """✅ НОВОЕ: Построить табы Shop / Purchased"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(
                        f"🛍️ {translations.get('shop')}",  # ✅ Перевод
                        size=16,
                        weight=ft.FontWeight.BOLD if self.view_mode == "shop" else ft.FontWeight.NORMAL,
                        color=ft.Colors.BLUE_600 if self.view_mode == "shop" else None,  # ✅ Theme-aware
                    ),
                    padding=15,
                    border_radius=8,
                    bgcolor=ft.Colors.BLUE_50 if self.view_mode == "shop" else None,
                    on_click=lambda _: self.switch_view_mode("shop"),
                    ink=True,
                ),
                ft.Container(width=10),
                ft.Container(
                    content=ft.Text(
                        f"📦 {translations.get('purchased_items')}",  # ✅ Перевод
                        size=16,
                        weight=ft.FontWeight.BOLD if self.view_mode == "purchased" else ft.FontWeight.NORMAL,
                        color=ft.Colors.GREEN_600 if self.view_mode == "purchased" else None,  # ✅ Theme-aware
                    ),
                    padding=15,
                    border_radius=8,
                    bgcolor=ft.Colors.GREEN_50 if self.view_mode == "purchased" else None,
                    on_click=lambda _: self.switch_view_mode("purchased"),
                    ink=True,
                ),
            ], spacing=0),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
        )
    
    def switch_view_mode(self, mode):
        """✅ НОВОЕ: Переключить режим просмотра"""
        self.view_mode = mode
        # ✅ ИСПРАВЛЕНО: Триггерим refresh через callback
        if self.on_refresh:
            self.on_refresh()
    
    def build_purchased_items(self):
        """✅ НОВОЕ: Показать купленные товары с возможностью удаления"""
        if not self.grocery_data or not self.grocery_data.get("purchased"):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_BAG_OUTLINED, size=64),  # ✅ Убран color
                    ft.Text(translations.get("no_purchases"), size=18),  # ✅ Перевод + убран color
                    ft.Text(translations.get("buy_groceries_first"), size=14),  # ✅ Перевод + убран color
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=50,
                alignment=ft.alignment.center,
                expand=True,
            )
        
        # ИСПРАВЛЕНО: читаем из purchased_cart (cart очищается после покупки)
        cart_items = self.grocery_data.get("purchased_cart", [])
        if not cart_items:
            cart_items = self.grocery_data.get("cart", [])  # fallback для старых записей
        if not cart_items:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_BAG_OUTLINED, size=64),
                    ft.Text(translations.get("no_purchases"), size=18),
                    ft.Text(translations.get("buy_groceries_first"), size=14),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=50, alignment=ft.alignment.center, expand=True,
            )
        
        items_list = []
        for item in cart_items:
            item_card = ft.Container(
                content=ft.Row([
                    ft.Text(item.get("name", "Unknown"), size=16, weight=ft.FontWeight.BOLD, expand=True),
                    ft.Column([
                        ft.Text(f"{item.get('quantity', 0)} {item.get('unit', '')}", size=14),  # ✅ Убран color
                        ft.Text(f"{item.get('total', 0):,} ₸", size=14, color=ft.Colors.BLUE_600, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2),
                    # ✅ НОВОЕ: Кнопка удаления
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        icon_size=20,
                        tooltip=translations.get("remove"),  # ✅ Перевод
                        on_click=lambda _, product_id=item.get("product_id"): self.remove_purchased_item(product_id),
                    ),
                ]),
                padding=15,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.OUTLINE),  # ✅ Тёмная тема
                bgcolor=None,  # ✅ Тёмная тема
            )
            items_list.append(item_card)
        
        # Summary
        total = self.grocery_data.get("spent", 0)
        summary = ft.Container(
            content=ft.Row([
                ft.Text(f"{translations.get('total_spent')}:", size=18, weight=ft.FontWeight.BOLD),  # ✅ Перевод
                ft.Text(f"{total:,} ₸", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            border_radius=10,
            bgcolor=ft.Colors.GREEN_50,
            border=ft.border.all(2, ft.Colors.GREEN_200),
        )
        
        return ft.Container(
            content=ft.Column([
                summary,
                ft.Container(height=15),
                ft.Column(items_list, spacing=10),
            ], scroll=ft.ScrollMode.AUTO),
            padding=15,
            expand=True,
        )
    
    def remove_purchased_item(self, product_id):
        """✅ НОВОЕ: Удалить товар из купленных"""
        if not self.grocery_data:
            return
        
        # ИСПРАВЛЕНО: читаем из purchased_cart
        cart_items = self.grocery_data.get("purchased_cart", [])
        if not cart_items:
            cart_items = self.grocery_data.get("cart", [])
        
        # Удаляем товар
        cart_items = [item for item in cart_items if item.get("product_id") != product_id]
        
        # Пересчитываем spent
        new_spent = sum(item.get("total", 0) for item in cart_items)
        
        # Обновляем в БД
        store.update_purchased_items(self.user_info["id"], cart_items, new_spent)
        
        # Перезагружаем данные
        self.load_grocery_data()
        
        # Обновляем UI
        self.build_ui()
        self.update()
        
        # Показываем уведомление
        snackbar = ft.SnackBar(
            content=ft.Text("✅ Item removed"),
            bgcolor=ft.Colors.ORANGE_600,
            duration=1000,
        )
        self.page_ref.overlay.append(snackbar)
        snackbar.open = True
        self.page_ref.update()
    
    def show_budget_dialog(self):
        """Показать диалог установки бюджета"""
        dialog = BudgetDialog(
            self.page_ref,
            on_confirm=self.on_budget_set
        )
        self.page_ref.open(dialog)
    
    def on_budget_set(self, budget):
        """Обработать установку бюджета"""
        success = store.set_user_budget(self.user_info["id"], budget)

        if success:
            self.load_grocery_data()
            # Rebuild UI so budget display updates immediately
            self.build_ui()
            try:
                self.update()
            except Exception:
                self.page_ref.update()

            self.page_ref.open(ft.SnackBar(
                content=ft.Text(f"✅ Budget set: {budget:,} ₸"),
                bgcolor=ft.Colors.GREEN_600,
            ))
    
    def build_ui(self):
        """Построить UI"""
        # Header
        header = self.build_header()
        
        # ✅ НОВОЕ: View mode tabs (Shop / Purchased)
        view_tabs = self.build_view_tabs()
        
        # Category tabs или purchased list
        if self.view_mode == "shop":
            tabs = self.build_category_tabs()
            content = self.build_products_grid()
        else:
            tabs = ft.Container(height=0)  # Пустой для purchased view
            content = self.build_purchased_items()
        
        # Основной контент
        main_content = ft.Column([
            header,
            ft.Divider(height=1),
            view_tabs,
            tabs,
            ft.Container(height=10),
            content,
            ft.Container(height=120),  # Отступ для bottom panel
        ], expand=True, scroll=ft.ScrollMode.AUTO)
        
        # ✅ НОВОЕ: Используем Stack для overlay bottom panel ВНУТРИ контейнера
        # Это делает панель частью GroceryStore, а не глобальной
        self.content = ft.Stack([
            main_content,
            # Bottom panel будет добавлен динамически через update_bottom_panel()
        ], expand=True)
    
    def build_header(self):
        """Построить header с бюджетом"""
        if not self.grocery_data:
            remaining = 0
            budget = 0
        else:
            remaining = self.grocery_data.get("remaining", 0)
            budget = self.grocery_data.get("weekly_budget", 0)
        
        # Цвет в зависимости от остатка
        if remaining < 0:
            budget_color = ft.Colors.RED_600
            budget_icon = ft.Icons.WARNING
        elif remaining < 1000:
            budget_color = ft.Colors.ORANGE_600
            budget_icon = ft.Icons.INFO
        else:
            budget_color = ft.Colors.GREEN_600
            budget_icon = ft.Icons.CHECK_CIRCLE
        
        return ft.Container(
            content=ft.Row([
                # Left: Store info
                ft.Column([
                    ft.Text("🛒 Grocery Store", size=24, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Icon(ft.Icons.LOCATION_ON, size=14, color=ft.Colors.GREY_600),
                        ft.Text("Small, Semey", size=12, color=ft.Colors.GREY_600),
                    ], spacing=5),
                ], spacing=2),
                
                ft.Container(expand=True),
                
                # Right: Budget
                ft.Column([
                    ft.Row([
                        ft.Icon(budget_icon, size=20, color=budget_color),
                        ft.Text(f"{remaining:,} ₸", size=20, weight=ft.FontWeight.BOLD, color=budget_color),
                    ], spacing=8),
                    ft.Text(f"of {budget:,} ₸", size=12, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2),
                
                ft.Container(width=10),
                
                # Budget settings
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    tooltip="Change budget",
                    on_click=lambda _: self.show_budget_dialog()
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=15,
        )
    
    def build_category_tabs(self):
        """Построить табы категорий"""
        tabs = []
        
        for cat_id, cat_info in CATEGORIES.items():
            is_active = cat_id == self.current_category
            
            tab = ft.Container(
                content=ft.Row([
                    ft.Text(cat_info["icon"], size=18),
                    ft.Text(cat_info["name"], size=14, weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL),
                ], spacing=8),
                padding=ft.padding.symmetric(horizontal=15, vertical=10),
                border_radius=8,
                bgcolor=ft.Colors.BLUE_100 if is_active else None,
                ink=True,
                on_click=lambda _, cid=cat_id: self.switch_category(cid),
            )
            tabs.append(tab)
        
        return ft.Container(
            content=ft.Row(tabs, spacing=5, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=15),
        )
    
    def switch_category(self, category_id):
        """Переключить категорию"""
        self.current_category = category_id
        # ✅ ИСПРАВЛЕНО: Триггерим refresh через callback
        if self.on_refresh:
            self.on_refresh()
    
    def build_products_grid(self):
        """Построить сетку продуктов"""
        products = PRODUCTS.get(self.current_category, [])
        
        cards = []
        for product in products:
            card = self.build_product_card(product)
            cards.append(card)
        
        # Responsive grid
        return ft.Container(
            content=ft.GridView(
                controls=cards,
                runs_count=3,  # 3 колонки
                max_extent=250,
                spacing=15,
                run_spacing=15,
                padding=15,
            ),
            expand=True,
        )
    
    def build_product_card(self, product):
        """Построить карточку продукта"""
        product_id = product["id"]
        in_cart = product_id in self.cart
        quantity = self.cart[product_id]["quantity"] if in_cart else 0
        
        return ft.Container(
            content=ft.Column([
                # Icon
                ft.Text(product["icon"], size=48),
                ft.Container(height=5),
                
                # Name
                ft.Text(
                    product["name"],
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=2,
                ),
                
                # Unit
                ft.Text(
                    product["unit"],
                    size=12,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER,
                ),
                
                ft.Container(height=5),
                
                # Price
                ft.Text(
                    f"{product['price']:,} ₸",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_600,
                ),
                
                ft.Container(height=10),
                
                # Quantity selector
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.REMOVE,
                        icon_size=18,
                        on_click=lambda _, p=product: self.decrease_quantity(p),
                        disabled=quantity == 0,
                    ),
                    ft.Container(
                        content=ft.Text(str(quantity), size=16, weight=ft.FontWeight.BOLD),
                        width=30,
                        alignment=ft.alignment.center,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_size=18,
                        on_click=lambda _, p=product: self.increase_quantity(p),
                    ),
                ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Container(height=5),
                
                # ✅ УБРАНО: Add to cart button теперь не нужна
                # Кнопка будет в bottom panel
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_300),
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_400),
        )
    
    def increase_quantity(self, product):
        """Увеличить количество"""
        product_id = product["id"]
        
        if product_id in self.cart:
            self.cart[product_id]["quantity"] += 1
        else:
            self.cart[product_id] = {"product": product, "quantity": 1}
        
        # ✅ ИСПРАВЛЕНО: Partial update - только grid + bottom panel
        self.save_cart()
        self.update_products_display()
    
    def decrease_quantity(self, product):
        """Уменьшить количество"""
        product_id = product["id"]
        
        if product_id in self.cart:
            self.cart[product_id]["quantity"] -= 1
            
            if self.cart[product_id]["quantity"] <= 0:
                del self.cart[product_id]
        
        # ✅ ИСПРАВЛЕНО: Partial update - только grid + bottom panel
        self.save_cart()
        self.update_products_display()
    
    def update_products_display(self):
        """Обновить только products grid (Stack->Column->controls[5])."""
        if self.view_mode != "shop":
            return
        try:
            # self.content = Stack, controls[0] = main Column
            main_col = self.content.controls[0]
            main_col.controls[5] = self.build_products_grid()
            main_col.update()
        except Exception as ex:
            print(f"[GroceryStore] update_products_display fallback: {ex}")
            self.build_ui()
            self.update()
        self.build_bottom_panel()
    
    def add_to_cart(self, product):
        """Добавить в корзину"""
        product_id = product["id"]
        
        if product_id in self.cart:
            # Увеличиваем количество
            self.cart[product_id]["quantity"] += 1
        else:
            # ✅ ИСПРАВЛЕНО: Создаём ПОЛНЫЙ объект с price
            self.cart[product_id] = {
                "product": {
                    "id": product["id"],
                    "name": product["name"],
                    "price": product["price"],  # ✅ КРИТИЧНО: добавляем price!
                    "unit": product["unit"],
                    "icon": product.get("icon", "📦"),
                },
                "quantity": 1
            }
        
        # Сохраняем в БД
        self.save_cart()
        
        # ✅ Обновляем bottom panel
        self.build_bottom_panel()
        
        # ✅ ИСПРАВЛЕНО: Правильный API для snackbar
        snackbar = ft.SnackBar(
            content=ft.Text(f"✅ {product['name']} added to cart"),
            bgcolor=ft.Colors.GREEN_600,
            duration=1000,
        )
        self.page_ref.overlay.append(snackbar)
        snackbar.open = True
        self.page_ref.update()
    
    def save_cart(self):
        """Сохранить корзину в БД"""
        from data.products import get_product_by_id
        
        cart_items = []
        
        for product_id, data in self.cart.items():
            # ✅ ИСПРАВЛЕНО: Правильное получение product
            if "product" in data and isinstance(data["product"], dict):
                # Новый item (только что добавленный в этой сессии)
                product = data["product"]
                quantity = data["quantity"]
            else:
                # Загруженный из БД - нужно получить product из database
                product = get_product_by_id(product_id)
                quantity = data.get("quantity", 0)
                
                if not product:
                    # Продукт не найден, пропускаем
                    continue
            
            price = product.get("price", 0)
            total = price * quantity
            
            print(f"SAVE_CART: {product_id} - price={price}, qty={quantity}, total={total}")
            
            cart_items.append({
                "product_id": product_id,
                "name": product.get("name", ""),
                "quantity": quantity,
                "unit": product.get("unit", ""),
                "price_per_unit": price,
                "total": total,
            })
        
        # Вычисляем общий subtotal
        subtotal = sum(item["total"] for item in cart_items)
        print(f"SAVE_CART: Total cart subtotal = {subtotal}")
        
        store.update_cart(self.user_info["id"], cart_items)
        # ✅ НЕ вызываем load_grocery_data() здесь - это перезаписывает cart!
    
    def build_bottom_panel(self):
        """✅ НОВОЕ: Построить bottom summary panel"""
        # Сначала удаляем старую панель
        self.clear_bottom_panel()
        
        # Считаем totals
        total_items = 0
        subtotal = 0
        
        # ✅ ИСПРАВЛЕНО: Правильная структура cart
        for product_id, data in self.cart.items():
            if "product" in data and isinstance(data["product"], dict):
                # Это product object из кода
                price = data["product"].get("price", 0)
                quantity = data.get("quantity", 0)
                print(f"DEBUG: New item {product_id}: price={price}, qty={quantity}")
            else:
                # Это данные из БД (уже сохранённые)
                price = data.get("price_per_unit", 0)
                quantity = data.get("quantity", 0)
                print(f"DEBUG: DB item {product_id}: price={price}, qty={quantity}")
            
            total_items += quantity
            subtotal += price * quantity
        
        print(f"DEBUG: Total items={total_items}, subtotal={subtotal}")
        
        if not self.grocery_data:
            budget = 0
            remaining = 0
        else:
            budget = self.grocery_data.get("weekly_budget", 0)
            remaining = budget - subtotal
        
        # Если корзина пустая - не показываем panel
        if total_items == 0:
            return
        
        # Цвет в зависимости от остатка
        if remaining < 0:
            remaining_color = ft.Colors.RED_600
        elif remaining < 1000:
            remaining_color = ft.Colors.ORANGE_600
        else:
            remaining_color = ft.Colors.GREEN_600
        
        # Bottom panel
        # ✅ ПРАВИЛЬНОЕ позиционирование для page.overlay
        panel = ft.Container(
            content=ft.Row([
                # Left: Summary
                ft.Column([
                    ft.Row([
                        ft.Text("Selected:", size=12, color=ft.Colors.GREY_700),
                        ft.Text(f"{total_items} items", size=12, weight=ft.FontWeight.BOLD),
                    ], spacing=5),
                    ft.Row([
                        ft.Text("Total:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{subtotal:,} ₸", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
                    ], spacing=8),
                ], spacing=2),
                
                ft.Container(width=20),
                
                # Middle: Remaining
                ft.Column([
                    ft.Text("After purchase:", size=11, color=ft.Colors.GREY_600),
                    ft.Row([
                        ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=16, color=remaining_color),
                        ft.Text(f"{remaining:,} ₸", size=14, weight=ft.FontWeight.BOLD, color=remaining_color),
                    ], spacing=5),
                ], spacing=2),
                
                ft.Container(expand=True),
                
                # Right: Buttons
                ft.Row([
                    ft.OutlinedButton(
                        "Clear",
                        icon=ft.Icons.CLEAR,
                        on_click=lambda _: self.clear_cart(),
                        style=ft.ButtonStyle(color=ft.Colors.RED_600),
                    ),
                    ft.ElevatedButton(
                        "Buy Selected",
                        icon=ft.Icons.SHOPPING_CART_CHECKOUT,
                        on_click=lambda _: self.show_cart(),
                        disabled=remaining < 0,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.GREEN_600,
                            padding=15,
                        ),
                    ),
                ], spacing=10),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(left=250, right=15, top=15, bottom=15),  # ✅ Учитываем sidebar!
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(top=ft.BorderSide(2, ft.Colors.GREY_300)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(0, -2),
            ),
            # ✅ КРИТИЧНО для page.overlay - БЕЗ ЭТОГО панель занимает весь экран!
            bottom=0,
            left=0,   # Начинается с левого края (от page, не от content_area)
            right=0,  # До правого края
            height=80,
        )
        
        # ✅ Помечаем панель специальным атрибутом для идентификации
        panel.data = "grocery_bottom_panel"
        
        self.page_ref.overlay.append(panel)
        self.page_ref.update()
        # Уведомляем layout — нужно поднять chat FAB
        if self.on_panel_show:
            self.on_panel_show()
    
    def clear_bottom_panel(self):
        """✅ НОВОЕ: Удалить bottom panel из overlay"""
        to_remove = []
        for item in self.page_ref.overlay:
            # Ищем панель по data атрибуту
            if hasattr(item, 'data') and item.data == "grocery_bottom_panel":
                to_remove.append(item)
        
        for item in to_remove:
            self.page_ref.overlay.remove(item)
        
        if to_remove:
            print(f"CLEAR_BOTTOM_PANEL: Removed {len(to_remove)} panels")
            self.page_ref.update()
    
    def clear_cart(self):
        """Очистить текущую корзину. Купленные товары (purchased_cart) не трогаем."""
        self.cart = {}
        self.save_cart()
        self.clear_bottom_panel()
        # Уведомляем layout о поднятии FAB обратно
        if self.on_panel_hide:
            self.on_panel_hide()
        # Обновляем только grid продуктов
        try:
            main_col = self.content.controls[0]
            main_col.controls[5] = self.build_products_grid()
            main_col.update()
        except Exception:
            if self.on_refresh:
                self.on_refresh()
    
    def build_cart_button(self):
        """Построить floating кнопку корзины"""
        cart_count = sum(data["quantity"] for data in self.cart.values())
        
        return ft.FloatingActionButton(
            content=ft.Stack([
                ft.Icon(ft.Icons.SHOPPING_CART, color=ft.Colors.WHITE, size=28),
                ft.Container(
                    content=ft.Text(
                        str(cart_count),
                        color=ft.Colors.WHITE,
                        size=10,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=2,
                    border_radius=8,
                    bgcolor=ft.Colors.RED_600,
                    width=16,
                    height=16,
                    alignment=ft.alignment.center,
                    top=-5,
                    right=-5,
                ) if cart_count > 0 else ft.Container(width=0),
            ]),
            on_click=lambda _: self.show_cart(),
            bgcolor=ft.Colors.BLUE_600,
        )
    
    def show_cart(self):
        """Показать панель корзины"""
        from components.cart_panel import CartPanel
        
        panel = CartPanel(
            page=self.page_ref,
            user_info=self.user_info,
            cart=self.cart,
            grocery_data=self.grocery_data,
            on_purchase_complete=self.on_purchase_complete,  # ✅ ИСПРАВЛЕНО: передаём callback
        )
        
        self.page_ref.open(panel)
    
    def on_purchase_complete(self):
        """Callback после покупки: убираем панель, переключаемся на Purchased."""
        print("[GroceryStore] on_purchase_complete")
        self.cart = {}
        self.clear_bottom_panel()
        # Уведомляем layout — FAB возвращается вниз
        if self.on_panel_hide:
            self.on_panel_hide()
        self.load_grocery_data()
        self.view_mode = "purchased"
        self.build_ui()
        self.update()