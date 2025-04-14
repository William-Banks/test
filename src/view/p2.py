import flet as ft


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    dlg = ft.AlertDialog(
        title=ft.Text("Tarefa adcionada com sucesso!"),
    )

    

    page.add(
        ft.ElevatedButton("Open dialog", on_click=lambda e: page.open(dlg)),
    )

ft.app(main)