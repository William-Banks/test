import flet as ft
from service import crud
from model.db import SessionLocal
from datetime import datetime

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

        # Obtém a data atual (apenas data, sem a parte de hora)
        data_atual = datetime.now().date()

        for tarefa in tarefas:
            is_expanded = self.expanded_task_id == tarefa.ID
            cor_container = cor_container_expandido if is_expanded else cor_container_normal

            # Calcula a cor da bolinha
            cor_bolinha = ft.colors.RED if tarefa.DATA_TAREFA and tarefa.DATA_TAREFA < data_atual else ft.colors.GREEN

            conteudo = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row([
                                ft.Container(
                            content=ft.CircleAvatar(
                                bgcolor=cor_bolinha,  # Cor da bolinha (verde ou vermelha)
                                radius=8,  # Tamanho da bolinha
                            ),
                            margin=ft.margin.only(right=8),  # Espaçamento entre a bolinha e o nome da tarefa
                        ),
                            ft.Text(tarefa.DESCRICAO, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("✅ Concluída" if tarefa.SITUACAO else "⏳ Pendente"),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        ft.AnimatedSwitcher(
                            content=ft.Column(
                                controls=[
                                    ft.Text(f"📅 Data: {tarefa.DATA_TAREFA.strftime('%d/%m/%Y')}" if tarefa.DATA_TAREFA else "📅 Data: não definida"),
                                    ft.Text(f"📂 Categoria: {tarefa.CATEGORIA}"),
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


            

            tarefa_contextual = ft.CupertinoContextMenu(
                content=conteudo,
                enable_haptic_feedback=True,
                actions=[
                    ft.CupertinoContextMenuAction(
                        text="Editar",
                        trailing_icon=ft.icons.EDIT,
                        on_click=lambda e, t=tarefa: self.editar_tarefa(t)
                    ),
                    ft.CupertinoContextMenuAction(
                        text="Excluir",
                        is_destructive_action=True,
                        trailing_icon=ft.icons.DELETE,
                        on_click=lambda e, t=tarefa: self.remover_tarefa_confirmar(t)
                    ),
                ]
            )

            tarefa_containers.append(tarefa_contextual)

        dd = self.get_dropdown()

        return ft.Column([
            ft.Row([dd], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Column(tarefa_containers, scroll=ft.ScrollMode.AUTO)
        ])

    def toggle_expand(self, task_id):
        self.expanded_task_id = task_id if self.expanded_task_id != task_id else None
        self.page.controls.clear()
        self.page.add(self.construir(self.categoria_filter))
        self.page.update()

    def get_dropdown(self):
        icons = [
            {"name": "Todos", "icon_name": ft.Icons.DENSITY_MEDIUM_OUTLINED},
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
        self.categoria_filter = categoria_selecionada
        self.expanded_task_id = None
        self.page.controls.clear()
        self.page.add(self.construir(self.categoria_filter))
        self.page.update()

    def remover_tarefa_confirmar(self, tarefa):
        dlg_confirmar = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmação de Exclusão"),
            content=ft.Text(f"Tem certeza que deseja excluir a tarefa: {tarefa.DESCRICAO}?"),
            actions=[
                ft.TextButton("Sim", on_click=lambda e: self.confirmar_exclusao(tarefa, dlg_confirmar)),
                ft.TextButton("Não", on_click=lambda e: self.page.close(dlg_confirmar)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.open(dlg_confirmar)
        dlg_confirmar.visible = True
        self.page.update()

    def confirmar_exclusao(self, tarefa, dialog):
        crud.excluir_tarefa(SessionLocal(), tarefa.ID)
        self.page.close(dialog)
        self.page.controls.clear()
        self.page.add(self.construir(self.categoria_filter))
        self.page.open(ft.SnackBar(ft.Text("🗑️ Tarefa removida com sucesso!", color=ft.Colors.WHITE), bgcolor='#3C3D37'))
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

            if updated_tarefa:
                self.page.close(dlg_modal_edicao)
                self.page.controls.clear()
                self.page.add(self.construir(self.categoria_filter))
                self.page.update()
                
                self.page.open(ft.SnackBar(ft.Text("✅ Tarefa atualizada com sucesso!", color=ft.Colors.WHITE), bgcolor='#3C3D37'))


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
                ft.TextButton("Salvar", on_click=salvar_edicao),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.open(dlg_modal_edicao)
        dlg_modal_edicao.visible = True
        self.page.update()