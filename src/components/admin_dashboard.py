from datetime import datetime

import flet as ft

from data.store import store


class AdminDashboard(ft.Column):
    """Admin view for ratings and bug reports."""

    def __init__(self, page: ft.Page, user_info: dict):
        super().__init__()
        self.page_ref = page
        self.user_info = user_info
        self.expand = True
        self.spacing = 20
        self.scroll = ft.ScrollMode.AUTO

        if not store.is_admin_account(user_info["id"]):
            self.controls = [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.BLOCK, size=80, color=ft.Colors.RED),
                            ft.Text(
                                "Access Denied",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.RED,
                            ),
                            ft.Text(
                                "You don't have admin privileges",
                                size=14,
                                color=ft.Colors.GREY,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            ]
            return

        self.tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tab_changed,
            tabs=[
                ft.Tab(text="Overview", icon=ft.Icons.DASHBOARD),
                ft.Tab(text="Ratings", icon=ft.Icons.STAR),
                ft.Tab(text="Bug Reports", icon=ft.Icons.BUG_REPORT),
            ],
        )
        self.content_container = ft.Container(expand=True)
        self.controls = [
            ft.Row(
                [
                    ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=32, color=ft.Colors.BLUE_700),
                    ft.Text("Admin Dashboard", size=28, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            ft.Divider(),
            self.tabs,
            self.content_container,
        ]
        self.show_overview()

    def tab_changed(self, e):
        if self.tabs.selected_index == 0:
            self.show_overview()
        elif self.tabs.selected_index == 1:
            self.show_ratings()
        elif self.tabs.selected_index == 2:
            self.show_bug_reports()

    def show_overview(self):
        all_ratings = store.get_all_ratings()
        all_reports = store.get_all_bug_reports()

        total_ratings = len(all_ratings)
        avg_rating = (
            sum(r.get("rating", 0) for r in all_ratings) / total_ratings if total_ratings > 0 else 0
        )
        new_reports = len([r for r in all_reports if r.get("status") == "new"])
        resolved_reports = len([r for r in all_reports if r.get("status") == "resolved"])

        star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in all_ratings:
            value = int(rating.get("rating", 0))
            if value in star_counts:
                star_counts[value] += 1

        self.content_container.content = ft.Column(
            [
                ft.Row(
                    [
                        self.create_stat_card(
                            "Total Ratings", str(total_ratings), ft.Icons.STAR, ft.Colors.AMBER_600
                        ),
                        self.create_stat_card(
                            "Average Rating",
                            f"{avg_rating:.1f}/5",
                            ft.Icons.TRENDING_UP,
                            ft.Colors.GREEN_600,
                        ),
                        self.create_stat_card(
                            "New Reports", str(new_reports), ft.Icons.BUG_REPORT, ft.Colors.RED_600
                        ),
                        self.create_stat_card(
                            "Resolved",
                            str(resolved_reports),
                            ft.Icons.CHECK_CIRCLE,
                            ft.Colors.BLUE_600,
                        ),
                    ],
                    spacing=15,
                    wrap=True,
                ),
                ft.Container(height=20),
                ft.Text("Rating Distribution", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                *[
                    self.create_rating_bar(star, count, total_ratings)
                    for star, count in sorted(star_counts.items(), reverse=True)
                ],
            ],
            spacing=10,
        )
        self.safe_update(self.content_container)

    def create_stat_card(self, title: str, value: str, icon, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, color=color, size=24),
                            ft.Text(title, size=14, color=ft.Colors.GREY_600),
                        ],
                        spacing=10,
                    ),
                    ft.Container(height=5),
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD),
                ]
            ),
            width=200,
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREY_400),
        )

    def create_rating_bar(self, stars: int, count: int, total: int):
        percentage = (count / total * 100) if total > 0 else 0
        return ft.Row(
            [
                ft.Text(f"{stars}*", size=14, width=50),
                ft.Container(
                    content=ft.ProgressBar(
                        value=percentage / 100,
                        width=300,
                        color=ft.Colors.AMBER_600,
                        bgcolor=ft.Colors.GREY_200,
                    )
                ),
                ft.Text(f"{count} ({percentage:.1f}%)", size=14, width=100),
            ],
            spacing=10,
        )

    def show_ratings(self):
        ratings = store.get_all_ratings(limit=50)
        if not ratings:
            self.content_container.content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.INBOX, size=80, color=ft.Colors.GREY),
                        ft.Text("No ratings yet", size=18, color=ft.Colors.GREY),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        else:
            cards = [self.create_rating_card(r) for r in ratings]
            self.content_container.content = ft.Column(cards, spacing=10, scroll=ft.ScrollMode.AUTO)
        self.safe_update(self.content_container)

    def create_rating_card(self, rating: dict):
        """Create a rating card with details action."""
        try:
            date_obj = datetime.fromisoformat(rating["created_at"])
            date_str = date_obj.strftime("%b %d, %Y at %H:%M")
        except Exception:
            date_str = str(rating.get("created_at", ""))

        stars_row = self.build_star_row(rating.get("rating", 0), 20)
        comment = rating.get("comment", "") or ""
        comment_preview = comment[:100] + ("..." if len(comment) > 100 else "")
        if not comment_preview:
            comment_preview = "No comment"

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            stars_row,
                            ft.Container(expand=True),
                            ft.Text(date_str, size=12, color=ft.Colors.GREY_600),
                        ]
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        comment_preview,
                        size=14,
                        color=ft.Colors.GREY_800 if comment else ft.Colors.GREY_400,
                    ),
                    ft.Container(height=5),
                    ft.TextButton(
                        "View Details",
                        icon=ft.Icons.VISIBILITY,
                        on_click=lambda e, r=rating: self.view_rating_details(r),
                    ),
                ]
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREY_400),
        )

    def show_bug_reports(self):
        reports = store.get_all_bug_reports(limit=50)
        if not reports:
            self.content_container.content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.INBOX, size=80, color=ft.Colors.GREY),
                        ft.Text("No bug reports yet", size=18, color=ft.Colors.GREY),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        else:
            cards = [self.create_bug_card(r) for r in reports]
            self.content_container.content = ft.Column(cards, spacing=10, scroll=ft.ScrollMode.AUTO)
        self.safe_update(self.content_container)

    def create_bug_card(self, report: dict):
        try:
            date_obj = datetime.fromisoformat(report["created_at"])
            date_str = date_obj.strftime("%b %d, %Y at %H:%M")
        except Exception:
            date_str = str(report.get("created_at", ""))

        status_colors = {
            "new": ft.Colors.BLUE_600,
            "in_progress": ft.Colors.ORANGE_600,
            "resolved": ft.Colors.GREEN_600,
            "closed": ft.Colors.GREY_600,
        }
        status = report.get("status", "new")
        status_color = status_colors.get(status, ft.Colors.GREY)
        bug_label = report.get("bug_type", "other")

        actions = [
            ft.TextButton(
                "View Details",
                icon=ft.Icons.VISIBILITY,
                on_click=lambda e, r=report: self.view_bug_details(r),
            )
        ]
        if status != "resolved":
            actions.append(
                ft.TextButton(
                    "Mark Resolved",
                    icon=ft.Icons.CHECK,
                    on_click=lambda e, r=report: self.mark_resolved(r),
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(
                                    status.upper(),
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4,
                            ),
                            ft.Text(bug_label, size=14, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Text(date_str, size=12, color=ft.Colors.GREY_600),
                        ]
                    ),
                    ft.Divider(height=1),
                    ft.Text(
                        report.get("description", ""),
                        size=14,
                        color=ft.Colors.GREY_800,
                        max_lines=3,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Row(actions, spacing=5),
                ]
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREY_400),
        )

    def view_bug_details(self, report: dict):
        """Show bug details in modal with close and resolve actions."""
        try:
            date_obj = datetime.fromisoformat(report["created_at"])
            date_str = date_obj.strftime("%B %d, %Y at %H:%M")
        except Exception:
            date_str = str(report.get("created_at", ""))

        bug_type_labels = {
            "lag": "App is lagging / slow",
            "crash": "App crashed / froze",
            "feature_not_working": "Feature not working properly",
            "visual_bug": "Visual glitch / UI issue",
            "data_loss": "Lost data / events",
            "login_issue": "Can't login / register",
            "other": "Other issue",
        }
        bug_label = bug_type_labels.get(report.get("bug_type", "other"), report.get("bug_type", "other"))

        actions = [ft.TextButton("Close", on_click=lambda e: self.page_ref.close(details_dialog))]
        if report.get("status") != "resolved":
            actions.append(
                ft.ElevatedButton(
                    "Mark as Resolved",
                    icon=ft.Icons.CHECK,
                    on_click=lambda e: self.mark_resolved_from_dialog(report, details_dialog),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600),
                )
            )

        details_dialog = ft.AlertDialog(
            modal=False,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.BUG_REPORT, color=ft.Colors.RED_600, size=24),
                    ft.Text("Bug Report Details", size=18, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Type:", size=14, weight=ft.FontWeight.BOLD, width=100),
                                ft.Text(bug_label, size=14),
                            ]
                        ),
                        ft.Divider(height=1),
                        ft.Row(
                            [
                                ft.Text("Status:", size=14, weight=ft.FontWeight.BOLD, width=100),
                                ft.Container(
                                    content=ft.Text(
                                        str(report.get("status", "new")).upper(),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                    bgcolor={
                                        "new": ft.Colors.BLUE_600,
                                        "in_progress": ft.Colors.ORANGE_600,
                                        "resolved": ft.Colors.GREEN_600,
                                        "closed": ft.Colors.GREY_600,
                                    }.get(report.get("status", "new"), ft.Colors.GREY),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=4,
                                ),
                            ]
                        ),
                        ft.Divider(height=1),
                        ft.Row(
                            [
                                ft.Text("Reported:", size=14, weight=ft.FontWeight.BOLD, width=100),
                                ft.Text(date_str, size=14, color=ft.Colors.GREY_700),
                            ]
                        ),
                        ft.Divider(height=1),
                        ft.Text("Description:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(height=5),
                        ft.Container(
                            content=ft.Text(report.get("description", ""), size=13, color=ft.Colors.GREY_800),
                            bgcolor=ft.Colors.GREY_100,
                            padding=10,
                            border_radius=5,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                        ),
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=500,
                height=400,
            ),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page_ref.open(details_dialog)

    def mark_resolved(self, report: dict):
        if store.update_report_status(report.get("id", ""), "resolved"):
            self.show_bug_reports()

    def mark_resolved_from_dialog(self, report: dict, dialog: ft.AlertDialog):
        """Mark report resolved and close details dialog."""
        if store.update_report_status(report.get("id", ""), "resolved"):
            self.page_ref.close(dialog)
            self.show_bug_reports()

    def view_rating_details(self, rating: dict):
        """Show rating details in modal window."""
        try:
            date_obj = datetime.fromisoformat(rating["created_at"])
            date_str = date_obj.strftime("%B %d, %Y at %H:%M")
        except Exception:
            date_str = str(rating.get("created_at", ""))

        details_dialog = ft.AlertDialog(
            modal=False,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER_600, size=24),
                    ft.Text("Rating Details", size=18, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Rating:", size=14, weight=ft.FontWeight.BOLD, width=100),
                                self.build_star_row(rating.get("rating", 0), 24),
                                ft.Text(f"{rating.get('rating', 0)}/5", size=16, weight=ft.FontWeight.BOLD),
                            ]
                        ),
                        ft.Divider(height=1),
                        ft.Row(
                            [
                                ft.Text("Date:", size=14, weight=ft.FontWeight.BOLD, width=100),
                                ft.Text(date_str, size=14, color=ft.Colors.GREY_700),
                            ]
                        ),
                        ft.Divider(height=1),
                        ft.Text("Comment:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(height=5),
                        ft.Container(
                            content=ft.Text(
                                rating.get("comment", "No comment provided"),
                                size=13,
                                color=ft.Colors.GREY_800 if rating.get("comment") else ft.Colors.GREY_400,
                                italic=not bool(rating.get("comment")),
                            ),
                            bgcolor=ft.Colors.GREY_100,
                            padding=10,
                            border_radius=5,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                        ),
                    ],
                    spacing=10,
                ),
                width=450,
                height=300,
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self.page_ref.close(details_dialog))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page_ref.open(details_dialog)

    @staticmethod
    def build_star_row(rating_value: float, size: int):
        """Build full/half/empty stars row for decimal ratings."""
        controls = []
        for i in range(1, 6):
            if rating_value >= i:
                icon = ft.Icons.STAR
            elif rating_value >= i - 0.5:
                icon = ft.Icons.STAR_HALF
            else:
                icon = ft.Icons.STAR_OUTLINE
            controls.append(ft.Icon(icon, color=ft.Colors.AMBER_600, size=size))
        return ft.Row(controls, spacing=2)

    @staticmethod
    def safe_update(control):
        try:
            control.update()
        except AssertionError:
            # View may be prepared before being attached to page.
            pass
