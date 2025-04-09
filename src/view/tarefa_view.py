import flet as ft
from service import crud
from model.db import SessionLocal


class Page1:
    def __init__(self, page: ft.Page):
        self.page = page  # Inicializa a página

    def construir(self, categoria_filter=None):
        # Obtém todas as tarefas do banco de dados
        tarefas = crud.listar_tarefa(SessionLocal())

        # Se houver um filtro de categoria, filtra as tarefas
        if categoria_filter and categoria_filter != "Todos":
            tarefas = [t for t in tarefas if t.CATEGORIA == categoria_filter]
        
        # Lista de colunas do DataTable
        columns = [
            ft.DataColumn(ft.Text("Descrição")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Categoria")),
            ft.DataColumn(ft.Text("Data")),
            ft.DataColumn(ft.Text("Ações")),
            
        ]

        # Lista de linhas para o DataTable
        rows = []
        for tarefa in tarefas:
            rows.append(
                ft.DataRow(
                    cells=[ 
                        ft.DataCell(content=ft.Row([
                            ft.Container(
                                content=ft.Text(tarefa.DESCRICAO),
                                width=70,  # Limita a largura para que o texto caiba
                            )
                        ])),
                        ft.DataCell(content=ft.Row([
                            ft.Container(
                                content=ft.Text("Concluída" if tarefa.SITUACAO else "Pendente"),
                                width=70,  # Limita a largura para que o texto caiba
                            )
                        ])),
                        ft.DataCell(content=ft.Row([
                            ft.Container(
                                content=ft.Text(str(tarefa.CATEGORIA)),
                                width=70,  # Limita a largura para que o texto caiba
                            )
                        ])),
                        ft.DataCell(content=ft.Row([
                            ft.Container(
                                content=ft.Text(str(tarefa.DATA_TAREFA)),
                                width=75,  # Limita a largura para que o texto caiba
                            )
                        ])),
                        ft.DataCell(content=ft.Row([
                            ft.Container(
                                content=ft.Row([  
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="Editar tarefa",
                                        on_click=lambda e, task=tarefa: self.editar_tarefa(task)
                                    ),
                                ]),  # Limita a largura para que o conteúdo caiba
                            )
                        ])),
                    ] ,
                ),
            )

        # Criação da DataTable com configurações de adaptabilidade
        data_table = ft.DataTable(
            column_spacing=5,  # Ajuste no espaçamento entre colunas
            rows=rows,  # Linhas da tabela
            data_row_min_height=40,  # Menor altura das linhas de dados
            columns=columns,
            border=ft.border.all(2, "black"),
            border_radius=10,
            data_row_max_height=60,  # Maior altura das linhas de dados
            heading_row_height=50,  # Altura da linha de cabeçalho
            show_bottom_border=True,  # Mostrar borda inferior
        )
        
        # Adiciona o Dropdown no canto superior direito
        icons = [
            {"name": "Todos", "icon_name": ft.Icons.ALL_OUT},
            {"name": "Pessoal", "icon_name": ft.Icons.EMOJI_EMOTIONS},
            {"name": "Compras", "icon_name": ft.Icons.SHOPPING_CART_OUTLINED},
            {"name": "Trabalho", "icon_name": ft.Icons.COMPUTER},
            {"name": "Lista de Desejos", "icon_name": ft.Icons.FAVORITE},
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
            label="Filtrar tarefas",
            options=get_options(),
            on_change=lambda e: self.filtrar_tarefas(dd.value)
        )

        # Layout da página com a tabela e o dropdown no canto superior direito
        return ft.Row(
            [
                ft.Column(
                    [
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK_IOS,  # Ícone de voltar
                            tooltip="Voltar",
                            on_click=lambda _: self.page.go("/interface"),  # Ação para voltar à página anterior
                        ),
                        dd,
                        data_table,  # Tabela de tarefas
                    ],
                    expand=True,
                ),
            ]
        )

    def filtrar_tarefas(self, categoria_selecionada):
        # Recarrega a página com o filtro aplicado
        self.page.controls.clear()
        self.page.add(self.construir(categoria_selecionada))
        self.page.update()

    def remover_tarefa(self, tarefa, dlg_modal_edicao):
        # Função para remover a tarefa, que será chamada no botão vermelho no modal
        def confirmar_exclusao(e):
            # Remove a tarefa do banco de dados
            crud.excluir_tarefa(SessionLocal(), tarefa.ID)
            
            # Atualiza a listagem na interface
            self.page.controls.clear()
            self.page.add(self.construir())
            self.page.update()

            # Fecha o modal de confirmação de exclusão
            self.page.close(dlg_confirmar_exclusao)

            # Fecha o modal de edição apenas se a exclusão for confirmada
            self.page.close(dlg_modal_edicao)

        def cancelar_exclusao(e):
            # Fecha apenas o modal de confirmação de exclusão
            self.page.close(dlg_confirmar_exclusao)
            self.page.open(dlg_modal_edicao)  # Reabre o modal de edição
            self.page.update()

        # Dialogo de confirmação de exclusão
        dlg_confirmar_exclusao = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmação de Exclusão"),
            content=ft.Text(f"Você tem certeza que deseja excluir a tarefa: {tarefa.DESCRICAO}?"),
            actions=[
                ft.TextButton("Sim", on_click=confirmar_exclusao),
                ft.TextButton("Não", on_click=cancelar_exclusao),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Abre o modal de confirmação de exclusão sem fechar o modal de edição
        self.page.open(dlg_confirmar_exclusao)
        dlg_confirmar_exclusao.visible = True
        self.page.update()

    def editar_tarefa(self, tarefa):
        # Função para editar a tarefa
        def salvar_edicao(e):
            descricao = descricao_text.value
            situacao = situacao_switch.value
            categoria = dd_edit.value
            data_tarefa = dp_edit.value

            updated_tarefa = crud.editar_tarefa(SessionLocal(), tarefa.ID, descricao, situacao, categoria, data_tarefa)

            if updated_tarefa:
                self.page.close(dlg_modal_edicao)
                self.page.controls.clear()
                self.page.add(self.construir())
                self.page.update()

        def cancelar_edicao(e):
            self.page.close(dlg_modal_edicao)
            self.page.update()

        descricao_text = ft.TextField(value=tarefa.DESCRICAO, label="Descrição", autofocus=True)
        situacao_switch = ft.Switch(label="Concluída", value=tarefa.SITUACAO)

        icons = [
            {"name": "Pessoal", "icon_name": ft.Icons.EMOJI_EMOTIONS},
            {"name": "Compras", "icon_name": ft.Icons.SHOPPING_CART_OUTLINED},
            {"name": "Trabalho", "icon_name": ft.Icons.COMPUTER},
            {"name": "Lista de Desejos", "icon_name": ft.Icons.FAVORITE},
        ]

        def get_options():
            options = []
            for icon in icons:
                options.append(
                    ft.DropdownOption(key=icon["name"], leading_icon=icon["icon_name"])
                )
            return options

        dd_edit = ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,
            enable_filter=True,
            editable=True,
            leading_icon=ft.Icons.SEARCH,
            label="Categoria",
            options=get_options(),
            value=tarefa.CATEGORIA
        )

        def handle_change(e):
            # Atualiza a label com a data selecionada
            data_selecionada = e.control.value
            label_data.value = f"Data selecionada: {data_selecionada.strftime('%d-%m-%Y')}"
            dlg_modal_edicao.update()

        dp_edit = ft.DatePicker(on_change=handle_change)

        dp = ft.ElevatedButton(
            "Escolher data",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: dlg_modal_edicao.open(dp_edit),
        )

        label_data = ft.Text(value=dp_edit.value, size=16)

        dlg_modal_edicao = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Tarefa"),
            content=ft.Column([  
                descricao_text,
                dd_edit,
                dp,
                situacao_switch,
            ]),
            actions=[
                ft.TextButton("Salvar", on_click=salvar_edicao),
                ft.TextButton("Cancelar", on_click=cancelar_edicao),
                # Botão Excluir na parte inferior esquerda, em vermelho
                ft.TextButton(
                    "Excluir", 
                    on_click=lambda e: self.remover_tarefa(tarefa, dlg_modal_edicao),
                    style=ft.ButtonStyle(color=ft.colors.RED),  # Usando ButtonStyle para mudar a cor
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.START,  # Alinhamento do botão para o lado esquerdo
        )

        # Abre o modal de edição
        self.page.open(dlg_modal_edicao)
        dlg_modal_edicao.visible = True
        self.page.update()
