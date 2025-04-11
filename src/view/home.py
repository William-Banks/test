import sys
import os

# Adiciona o diretório raiz ao sys.path para importar corretamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import flet as ft  # Importando a biblioteca flet para criar a interface gráfica
from src.service import crud  # Importando as funções de CRUD do arquivo crud.py
from src.model.db import SessionLocal  # Importando a sessão do banco de dados
from view.tarefa_view import Page1


# Lista global para armazenar as tarefas
lista_tarefas = []

def main(page=ft.Page):  # Função principal que é chamada para renderizar a página
    page.title = 'ToDoList'  # Definindo o título da página no navegador
    page.window.center()  # Centraliza a janela
    page.window.height = 800
    page.window.width = 450
    page.padding = 5
    page.scroll = 'adaptive'  # Permite rolagem adaptável, dependendo do conteúdo
    page.bgcolor = '#1E201E'  # Define a cor de fundo da página

    def alterar_tema(e):  
        # Função para alternar entre o tema claro e o tema escuro
        if page.bgcolor == '#F6F0F0':
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor = '#1E201E'
            nova_tarefa.bgcolor = '#3C3D37'
            page.floating_action_button.bgcolor = '#697565'
            page.appbar.bgcolor = '#3C3D37'
            btn_tema.icon = ft.icons.WB_SUNNY_OUTLINED
            btn_tema.tooltip = 'Alterar para tema claro'
            
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.bgcolor = '#F6F0F0'
            nova_tarefa.bgcolor = '#D5C7A3'
            page.floating_action_button.bgcolor = '#F2E2B1'
            page.appbar.bgcolor = '#D5C7A3'
            btn_tema.icon = ft.icons.NIGHTS_STAY_OUTLINED
            btn_tema.tooltip = 'Alterar para tema escuro'
            
        page.update()  # Atualiza a página com as novas configurações de tema

    btn_tema = ft.IconButton(icon = ft.icons.WB_SUNNY_OUTLINED, tooltip = 'Alterar o tema', on_click = alterar_tema)

    def check_item_clicked(e):
        # Função que altera o estado do checkbox
        e.control.checked = not e.control.checked
        page.update()

    def mudar_rota(e):  # Função chamada quando há mudança na seleção da barra de navegação
        if e.control.selected_index == 0:
            page.go('/tela')

    def listar_tarefa(e):
        def rotas(route):
            page.controls.clear()  # Limpa os controles da página antes de adicionar novos
            tela = None

            if route == '/':
                tela = Page1(page)  # Volta para a página inicial com a lista de tarefas
                page.floating_action_button.visible = False
                page.appbar.actions[1].visible = False
                page.appbar.vsible = False

            elif route == '/interface':
                tela = main(page)  # Aqui ele vai criar a tela principal novamente
                page.floating_action_button.visible = True
                page.appbar.actions[1].visible = True
                page.appbar.vsible = True
            else:
                print(f"Rota desconhecida: {route}")

            if tela:
                page.add(tela.construir())  # Adiciona a tela ao layout

        page.on_route_change = lambda e: rotas(e.route)  # Registra a mudança de rota
        page.go('/')  # Navega para a rota inicial


    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.CHECK_CIRCLE_SHARP),
        leading_width=40,
        title=ft.Text("To-Do List"),
        center_title=False,
        bgcolor = '#3C3D37',  # Cor do fundo da appbar
        actions=[
            btn_tema,  # Ícone de alternância de tema
            ft.IconButton(icon=ft.Icons.MENU_BOOK, tooltip="Listar tarefas", on_click=listar_tarefa),  # Ícone de listagem de tarefas
        ],
    )

    def adicionar(e):  # Função para abrir o modal de adicionar uma nova tarefa
        nova_tarefa_modal = ft.TextField(label='Nome da tarefa', width=200)  # Campo de entrada dentro do modal

        categories = [
            {"name": "Pessoal", "icon_name": ft.Icons.EMOJI_EMOTIONS},
            {"name": "Compras", "icon_name": ft.Icons.SHOPPING_CART_OUTLINED},
            {"name": "Trabalho", "icon_name": ft.Icons.COMPUTER},
            {"name": "Lista de Desejos", "icon_name": ft.Icons.FAVORITE},
        ]

        def get_options():
            options = []
            for category in categories:
                options.append(
                    ft.DropdownOption(key=category["name"], leading_icon=category["icon_name"])
                )
            return options

        dd = ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,
            enable_filter=True,
            editable=True,
            leading_icon=ft.Icons.SEARCH,
            label="Categoria",
            options=get_options(),
        )

        # Adicionando um campo para exibir a data selecionada
        label_data = ft.Text(value="Data não selecionada", size=16)

        def handle_change(e):
            # Atualiza a label com a data selecionada
            data_selecionada = e.control.value
            label_data.value = f"Data selecionada: {data_selecionada.strftime('%d-%m-%Y')}"
            page.update()

        dp_data = ft.DatePicker(on_change=handle_change)

        dp = ft.ElevatedButton(
            "Escolher data",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: page.open(dp_data),
        )

        def salvar_edicao(e):
            tarefa_nome = nova_tarefa_modal.value
            categoria_selecionada = dd.value  # Captura o valor selecionado no dropdown
            data_selecionada = dp_data.value

            if not tarefa_nome:  # Verifica se o campo de texto está vazio
                nova_tarefa_modal.error_text = 'Digite algo para adicionar'
                page.update()
            elif not categoria_selecionada:  # Verifica se uma categoria foi selecionada
                nova_tarefa_modal.error_text = 'Selecione uma categoria'
                page.update()
            else:
                nova_tarefa_modal.error_text = None  # Limpa a mensagem de erro

                # Criando a tarefa no banco de dados com a categoria
                tarefa_criada = crud.cadastrar_tarefa(SessionLocal(), tarefa_nome, False, categoria_selecionada, data_selecionada)

                # Criando um container de linha (Row) para a tarefa
                tarefa = ft.Row([])

                page.add(ft.Text('Tarefa adicionada com sucesso!', width=50))  # Adiciona a tarefa na página
                lista_tarefas.append(tarefa)  # Adiciona a tarefa na lista global de tarefas

                # Fechar o modal após adicionar
                page.close(modal_tarefa)

                nova_tarefa_modal.value = ''  # Limpa o campo de entrada
                nova_tarefa_modal.update()
                page.update()  # Atualiza a página

        # Modal para adicionar nova tarefa
        modal_tarefa = ft.AlertDialog(
            modal=True,
            title=ft.Text("Adicionar Tarefa"),
            content=ft.Column([nova_tarefa_modal, dd, dp, label_data]),  # Adiciona a label da data
            actions=[
                ft.TextButton("Adicionar", on_click=salvar_edicao),  # Adiciona a tarefa
                ft.TextButton("Cancelar", on_click=lambda e: page.close(modal_tarefa)),  # Fecha o modal sem adicionar
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Exibe o modal de adicionar tarefa
        page.open(modal_tarefa)





    def atualizar_situacao(task_id, situacao):  # Função para atualizar a situação da tarefa no banco de dados
        tarefa_atual = crud.listar_tarefa_id(SessionLocal(), task_id)  # Obtém a tarefa pelo ID
        if tarefa_atual:
            descricao_tarefa = tarefa_atual.DESCRICAO  # Descrição da tarefa
            crud.editar_tarefa(SessionLocal(), task_id, descricao_tarefa, situacao)

    def editar_tarefa(tarefa, checkbox, btn_editar, botao_remover, tarefa_criada):  # Função para editar uma tarefa existente
        checkbox.visible = False
        btn_editar.visible = False
        botao_remover.visible = False
        page.update()

        # Criando o campo de edição com o valor atual da tarefa
        campo_edicao = ft.TextField(label='Editar tarefa', value=checkbox.label, width=200)

        # Criando o botão para salvar a edição
        def salvar_edicao(e):
            updated_task = crud.editar_tarefa(
                SessionLocal(), tarefa_criada.ID, campo_edicao.value, checkbox.value
            )

            if updated_task:
                checkbox.label = campo_edicao.value  # Atualiza o texto da tarefa
                checkbox.value = updated_task.SITUACAO  # Atualiza a situação da tarefa
                page.update()

            # Exibe novamente o checkbox e os botões de editar e remover
            checkbox.visible = True
            btn_editar.visible = True
            botao_remover.visible = True
            campo_edicao.visible = False
            btn_salvar.visible = False
            page.update()

        # Ícone de salvar edição
        btn_salvar = ft.IconButton(
            icon=ft.icons.SAVE_OUTLINED,
            tooltip='Salvar tarefa',
            on_click=salvar_edicao
        )

        tarefa.controls.append(campo_edicao)
        tarefa.controls.append(btn_salvar)
        page.update()

    def remover_tarefa(tarefa, tarefa_criada):  # Função para remover uma tarefa
        def confirmar_exclusao(e):
            crud.excluir_tarefa(SessionLocal(), tarefa_criada.ID)
            page.controls.remove(tarefa)  # Remove a tarefa da página
            lista_tarefas.remove(tarefa)  # Remove a tarefa da lista de tarefas
            page.update()
            page.close(dlg_modal)

        def cancelar_exclusao(e):
            page.close(dlg_modal)

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Por favor, confirme"),
            content=ft.Text("Você tem certeza que deseja excluir esta tarefa?"),
            actions=[
                ft.TextButton("Sim", on_click=confirmar_exclusao),
                ft.TextButton("Não", on_click=cancelar_exclusao),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.open(dlg_modal)
        dlg_modal.visible = True
        page.update()

    nova_tarefa = ft.TextField(label='Nome da tarefa', width=200)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD_ROUNDED, bgcolor = '#697565', tooltip="Adicionar tarefa", on_click=adicionar
    )

    page.add(ft.Column([  
        ft.Row([]),
    ]))

    page.update()

# Iniciando o app
ft.app(main)