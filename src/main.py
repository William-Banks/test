import flet as ft
from view.home import main
from view.tarefa_view import Page1

def tela(page: ft.Page):
    page.title = "To-Do List"
    page.window.height = 812
    page.window.width = 375
    page.padding = 50
    page.scroll = "adaptive"
    
    def mudar_rota(route):
        page.controls.clear()  # Limpa os elementos antes de carregar a nova página
        
        # Se a rota for a principal (home), chama a função main() para renderizar a tela inicial
        if route == "/":
            tela_inicial = main(page)  # Carrega a página inicial (home)
        # Se a rota for "/tela", chama a página de tarefas (Page1)
        elif route == "/tela":
            tela_inicial = Page1(page)  # Carrega a página de tarefas
        else:
            tela_inicial = ft.Text("Página não encontrada!")  # Página de erro, se a rota não for válida
        
        page.add(tela_inicial)  # Renderiza a página
        page.update()  # Atualiza a interface

    page.on_route_change = lambda e: mudar_rota(e.route)  # Detecta mudanças de rota
    page.go("/")  # Define a rota inicial (página principal)