"""
╔══════════════════════════════════════════════════════════════════════════╗
║                         DATA FAKE SUITE                                  ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import logging
import sys
import warnings
import flet as ft


# CONFIGURAÇÃO
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)


# IMPORTS DAS FEATURES
try:
    from features.anonymizer.ui import AnonymizerTab
    # from features.converter.ui import ConverterTab
except ImportError as e:
    print(f"❌ ERRO CRÍTICO: Não foi possível importar as features.")
    print(f"   Detalhes: {e}")
    sys.exit(1)


APP_CONFIG = {
    "title": "Data Fake Suite",
    "version": "1.0",
    "author": "Gabriel Kalichak",
    "window_width": 1400,
    "window_height": 900,
    "window_resizable": True,
    "resizable_min_width": 800,
    "resizable_min_height": 600,
    "theme_mode": "",
    "color_scheme": ft.Colors.BLUE,
}


def main(page: ft.Page):
    """
    Ponto de entrada principal da aplicação.
    """
    
    #  CONFIGURAÇÃO DA PÁGINA 
    page.title = APP_CONFIG["title"]
    page.padding = 20
    page.theme_mode = APP_CONFIG["theme_mode"]
    page.theme = ft.Theme(color_scheme_seed=APP_CONFIG["color_scheme"])
    
    try:
        page.window.width = APP_CONFIG["window_width"]
        page.window.height = APP_CONFIG["window_height"]
    except:
        pass

    #  ÁREA DE CONTEÚDO (CORPO) 
    # Aqui é onde o conteúdo das ferramentas será exibido
    body_container = ft.Container(expand=True)

    #  FUNÇÃO DE TROCA DE ABAS 
    def mudar_aba(e):
        # Identifica qual botão foi clicado (0, 1, 2...)
        selected_index = e.control.data
        
        # Atualiza o visual dos botões (destaque o selecionado)
        for btn in menu_bar.controls:
            if btn.data == selected_index:
                btn.style = ft.ButtonStyle(
                    color=ft.Colors.BLUE, 
                    bgcolor=ft.Colors.BLUE_50
                )
            else:
                btn.style = ft.ButtonStyle(
                    color=ft.Colors.GREY_700, 
                    bgcolor=ft.Colors.TRANSPARENT
                )
        
        # Troca o conteúdo
        body_container.content = None # Limpa
        
        if selected_index == 0:
            # Carrega o Anonimizador
            print("🔄 Carregando Anonimizador...")
            try:
                content = AnonymizerTab(page)
                body_container.content = content
            except Exception as err:
                import traceback
                traceback.print_exc()
                body_container.content = ft.Text(f"Erro ao carregar feature: {err}", color="red")
        
        elif selected_index == 1:
            # Exemplo para futura feature
            body_container.content = ft.Text("🚧 Conversor em desenvolvimento...", size=20)
        
        elif selected_index == 2:
            body_container.content = ft.Text("🚧 Validador em desenvolvimento...", size=20)
            
        page.update()

    #  BARRA DE MENU (ABAS MANUAIS) 
    menu_bar = ft.Row(
        controls=[
            ft.TextButton(
                content=ft.Row([ft.Icon(ft.Icons.SECURITY), ft.Text("Anonimizador")]),
                data=0,
                on_click=mudar_aba,
                style=ft.ButtonStyle(color=ft.Colors.BLUE, bgcolor=ft.Colors.BLUE_50) # Começa selecionado
            ),
            ft.TextButton(
                content=ft.Row([ft.Icon(ft.Icons.TRANSFORM), ft.Text("Conversor")]),
                data=1,
                on_click=mudar_aba
            ),
            ft.TextButton(
                content=ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE), ft.Text("Validador")]),
                data=2,
                on_click=mudar_aba
            ),
        ],
        spacing=10
    )

    #  INICIALIZAÇÃO 
    # Carrega a primeira aba (Anonimizador) ao iniciar
    body_container.content = AnonymizerTab(page)

    #  CABEÇALHO DO APP 
    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ANALYTICS, size=32, color=ft.Colors.BLUE_700),
            ft.Column([
                ft.Text(APP_CONFIG["title"], size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                ft.Text(f"v{APP_CONFIG['version']} • Sistema Modular", size=11, color=ft.Colors.GREY_600),
            ], spacing=0),
        ], spacing=10),
        padding=ft.padding.only(bottom=10)
    )
    
    #  LAYOUT PRINCIPAL 
    main_content = ft.Column([
        header,
        menu_bar,
        ft.Divider(height=1, color=ft.Colors.GREY_300),
        body_container
    ], expand=True, spacing=10)
    
    page.add(ft.Container(content=main_content, expand=True, padding=10))
    page.update()
    print("Aplicação iniciada")

if __name__ == "__main__":
    ft.app(target=main)