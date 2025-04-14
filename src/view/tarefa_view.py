import flet as ft
from service import crud
from model.db import SessionLocal


class Page1:
    def __init__(self, page: ft.Page):
        self.page = page
        self.expanded_task_id = None
        self.categoria_filter = None

    def construir(self, categoria_filter=None):
        tarefas = crud.listar_tarefa(SessionLocal())

        if categoria_filter and categoria_filter != "Todos":
            tarefas = [t for t in tarefas if t.CATEGORIA == categoria_filter]

        tarefa_containers = []

        cor_container_normal = "#3C3D37"
        cor_container_expandido = "#697565"

        for tarefa in tarefas:
            is_expanded = self.expanded_task_id == tarefa.ID
            cor_container = cor_container_expandido if is_expanded else cor_container_normal

            tarefa_container = ft.Container(
                content=ft.Column(
                    controls=[

                        ft.Row([
                            ft.Text(tarefa.DESCRICAO, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("✅ Concluída" if tarefa.SITUACAO else "⏳ Pendente"),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        ft.AnimatedSwitcher(
                            content=ft.Column(
                                controls=[
                                    ft.Text(f"📅 Data: {tarefa.DATA_TAREFA.strftime('%d/%m/%Y')}" if tarefa.DATA_TAREFA else "📅 Data: não definida"),
                                    ft.Text(f"📂 Categoria: {tarefa.CATEGORIA}"),
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        tooltip="Editar tarefa",
                                        on_click=lambda e, task=tarefa: self.editar_tarefa(task)
                                    )
                                ]
                            ) if is_expanded else ft.Container(),
                            duration=300
                        )
                    ]
                ),
                padding=15,
                margin=ft.margin.only(bottom=8),
                border_radius=10,
                bgcolor=cor_container,
                ink=True,
                on_click=lambda e, task_id=tarefa.ID: self.toggle_expand(task_id),
            )

            tarefa_containers.append(tarefa_container)

        dd = self.get_dropdown()

        return ft.Column([
            ft.Row([
                dd
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Column(tarefa_containers, scroll=ft.ScrollMode.AUTO)
        ])

    def toggle_expand(self, task_id):
        self.expanded_task_id = task_id if self.expanded_task_id != task_id else None
        self.page.controls.clear()
        self.page.add(self.construir(self.categoria_filter))  # Passando a categoria filtrada para garantir que a filtragem não se perca
        self.page.update()

    def get_dropdown(self):
        icons = [
            {"name": "Todos", "icon_name": ft.Icons.ALL_OUT},
            {"name": "Pessoal", "icon_name": ft.Icons.EMOJI_EMOTIONS},
            {"name": "Compras", "icon_name": ft.Icons.SHOPPING_CART_OUTLINED},
            {"name": "Trabalho", "icon_name": ft.Icons.COMPUTER},
            {"name": "Lista de Desejos", "icon_name": ft.Icons.FAVORITE},
        ]

        options = [ft.dropdown.Option(key=icon["name"], leading_icon=icon["icon_name"]) for icon in icons]

        return ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,
            enable_filter=True,
            editable=True,
            leading_icon=ft.Icons.SEARCH,
            label="Filtrar tarefas",
            options=options,
            on_change=lambda e: self.filtrar_tarefas(e.control.value)
        )

    def filtrar_tarefas(self, categoria_selecionada):
        self.categoria_filter = categoria_selecionada  # Atualizando o filtro de categoria
        self.expanded_task_id = None  # Resetando a tarefa expandida
        self.page.controls.clear()  # Limpa os controles da página
        self.page.add(self.construir(self.categoria_filter))  # Passando a categoria filtrada para garantir a filtragem correta
        self.page.update()

    def remover_tarefa(self, tarefa, dlg_modal_edicao, dlg_exclusao):
        def confirmar_exclusao(e):
            crud.excluir_tarefa(SessionLocal(), tarefa.ID)
            self.page.controls.clear()
            self.page.add(self.construir(self.categoria_filter))  # Passando o filtro para manter
            self.page.update()
            self.page.close(dlg_confirmar_exclusao)
            self.page.close(dlg_modal_edicao)
            self.page.open(dlg_exclusao)

        def cancelar_exclusao(e):
            self.page.close(dlg_confirmar_exclusao)
            self.page.open(dlg_modal_edicao)
            self.page.update()

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

        self.page.open(dlg_confirmar_exclusao)
        dlg_confirmar_exclusao.visible = True
        self.page.update()

    def editar_tarefa(self, tarefa):
        def salvar_edicao(e):
            descricao = descricao_text.value
            situacao = situacao_switch.value
            categoria = dd_edit.value
            data_tarefa = dp_edit.value

            if not descricao:
                descricao_text.error_text = 'Descrição é obrigatória'
                dlg_modal_edicao.update()
                return

            if not data_tarefa:
                label_data.value = '📅 Por favor, escolha uma data!'
                dlg_modal_edicao.update()
                return

            updated_tarefa = crud.editar_tarefa(SessionLocal(), tarefa.ID, descricao, situacao, categoria, data_tarefa)

            dlg_sucesso = ft.AlertDialog(
            modal=True,
            title=ft.Text("✅ Tarefa atualizada com sucesso!"),
            actions=[ft.TextButton("Fechar", on_click=lambda e: self.page.close(dlg_sucesso))],
            )

            if updated_tarefa:
                # Fecha o modal de edição e mantém o filtro
                self.page.close(dlg_modal_edicao)
                self.page.controls.clear()
                self.page.add(self.construir(self.categoria_filter))  # Passa a categoria para manter o filtro
                self.page.open(dlg_sucesso)
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

        options = [ft.dropdown.Option(key=icon["name"], leading_icon=icon["icon_name"]) for icon in icons]

        dd_edit = ft.Dropdown(
            border=ft.InputBorder.UNDERLINE,
            enable_filter=True,
            editable=True,
            leading_icon=ft.Icons.SEARCH,
            label="Categoria",
            options=options,
            value=tarefa.CATEGORIA
        )

        label_data = ft.Text(
            value=f"📅 Data selecionada: {tarefa.DATA_TAREFA.strftime('%d-%m-%Y')}" if tarefa.DATA_TAREFA else "📅 Data não selecionada",
            size=16
        )

        def handle_change(e):
            data_selecionada = e.control.value
            label_data.value = f"📅 Data selecionada: {data_selecionada.strftime('%d-%m-%Y')}"
            dlg_modal_edicao.update()

        dp_edit = ft.DatePicker(
            value=tarefa.DATA_TAREFA,
            on_change=handle_change
        )

        dp_button = ft.ElevatedButton(
            "Escolher data",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: self.page.open(dp_edit),
        )

        dlg_exclusao = ft.AlertDialog(
            modal=True,
            title=ft.Text("🗑️ Tarefa removida com sucesso!"),
            actions=[ft.TextButton("Fechar", on_click=lambda e: self.page.close(dlg_exclusao))],
            )

        dlg_modal_edicao = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Tarefa"),
            content=ft.Column([
                descricao_text,
                dd_edit,
                dp_button,
                label_data,
                situacao_switch,
            ], spacing=30),
            actions=[
                ft.TextButton("Salvar", on_click=salvar_edicao),
                ft.TextButton("Cancelar", on_click=cancelar_edicao),
                ft.TextButton(
                    "Excluir",
                    on_click=lambda e: self.remover_tarefa(tarefa, dlg_modal_edicao, dlg_exclusao),
                    style=ft.ButtonStyle(color=ft.colors.RED),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.START,
        )

        self.page.open(dlg_modal_edicao)
        dlg_modal_edicao.visible = True
        self.page.update()
