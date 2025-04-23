import flet as ft
from service import crud
from model.db import SessionLocal
from datetime import datetime

class Page1:
    # Inicializa a classe de página, onde `self.page` é a instância da página do Flet.
    # A variável `expanded_task_id` mantém o ID da tarefa expandida (para exibir detalhes).
    # `categoria_filter` será usado para aplicar filtros de categoria.
    def __init__(self, page: ft.Page):
        self.page = page
        self.expanded_task_id = None  # ID da tarefa atualmente expandida
        self.categoria_filter = None  # Filtro de categoria da tarefa (Pessoal, Compras, etc.)

    # Função principal que constrói a página exibindo tarefas filtradas com base na categoria.
    # Ela também permite expandir ou colapsar detalhes de uma tarefa específica.
    def construir(self, categoria_filter=None):
        tarefas = crud.listar_tarefa(SessionLocal())  # Busca todas as tarefas do banco de dados
        data_atual = datetime.now().date()  # Obtém a data atual para comparação com datas de vencimento

        # Filtragem das tarefas com base na categoria e/ou situação
        if categoria_filter and categoria_filter != "Todos":
            if categoria_filter == "Cumpridas":
                tarefas = [t for t in tarefas if t.SITUACAO]  # Filtra as tarefas que já foram concluídas
            elif categoria_filter == "Pendentes":
                tarefas = [t for t in tarefas if not t.SITUACAO]  # Filtra as tarefas pendentes
            elif categoria_filter == "Data Vencida":
                # Filtra as tarefas vencidas (não concluídas) com base na data de vencimento
                tarefas = [t for t in tarefas if t.DATA_TAREFA and t.DATA_TAREFA < data_atual and not t.SITUACAO]
            else:
                # Filtra as tarefas pela categoria especificada
                tarefas = [t for t in tarefas if t.CATEGORIA == categoria_filter]

        tarefa_containers = []  # Lista que armazenará os containers de cada tarefa na interface

        # Define as cores para os containers dependendo se a tarefa está expandida ou não
        cor_container_normal = "#3C3D37"  # Cor padrão do container
        cor_container_expandido = "#697565"  # Cor do container quando a tarefa estiver expandida

        for tarefa in tarefas:
            # Verifica se a tarefa está expandida, para exibir ou esconder os detalhes dela
            is_expanded = self.expanded_task_id == tarefa.ID
            cor_container = cor_container_expandido if is_expanded else cor_container_normal

            # A cor da bolinha à esquerda da descrição depende se a tarefa está vencida
            cor_bolinha = ft.colors.RED if tarefa.DATA_TAREFA and tarefa.DATA_TAREFA < data_atual and not tarefa.SITUACAO else ft.colors.GREEN

            # Cria o conteúdo principal da tarefa (descrição, status e categorias)
            conteudo = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row([
                            ft.Container(
                                content=ft.CircleAvatar(bgcolor=cor_bolinha, radius=8),  # Ícone de status (vermelho ou verde)
                                margin=ft.margin.only(right=8),
                            ),
                            ft.Text(tarefa.DESCRICAO, size=16, weight=ft.FontWeight.BOLD),  # Descrição da tarefa
                            ft.Text("✅ Concluída" if tarefa.SITUACAO else "⏳ Pendente"),  # Status da tarefa (concluída ou pendente)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.AnimatedSwitcher(
                            # Quando a tarefa estiver expandida, exibe mais detalhes
                            content=ft.Column(
                                controls=[
                                    ft.Text(f"📅 Data: {tarefa.DATA_TAREFA.strftime('%d/%m/%Y')}" if tarefa.DATA_TAREFA else "📅 Data: não definida"),  # Data da tarefa
                                    ft.Text(f"📂 Categoria: {tarefa.CATEGORIA}"),  # Categoria da tarefa (Trabalho, Pessoal, etc.)
                                ]
                            ) if is_expanded else ft.Container(),  # Exibe os detalhes apenas se a tarefa estiver expandida
                            duration=300  # Duração da animação para expandir/colapsar
                        )
                    ]
                ),
                padding=15,
                margin=ft.margin.only(bottom=8),
                border_radius=10,
                bgcolor=cor_container,  # Define a cor de fundo com base no estado de expansão
                ink=True,  # Efeito de clique
                on_click=lambda e, task_id=tarefa.ID: self.toggle_expand(task_id),  # Alterna entre expandir ou colapsar
            )

            # Menu contextual com ações para editar ou excluir a tarefa
            tarefa_contextual = ft.CupertinoContextMenu(
                content=conteudo,
                enable_haptic_feedback=True,  # Feedback tátil ao interagir
                actions=[
                    ft.CupertinoContextMenuAction(
                        text="Editar",  # Ação de edição
                        trailing_icon=ft.icons.EDIT,
                        on_click=lambda e, t=tarefa: self.editar_tarefa(t)  # Chama a função de editar tarefa
                    ),
                    ft.CupertinoContextMenuAction(
                        text="Excluir",  # Ação de exclusão
                        is_destructive_action=True,  # Marca a ação como destrutiva (exclusão)
                        trailing_icon=ft.icons.DELETE,
                        on_click=lambda e, t=tarefa: self.remover_tarefa_confirmar(t)  # Chama a função de confirmação de exclusão
                    ),
                ]
            )

            tarefa_containers.append(tarefa_contextual)  # Adiciona o menu contextual à lista

        # Cria o dropdown de filtro de categoria
        dd = self.get_dropdown()

        return ft.Column([
            ft.Row([dd], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),  # Adiciona o dropdown de filtro
            ft.Column(tarefa_containers, scroll=ft.ScrollMode.AUTO)  # Exibe a lista de tarefas com scroll
        ])

    # Função para alternar entre expandir ou colapsar a tarefa selecionada
    def toggle_expand(self, task_id):
        self.expanded_task_id = task_id if self.expanded_task_id != task_id else None
        self.page.controls.clear()  # Limpa os controles da página atual
        self.page.add(self.construir(self.categoria_filter))  # Reconstroi a página com o filtro atual
        self.page.update()

    # Função para criar o dropdown de filtros de categoria
    def get_dropdown(self):
        icons = [
            {"name": "Todos", "icon_name": ft.Icons.DENSITY_MEDIUM_OUTLINED},
            {"name": "Pessoal", "icon_name": ft.Icons.EMOJI_EMOTIONS},
            {"name": "Compras", "icon_name": ft.Icons.SHOPPING_CART_OUTLINED},
            {"name": "Trabalho", "icon_name": ft.Icons.COMPUTER},
            {"name": "Lista de Desejos", "icon_name": ft.Icons.FAVORITE},
            {"name": "Cumpridas", "icon_name": ft.Icons.CHECK_CIRCLE},
            {"name": "Pendentes", "icon_name": ft.Icons.LOCK_CLOCK_ROUNDED},
            {"name": "Data Vencida", "icon_name": ft.Icons.ERROR},
        ]

        # Gera as opções de filtro a partir dos ícones e nomes
        options = [ft.dropdown.Option(key=icon["name"], leading_icon=icon["icon_name"]) for icon in icons]

        return ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,
            enable_filter=True,  # Permite filtrar as opções do dropdown
            editable=True,  # Permite que o usuário digite no campo de filtro
            leading_icon=ft.Icons.SEARCH,  # Ícone de busca
            label="Filtrar tarefas",  # Rótulo do filtro
            options=options,  # Opções de filtro criadas acima
            on_change=lambda e: self.filtrar_tarefas(e.control.value)  # Aplica o filtro quando a opção for alterada
        )

    # Função que aplica o filtro de categoria selecionada e recarrega a página
    def filtrar_tarefas(self, categoria_selecionada):
        self.categoria_filter = categoria_selecionada  # Define o filtro de categoria
        self.expanded_task_id = None  # Reseta a tarefa expandida
        self.page.controls.clear()  # Limpa os controles da página
        self.page.add(self.construir(self.categoria_filter))  # Reconstroi a página com o filtro atualizado
        self.page.update()

    # Função que exibe a caixa de confirmação para excluir uma tarefa
    def remover_tarefa_confirmar(self, tarefa):
        dlg_confirmar = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmação de Exclusão"),
            content=ft.Text(f"Tem certeza que deseja excluir a tarefa: {tarefa.DESCRICAO}?"),
            actions=[
                ft.TextButton("Sim", on_click=lambda e: self.confirmar_exclusao(tarefa, dlg_confirmar)),  # Ação de confirmação
                ft.TextButton("Não", on_click=lambda e: self.page.close(dlg_confirmar)),  # Ação de cancelamento
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.open(dlg_confirmar)  # Exibe a caixa de diálogo
        dlg_confirmar.visible = True
        self.page.update()

    # Função que executa a exclusão da tarefa no banco de dados
    def confirmar_exclusao(self, tarefa, dialog):
        crud.excluir_tarefa(SessionLocal(), tarefa.ID)  # Exclui a tarefa do banco de dados
        self.page.close(dialog)  # Fecha a caixa de diálogo
        self.page.controls.clear()  # Limpa os controles da página
        self.page.add(self.construir(self.categoria_filter))  # Recarrega a página com a lista atualizada
        self.page.open(ft.SnackBar(ft.Text("🗑️ Tarefa removida com sucesso!", color=ft.Colors.WHITE), bgcolor='#3C3D37'))  # Exibe notificação de sucesso
        self.page.update()

    # Função que abre o modal para editar uma tarefa
    def editar_tarefa(self, tarefa):
        def salvar_edicao(e):
            # Coleta os dados do formulário de edição
            descricao = descricao_text.value
            situacao = situacao_switch.value
            categoria = dd_edit.value
            data_tarefa = dp_edit.value

            # Valida se os campos obrigatórios foram preenchidos
            if not descricao:
                descricao_text.error_text = 'Descrição é obrigatória'
                dlg_modal_edicao.update()
                return

            if not data_tarefa:
                label_data.value = '📅 Por favor, escolha uma data!'
                dlg_modal_edicao.update()
                return

            # Atualiza a tarefa no banco de dados
            updated_tarefa = crud.editar_tarefa(SessionLocal(), tarefa.ID, descricao, situacao, categoria, data_tarefa)

            if updated_tarefa:
                # Se a tarefa for atualizada com sucesso, recarrega a página
                self.page.close(dlg_modal_edicao)
                self.page.controls.clear()
                self.page.add(self.construir(self.categoria_filter))
                self.page.update()
                self.page.open(ft.SnackBar(ft.Text("✅ Tarefa atualizada com sucesso!", color=ft.Colors.WHITE), bgcolor='#3C3D37'))  # Notificação de sucesso

        # Cria o formulário de edição da tarefa
        descricao_text = ft.TextField(value=tarefa.DESCRICAO, label="Descrição", autofocus=True)
        situacao_switch = ft.Switch(label="Concluída", value=tarefa.SITUACAO)
        dd_edit = ft.Dropdown(
            label="Categoria",
            options=[
                ft.dropdown.Option("Pessoal"),
                ft.dropdown.Option("Compras"),
                ft.dropdown.Option("Trabalho"),
                ft.dropdown.Option("Lista de Desejos")
            ],
            value=tarefa.CATEGORIA,
        )

        label_data = ft.Text(
            value=f"📅 Data selecionada: {tarefa.DATA_TAREFA.strftime('%d-%m-%Y')}" if tarefa.DATA_TAREFA else "📅 Data não selecionada",
            size=16
        )

        def handle_change(e):
            label_data.value = f"📅 Data selecionada: {e.control.value.strftime('%d-%m-%Y')}"
            dlg_modal_edicao.update()

        dp_edit = ft.DatePicker(value=tarefa.DATA_TAREFA, on_change=handle_change)
        dp_button = ft.ElevatedButton("Escolher data", icon=ft.Icons.CALENDAR_MONTH, on_click=lambda e: self.page.open(dp_edit))

        # Modal de edição da tarefa
        dlg_modal_edicao = ft.AlertDialog(
            modal=True,
            content=ft.Column([
                ft.Row([
                    ft.Text("Editar Tarefa", style="headlineSmall"),
                    ft.IconButton(icon=ft.icons.CLOSE, on_click=lambda e: self.page.close(dlg_modal_edicao)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                descricao_text,
                dd_edit,
                dp_button,
                label_data,
                situacao_switch,
            ], spacing=30),
            actions=[
                ft.TextButton("Salvar", on_click=salvar_edicao),  # Salva as alterações feitas
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.open(dlg_modal_edicao)  # Abre o modal de edição
        dlg_modal_edicao.visible = True
        self.page.update()
