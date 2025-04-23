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
    # Configurações iniciais da página
    page.title = 'ToDoList'
    page.window.center()  # Centraliza a janela na tela
    page.window.height = 800  # Define a altura da janela
    page.window.width = 450  # Define a largura da janela
    page.padding = 20  # Define o preenchimento (margem interna) da página
    page.scroll = 'adaptive'  # Define o comportamento do scroll
    page.bgcolor = '#1E201E'  # Define a cor de fundo da página
    page.window.icon = "assets/icon.png"  # Define o ícone da janela

    def construir_home():
        # Função para construir a tela inicial com as tarefas pendentes
        tarefas = crud.listar_tarefa(SessionLocal())  # Pega todas as tarefas do banco de dados
        tarefas_pendentes = [t for t in tarefas if not t.SITUACAO]  # Filtra as tarefas pendentes (SITUACAO == False)

        tarefa_containers = []  # Lista que vai armazenar os containers para as tarefas

        # Título da seção de tarefas pendentes
        tarefa_containers.append(
            ft.Text("⏳ Tarefas Pendentes", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
        )
        tarefa_containers.append(
            ft.Divider(thickness=1, color=ft.colors.GREY_700),  # Adiciona uma linha divisória
        )

        # Para cada tarefa pendente, cria um container com um checkbox e a descrição da tarefa
        for tarefa in tarefas_pendentes:
            checkbox = ft.Checkbox(
                value=False,  # O checkbox começa desmarcado
                on_change=lambda e, t=tarefa: concluir_tarefa(t)  # Chama a função concluir_tarefa ao alterar o checkbox
            )

            container = ft.Container(
                content=ft.Row([  # Layout horizontal com a descrição da tarefa e o checkbox
                    ft.Text(tarefa.DESCRICAO, size=16),  # Descrição da tarefa
                    checkbox  # Checkbox para concluir a tarefa
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),  # Alinha os itens de maneira espaçada
                padding=15,  # Define o preenchimento (margem interna) do container
                margin=ft.margin.only(bottom=10),  # Define a margem inferior do container
                border_radius=8,  # Define o raio de borda do container (bordas arredondadas)
                bgcolor="#3C3D37"  # Define a cor de fundo do container
            )

            tarefa_containers.append(container)  # Adiciona o container da tarefa à lista de containers

        # Se não houver tarefas pendentes, exibe uma mensagem informando isso
        if len(tarefa_containers) == 2:  # Só tem o título e a linha divisória
            tarefa_containers.append(
                ft.Text("👌 Nenhuma tarefa pendente!", size=16, weight=ft.FontWeight.NORMAL)
            )

        # Retorna a coluna contendo todos os containers de tarefas
        return ft.Column(tarefa_containers, scroll=ft.ScrollMode.AUTO)

    
    def concluir_tarefa(tarefa):
        # Função chamada ao concluir uma tarefa (marcando o checkbox)
        crud.editar_tarefa(SessionLocal(), tarefa.ID, tarefa.DESCRICAO, True, tarefa.CATEGORIA, tarefa.DATA_TAREFA)  # Atualiza a tarefa no banco
        page.controls.clear()  # Limpa os controles da página
        page.add(construir_home())  # Reconstroi a tela inicial
        page.open(ft.SnackBar(ft.Text("✅ Tarefa concluída!", color=ft.Colors.WHITE), bgcolor='#3C3D37'))  # Exibe um snack bar de sucesso
        page.update()  # Atualiza a página

    def atualizar_interface():
        # Função para atualizar a interface, recarregando as tarefas
        page.controls.clear()  # Limpa os controles da página
        page.add(construir_home())  # Reconstroi a tela inicial
        page.update()  # Atualiza a página
    
    def adicionar(e):
        # Função para adicionar uma nova tarefa
        nova_tarefa_modal = ft.TextField(label='Nome da tarefa', width=200, max_length=24)  # Campo de texto para o nome da tarefa
        page.scroll = 'adaptive'  # Ativa o scroll adaptável

        # Definindo as categorias possíveis para a tarefa
        categories = [
            {"name": "Pessoal", "icon_name": ft.Icons.EMOJI_EMOTIONS},
            {"name": "Compras", "icon_name": ft.Icons.SHOPPING_CART_OUTLINED},
            {"name": "Trabalho", "icon_name": ft.Icons.COMPUTER},
            {"name": "Lista de Desejos", "icon_name": ft.Icons.FAVORITE},
        ]

        # Função para retornar as opções do dropdown com as categorias
        def get_options():
            return [ft.DropdownOption(key=c["name"], leading_icon=c["icon_name"]) for c in categories]

        dd = ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,  # Define a borda do campo
            enable_filter=True,  # Permite filtrar as opções
            editable=True,  # Permite editar a opção
            leading_icon=ft.Icons.SEARCH,  # Ícone à esquerda do dropdown
            label="Categoria",  # Rótulo do campo
            options=get_options(),  # Opções de categorias
        )

        # Label para mostrar a data selecionada
        label_data = ft.Text(value="Data não selecionada", size=16)

        # Função chamada quando a data é alterada
        def handle_change(e):
            data_selecionada = e.control.value  # Obtém a data selecionada
            label_data.value = f"📅 Data selecionada: {data_selecionada.strftime('%d-%m-%Y')}"  # Atualiza o label
            page.update()  # Atualiza a página

        # Campo para escolher a data
        dp_data = ft.DatePicker(on_change=handle_change)

        # Botão para abrir o seletor de data
        dp = ft.ElevatedButton(
            "Escolher data",
            icon=ft.Icons.CALENDAR_MONTH,  # Ícone do calendário
            on_click=lambda e: page.open(dp_data),  # Abre o seletor de data
        )

        # Função para salvar a edição ou criação da tarefa
        def salvar_edicao(e):
            tarefa_nome = nova_tarefa_modal.value  # Obtém o nome da tarefa
            categoria_selecionada = dd.value  # Obtém a categoria selecionada
            data_selecionada = dp_data.value  # Obtém a data selecionada

            # Validação de dados
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
                tarefa_criada = crud.cadastrar_tarefa(SessionLocal(), tarefa_nome, False, categoria_selecionada, data_selecionada)  # Cria a tarefa no banco
                tarefa = ft.Row([])  # Placeholder para a nova tarefa
                lista_tarefas.append(tarefa)  # Adiciona a tarefa à lista de tarefas

                page.close(modal_tarefa)  # Fecha o modal
                page.open(ft.SnackBar(ft.Text("✅ Tarefa adicionada com sucesso!", color=ft.Colors.WHITE), bgcolor='#3C3D37'))  # Exibe o snack bar de sucesso
                
                if page.route == "/":
                    page.controls.clear()  # Limpa a página
                    page.add(construir_home())  # Recarrega as tarefas
                    page.update()

                nova_tarefa_modal.value = ''  # Limpa o campo de texto
                nova_tarefa_modal.update()  # Atualiza o campo de texto
                page.update()  # Atualiza a página

        # Modal para adicionar uma nova tarefa
        modal_tarefa = ft.AlertDialog(
            modal=True,
            bgcolor= '#1E201E',  # Cor de fundo do modal
            content=ft.Column([  # Conteúdo do modal
                ft.Row([
                    ft.Text("Adicionar Tarefa", style="headlineSmall"),
                    ft.IconButton(icon=ft.icons.CLOSE, on_click=lambda e: page.close(modal_tarefa)),  # Botão de fechar
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                nova_tarefa_modal,  # Campo de nome da tarefa
                dd,  # Dropdown para selecionar a categoria
                dp,  # Botão de escolha de data
                label_data  # Label para exibir a data
            ], spacing=30),
            actions=[  # Ações do modal
                ft.TextButton("Adicionar", on_click=salvar_edicao,)  # Botão para salvar a tarefa
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Abre o modal para adicionar uma tarefa
        page.open(modal_tarefa)

    def listar_tarefa(e):
        # Função para listar as rotas quando a navegação mudar
        def rotas(route):
            page.controls.clear()  # Limpa os controles da página
            tela = None

            if route == '/':
                tela = Page1(page)  # Carrega a tela principal de tarefas
                page.floating_action_button.visible = False  # Esconde o botão flutuante
                page.appbar.actions[0].visible = False  # Esconde o botão de ação na AppBar

            elif route == '/interface':
                tela = main(page)  # Carrega a tela de interface inicial
                page.floating_action_button.visible = True  # Exibe o botão flutuante
                page.appbar.actions[0].visible = True  # Exibe o botão de ação na AppBar
            else:
                print(f"Rota desconhecida: {route}")  # Caso a rota não seja reconhecida

            if tela:
                page.add(tela.construir())  # Adiciona o conteúdo da tela na página

        # Função chamada ao mudar de rota
        page.on_route_change = lambda e: rotas(e.route)

        # Ações baseadas no item selecionado na navegação
        if e.control.selected_index == 0:
            page.go('/interface')  # Vai para a interface inicial
        elif e.control.selected_index == 1:
            page.go('/')  # Vai para a página de tarefas
    
    btn_att = ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip="Atualizar",
        on_click=lambda e: atualizar_interface()  # Chama a função para atualizar a interface
    )

    # AppBar com o título e ícones de ações
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.CHECK_CIRCLE_SHARP),
        leading_width=40,
        title=ft.Text("To-Do List"),
        center_title=False,
        bgcolor='#3C3D37',  # Cor de fundo da AppBar
        actions=[  # Ações na AppBar (botões)
            ft.IconButton(
                icon=ft.Icons.REFRESH,  # Ícone de refresh
                tooltip="Atualizar",  # Tooltip ao passar o mouse
                on_click=lambda e: atualizar_interface()  # Chama a função de atualizar a interface
            )
        ]
    )

    # Barra de navegação inferior
    page.navigation_bar = ft.NavigationBar(
        destinations=[  # Destinos de navegação
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),  # Home
            ft.NavigationBarDestination(icon=ft.Icons.LIBRARY_BOOKS, label="Tarefas"),  # Tarefas
        ],
        on_change=listar_tarefa  # Chama a função listar_tarefa quando a navegação muda
    )

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD_ROUNDED,
        bgcolor='#697565',
        tooltip="Adicionar tarefa",
        on_click=adicionar,  # Ao clicar, abre o modal para adicionar uma nova tarefa
        width=70,  # Define a largura do botão flutuante
        height=70,  # Define a altura do botão flutuante
    )

    # Quando a aplicação é carregada, exibe a tela inicial
    page.add(construir_home())  # Adiciona a tela inicial com as tarefas pendentes
    page.update()  # Atualiza a página



