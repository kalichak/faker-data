# ============================================================================
# ARQUIVO: core/ui_components.py
# Componentes UI reutilizáveis entre features
# ============================================================================

import flet as ft


def get_border(color):
    """Helper para criar bordas compatível com diferentes versões do Flet."""
    try:
        return ft.border.all(1, color)
    except:
        return ft.Border.all(1, color)


def create_success_dialog(page, title, message, on_close=None):
    """Cria um diálogo de sucesso padrão."""
    dlg = ft.AlertDialog(
        title=ft.Text(f"✅ {title}"),
        content=ft.Text(message),
        actions=[
            ft.TextButton("OK", on_click=lambda _: close_and_callback(page, dlg, on_close))
        ]
    )
    return dlg


def create_error_dialog(page, title, message, on_close=None):
    """Cria um diálogo de erro padrão."""
    dlg = ft.AlertDialog(
        title=ft.Text(f"❌ {title}"),
        content=ft.Text(message),
        actions=[
            ft.TextButton("OK", on_click=lambda _: close_and_callback(page, dlg, on_close))
        ]
    )
    return dlg


def close_and_callback(page, dialog, callback):
    """Fecha o diálogo e executa callback se fornecido."""
    dialog.open = False
    page.update()
    if callback:
        callback()


def open_folder(filepath):
    """Abre a pasta contendo o arquivo no explorador do sistema."""
    import os
    import sys
    import subprocess
    
    try:
        folder = os.path.dirname(filepath)
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
    except:
        pass


class StatusText(ft.Text):
    """Componente de texto de status com cores automáticas."""
    
    def __init__(self, initial_text="", **kwargs):
        super().__init__(initial_text, **kwargs)
    
    def set_info(self, text):
        self.value = text
        self.color = "grey"
    
    def set_success(self, text):
        self.value = text
        self.color = "green"
    
    def set_error(self, text):
        self.value = text
        self.color = "red"