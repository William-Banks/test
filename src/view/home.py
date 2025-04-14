import sys
import os

# Adiciona o diretório raiz ao sys.path para importar corretamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import flet as ft
from src.service import crud
from src.model.db import SessionLocal
from view.tarefa_view import Page1

# Lista global para armazenar tarefas
lista_tarefas = []

def main(page: ft.Page):
    page.title = 'ToDoList'
    page.window.center()
    page.window.height = 800
    page.window.width = 450
    page.padding = 5
    page.scroll = 'adaptive'
    page.bgcolor = '#1E201E'

    def listar_tarefa(e):
        def rotas(route):
            page.controls.clear()
            tela = None

            if route == '/':
                tela = Page1(page)
                page.floating_action_button.visible = False

            elif route == '/interface':
                tela = main(page)
                page.floating_action_button.visible = True
            else:
                print(f"Rota desconhecida: {route}")

            if tela:
                page.add(tela.construir())

        page.on_route_change = lambda e: rotas(e.route)
        if e.control.selected_index == 0:
            page.go('/interface')
        elif e.control.selected_index == 1:
            page.go('/')

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.CHECK_CIRCLE_SHARP),
        leading_width=40,
        title=ft.Text("To-Do List"),
        center_title=False,
        bgcolor='#3C3D37',
    )

    def adicionar(e):
        nova_tarefa_modal = ft.TextField(label='Nome da tarefa', width=200, max_length=30)
        page.scroll = 'adaptive'

        categories = [
            {"name": "Pessoal", "icon_name": ft.Icons.EMOJI_EMOTIONS},
            {"name": "Compras", "icon_name": ft.Icons.SHOPPING_CART_OUTLINED},
            {"name": "Trabalho", "icon_name": ft.Icons.COMPUTER},
            {"name": "Lista de Desejos", "icon_name": ft.Icons.FAVORITE},
        ]

        def get_options():
            return [ft.DropdownOption(key=c["name"], leading_icon=c["icon_name"]) for c in categories]

        dd = ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,
            enable_filter=True,
            editable=True,
            leading_icon=ft.Icons.SEARCH,
            label="Categoria",
            options=get_options(),
        )

        label_data = ft.Text(value="Data não selecionada", size=16)

        def handle_change(e):
            data_selecionada = e.control.value
            label_data.value = f"📅 Data selecionada: {data_selecionada.strftime('%d-%m-%Y')}"
            page.update()

        dp_data = ft.DatePicker(on_change=handle_change)

        dp = ft.ElevatedButton(
            "Escolher data",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.open(dp_data),
        )

        dlg_sucesso = ft.AlertDialog(
            modal=True,
            title=ft.Text("✅ Tarefa adicionada com sucesso!"),
            actions=[ft.TextButton("Fechar", on_click=lambda e: page.close(dlg_sucesso))],
        )

        def salvar_edicao(e):
            tarefa_nome = nova_tarefa_modal.value
            categoria_selecionada = dd.value
            data_selecionada = dp_data.value

            if not tarefa_nome:
                nova_tarefa_modal.error_text = 'Digite algo para adicionar'
                page.update()
            elif not categoria_selecionada:
                nova_tarefa_modal.error_text = 'Selecione uma categoria'
                page.update()
            elif not data_selecionada:
                label_data.value = 'Por favor, escolha uma data!'
                page.update()
            else:
                nova_tarefa_modal.error_text = None
                tarefa_criada = crud.cadastrar_tarefa(SessionLocal(), tarefa_nome, False, categoria_selecionada, data_selecionada)
                tarefa = ft.Row([])  # Placeholder
                lista_tarefas.append(tarefa)

                page.close(modal_tarefa)
                page.open(dlg_sucesso)

                nova_tarefa_modal.value = ''
                nova_tarefa_modal.update()
                page.update()

        modal_tarefa = ft.AlertDialog(
            modal=True,
            title=ft.Text("Adicionar Tarefa"),
            content=ft.Column([nova_tarefa_modal, dd, dp, label_data], spacing=30),
            actions=[
                ft.TextButton("Adicionar", on_click=salvar_edicao),
                ft.TextButton("Cancelar", on_click=lambda e: page.close(modal_tarefa)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.open(modal_tarefa)

    # Layout da tela inicial
    categorias_cards = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.EMOJI_EMOTIONS, size=30),
                    ft.Text("Pessoal", size=12),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=100,
                height=80,
                bgcolor="#3C3D37",
                border_radius=10,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.COMPUTER, size=30),
                    ft.Text("Trabalho", size=12),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=100,
                height=80,
                bgcolor="#3C3D37",
                border_radius=10,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=30),
                    ft.Text("Compras", size=12),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=100,
                height=80,
                bgcolor="#3C3D37",
                border_radius=10,
                alignment=ft.alignment.center,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        spacing=10,
    )

    resumo_texto = ft.Text(
        "📌 Clique no botão '+' abaixo para adicionar uma nova tarefa!",
        size=13,
        color="#CCCCCC",
        text_align="center"
    )

    mensagem_inicial = ft.Column(
        [
            ft.Text("Organize suas tarefas com facilidade.", size=18, weight="bold", color="#FFFFFF"),
            categorias_cards,
            ft.Divider(opacity=0),
            resumo_texto,
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.TASK, label="Tarefas"),
        ],
        on_change=listar_tarefa
    )

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD_ROUNDED, bgcolor='#697565', tooltip="Adicionar tarefa", on_click=adicionar, width=70, height=70,
    )

    page.add(mensagem_inicial)
    page.update()

ft.app(main)
