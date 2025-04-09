import flet as ft

def main(page: ft.Page):

    icons = [
        {"name": "Smile", "icon_name": ft.Icons.SENTIMENT_SATISFIED_OUTLINED},
        {"name": "Cloud", "icon_name": ft.Icons.CLOUD_OUTLINED},
        {"name": "Brush", "icon_name": ft.Icons.BRUSH_OUTLINED},
        {"name": "Heart", "icon_name": ft.Icons.FAVORITE},
    ]

    def get_options():
        options = []
        for icon in icons:
            options.append(
                ft.DropdownOption(key=icon["name"], leading_icon=icon["icon_name"])
            )
        return options

    dd = ft.Dropdown(
        border=ft.InputBorder.UNDERLINE,
        enable_filter=True,
        editable=True,
        leading_icon=ft.Icons.SEARCH,
        label="Icon",
        options=get_options(),
    )

    page.add(dd)

import datetime
import flet as ft


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def handle_change(e):
        page.add(ft.Text(f"Date changed: {e.control.value.strftime('%Y-%m-%d')}"))

    def handle_dismissal(e):
        page.add(ft.Text(f"DatePicker dismissed"))

    page.add(
        ft.ElevatedButton(
            "Pick date",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.open(
                ft.DatePicker(
                    first_date=datetime.datetime(year=2023, month=10, day=1),
                    last_date=datetime.datetime(year=2024, month=10, day=1),
                    on_change=handle_change,
                    on_dismiss=handle_dismissal,
                )
            ),
        )
    )
