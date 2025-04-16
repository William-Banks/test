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
    page.padding = 20
    page.scroll = 'adaptive'
    page.bgcolor = '#1E201E'

    def construir_home():
        tarefas = crud.listar_tarefa(SessionLocal())
        tarefas_pendentes = [t for t in tarefas if not t.SITUACAO]

        tarefa_containers = []

        # Título da seção
        tarefa_containers.append(
            ft.Text("⏳ Tarefas Pendentes", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
        )
        tarefa_containers.append(
            ft.Divider(thickness=1, color=ft.colors.GREY_700),
        )
        

        for tarefa in tarefas_pendentes:
            checkbox = ft.Checkbox(
                value=False,
                on_change=lambda e, t=tarefa: concluir_tarefa(t)
            )

            container = ft.Container(
                content=ft.Row([
                    ft.Text(tarefa.DESCRICAO, size=16),
                    checkbox
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=15,
                margin=ft.margin.only(bottom=10),
                border_radius=8,
                bgcolor="#3C3D37"
            )

            tarefa_containers.append(container)

        if len(tarefa_containers) == 2:  # Só tem o título
            tarefa_containers.append(
                ft.Text("👌 Nenhuma tarefa pendente!", size=16, weight=ft.FontWeight.NORMAL)
            )

        return ft.Column(tarefa_containers, scroll=ft.ScrollMode.AUTO)

    
    def concluir_tarefa(tarefa):
        crud.editar_tarefa(SessionLocal(), tarefa.ID, tarefa.DESCRICAO, True, tarefa.CATEGORIA, tarefa.DATA_TAREFA)
        page.controls.clear()
        page.add(construir_home())
        page.open(ft.SnackBar(ft.Text("✅ Tarefa concluída!", color=ft.Colors.WHITE), bgcolor='#3C3D37'))
        page.update()

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
                page.open(ft.SnackBar(ft.Text("✅ Tarefa adicionada com sucesso!", color=ft.Colors.WHITE), bgcolor='#3C3D37'))
                
                if page.route == "/":
                    page.controls.clear()
                    page.add(construir_home())
                    page.update()

                nova_tarefa_modal.value = ''
                nova_tarefa_modal.update()
                page.update()

        modal_tarefa = ft.AlertDialog(
            modal=True,
            content=ft.Column([
                ft.Row([
                    ft.Text("Adicionar Tarefa", style="headlineSmall"),
                    ft.IconButton(icon=ft.icons.CLOSE, on_click=lambda e: page.close(modal_tarefa)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                nova_tarefa_modal,
                dd,
                dp,
                label_data
            ], spacing=30),
            actions=[
                ft.TextButton("Adicionar", on_click=salvar_edicao)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.open(modal_tarefa)

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

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.LIBRARY_BOOKS, label="Tarefas"),
        ],
        on_change=listar_tarefa
    )

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD_ROUNDED,
        bgcolor='#697565',
        tooltip="Adicionar tarefa",
        on_click=adicionar,
        width=70,
        height=70,
    )

    # Quando a app abre, mostra a tela Home
    page.add(construir_home())
    page.update()


ft.app(main)
