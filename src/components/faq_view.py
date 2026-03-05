import flet as ft
from data.faq_data import FAQ_ITEMS


class FAQView(ft.Container):
    def __init__(self):
        super().__init__(expand=True, padding=20, alignment=ft.alignment.top_center)

        style_palette = [
            (ft.Icons.ADD_CIRCLE_OUTLINE, ft.Colors.BLUE_100, ft.Colors.BLUE_700),
            (ft.Icons.CALENDAR_MONTH, ft.Colors.INDIGO_100, ft.Colors.INDIGO_700),
            (ft.Icons.RESTAURANT_MENU, ft.Colors.ORANGE_100, ft.Colors.ORANGE_700),
            (ft.Icons.LANGUAGE, ft.Colors.GREEN_100, ft.Colors.GREEN_700),
            (ft.Icons.DARK_MODE, ft.Colors.PINK_100, ft.Colors.PINK_700),
        ]

        accordion_items = [
            ft.Container(
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=16,
                bgcolor=ft.Colors.SURFACE,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=12,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
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
                            ft.Text(question, weight=ft.FontWeight.W_600, size=16),
                        ],
                        spacing=10,
                    ),
                    controls=[
                        ft.Container(
                            margin=ft.margin.only(left=44, right=8, bottom=10),
                            padding=12,
                            border_radius=10,
                            bgcolor=ft.Colors.GREY_50,
                            content=ft.Text(answer, size=14, color=ft.Colors.BLACK87),
                        )
                    ],
                ),
            )
            for idx, item in enumerate(FAQ_ITEMS)
            for icon_name, tint_bg, tint_fg in [style_palette[idx % len(style_palette)]]
            for question, answer in [(item["question"], item["answer"])]
        ]

        self.content = ft.Column(
            width=920,
            controls=[
                ft.Container(
                    padding=20,
                    border_radius=18,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.center_left,
                        end=ft.alignment.center_right,
                        colors=[ft.Colors.BLUE_50, ft.Colors.CYAN_50],
                    ),
                    border=ft.border.all(1, ft.Colors.BLUE_100),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=48,
                                height=48,
                                border_radius=24,
                                bgcolor=ft.Colors.WHITE,
                                alignment=ft.alignment.center,
                                content=ft.Icon(ft.Icons.HELP_CENTER, color=ft.Colors.BLUE_700, size=28),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("FAQ", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                                    ft.Text(
                                        "Click any question to expand details",
                                        size=14,
                                        color=ft.Colors.BLUE_700,
                                    ),
                                ],
                                spacing=2,
                            ),
                        ],
                        spacing=14,
                    ),
                ),
                ft.Divider(),
                *accordion_items,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
        )
