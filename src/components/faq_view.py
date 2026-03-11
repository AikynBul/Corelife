import flet as ft
from data.faq_data import FAQ_ITEMS


class FAQView(ft.Container):
    CATEGORY_COLORS_DARK = {
        "General": ft.Colors.BLUE_900,
        "Diet": ft.Colors.GREEN_900,
        "Calendar": ft.Colors.PURPLE_900,
        "Grocery": ft.Colors.ORANGE_900,
    }

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, padding=20, alignment=ft.alignment.top_center)
        self.page_ref = page

        is_dark_theme = self.page_ref.theme_mode == ft.ThemeMode.DARK
        card_border = ft.Colors.GREY_700 if is_dark_theme else ft.Colors.GREY_300
        answer_text_color = ft.Colors.GREY_200 if is_dark_theme else ft.Colors.GREY_800
        answer_bg = (
            ft.Colors.with_opacity(0.18, ft.Colors.BLACK)
            if is_dark_theme
            else ft.Colors.with_opacity(0.06, ft.Colors.GREY_600)
        )

        style_palette = [
            (ft.Icons.ADD_CIRCLE_OUTLINE, ft.Colors.BLUE_400),
            (ft.Icons.CALENDAR_MONTH, ft.Colors.INDIGO_400),
            (ft.Icons.RESTAURANT_MENU, ft.Colors.ORANGE_400),
            (ft.Icons.LANGUAGE, ft.Colors.GREEN_400),
            (ft.Icons.DARK_MODE, ft.Colors.PINK_400),
        ]

        accordion_items = []
        for idx, item in enumerate(FAQ_ITEMS):
            icon_name, tint_fg = style_palette[idx % len(style_palette)]
            category = self._detect_category(item.get("question", ""), item.get("answer", ""))
            if is_dark_theme:
                card_bg = self.CATEGORY_COLORS_DARK.get(category, ft.Colors.GREY_900)
                tint_bg = ft.Colors.with_opacity(0.22, ft.Colors.WHITE)
            else:
                card_bg = ft.Colors.SURFACE
                tint_bg = ft.Colors.with_opacity(0.15, tint_fg)

            accordion_items.append(
                ft.Container(
                    border=ft.border.all(1, card_border),
                    border_radius=16,
                    bgcolor=card_bg,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=12,
                        color=ft.Colors.with_opacity(0.18, ft.Colors.BLACK),
                        offset=ft.Offset(0, 3),
                    ),
                    content=ft.ExpansionTile(
                        title=ft.Row(
                            controls=[
                                ft.Container(
                                    width=34,
                                    height=34,
                                    border_radius=17,
                                    bgcolor=tint_bg,
                                    alignment=ft.alignment.center,
                                    content=ft.Icon(icon_name, size=18, color=tint_fg),
                                ),
                                ft.Text(
                                    item.get("question", ""),
                                    weight=ft.FontWeight.W_600,
                                    size=15,
                                ),
                            ],
                            spacing=10,
                        ),
                        controls=[
                            ft.Container(
                                padding=ft.padding.only(left=44, right=12, bottom=12, top=2),
                                content=ft.Container(
                                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                                    border_radius=8,
                                    bgcolor=answer_bg,
                                    border=ft.border.only(
                                        left=ft.border.BorderSide(3, ft.Colors.with_opacity(0.6, tint_fg))
                                    ),
                                    content=ft.Text(
                                        item.get("answer", ""),
                                        size=14,
                                        color=answer_text_color,
                                        text_align=ft.TextAlign.LEFT,
                                    ),
                                ),
                            )
                        ],
                    ),
                )
            )

        self.content = ft.Column(
            width=920,
            controls=[
                ft.Container(
                    padding=20,
                    border_radius=18,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.center_left,
                        end=ft.alignment.center_right,
                        colors=[
                            ft.Colors.with_opacity(0.12, ft.Colors.BLUE_400),
                            ft.Colors.with_opacity(0.12, ft.Colors.CYAN_400),
                        ],
                    ),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.4, ft.Colors.BLUE_400)),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=48,
                                height=48,
                                border_radius=24,
                                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_400),
                                alignment=ft.alignment.center,
                                content=ft.Icon(ft.Icons.HELP_CENTER, color=ft.Colors.BLUE_300, size=28),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("FAQ", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
                                    ft.Text(
                                        "Click any question to expand details",
                                        size=14,
                                        color=ft.Colors.BLUE_300,
                                    ),
                                ],
                                spacing=2,
                            ),
                        ],
                        spacing=14,
                    ),
                ),
                ft.Divider(color=ft.Colors.GREY_700),
                *accordion_items,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
        )

    def _detect_category(self, question: str, answer: str) -> str:
        text = f"{question} {answer}".lower()
        if any(token in text for token in ["diet", "meal", "food", "nutrition"]):
            return "Diet"
        if any(token in text for token in ["calendar", "event", "schedule", "view"]):
            return "Calendar"
        if any(token in text for token in ["grocery", "store", "product", "cart", "shop"]):
            return "Grocery"
        return "General"
