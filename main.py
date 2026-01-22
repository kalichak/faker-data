import logging
import os
import sys
import warnings
import flet as ft

# ==============================================================================
# 1. CONFIGURAÇÃO E IMPORTS
# ==============================================================================
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

try:
    from pipeline import processar
    from file_parser import detect_encoding
except ImportError as e:
    print(f"ERRO CRÍTICO: {e}")
    sys.exit(1)

def main(page: ft.Page):
    page.title = "Anonimizador Inteligente"
    page.padding = 20
    page.theme_mode = "light"

    # Compatibilidade de janela
    try:
        page.window.width = 1200
        page.window.height = 800
    except:
        pass

    # ==========================================================================
    # 2. ESTADO E HELPERS
    # ==========================================================================
    state = {
        "file_path": None,
        "header_start": None,
        "header_end": None,
        "data_start": None,
        "lines_preview": [],
        "separator": "|"
    }

    # Helper para bordas
    def get_border(color):
        try:
            return ft.border.all(1, color)
        except:
            return ft.Border.all(1, color)

    # Componentes UI básicos
    txt_status = ft.Text("Cole o caminho do arquivo ou arraste para a janela...", color="grey")
    lv_preview = ft.ListView(expand=True, spacing=2, padding=10)
    
    # Campo de texto para caminho do arquivo
    txt_file_path = ft.TextField(
        label="Caminho do arquivo",
        hint_text=r"Ex: C:\Users\Gabri\arquivo.txt",
        expand=True,
        border_color=ft.Colors.BLUE_300
    )
    
    dd_sep = ft.Dropdown(
        label="Separador",
        options=[
            ft.dropdown.Option("|"),
            ft.dropdown.Option("TAB"),
            ft.dropdown.Option(";"),
            ft.dropdown.Option(","),
        ],
        value="|",
        width=150
    )

    # ==========================================================================
    # 3. LÓGICA
    # ==========================================================================
    def atualizar_cores():
        hs = state["header_start"]
        he = state["header_end"]
        ds = state["data_start"]
        
        for c in lv_preview.controls:
            idx = c.data
            color = "white"
            if hs is not None and idx == hs: 
                color = "#81C784"
            elif he is not None and idx == he: 
                color = "#81C784"
            elif hs is not None and he is not None and hs < idx < he: 
                color = "#C8E6C9"
            elif ds is not None and idx >= ds: 
                color = "#E3F2FD"
            elif ds is not None and idx == ds: 
                color = "#64B5F6"
            c.bgcolor = color
        page.update()

    def on_line_click(e):
        idx = e.control.data
        if state["header_start"] is None:
            state["header_start"] = idx
            page.snack_bar = ft.SnackBar(ft.Text("✓ Início do Header selecionado"))
        elif state["header_end"] is None:
            state["header_end"] = idx
            if state["header_start"] > idx: 
                state["header_end"] = state["header_start"]
                state["header_start"] = idx
            page.snack_bar = ft.SnackBar(ft.Text("✓ Fim do Header selecionado"))
        elif state["data_start"] is None:
            state["data_start"] = idx
            page.snack_bar = ft.SnackBar(ft.Text("✓ Início dos Dados selecionado"))
        else:
            state["header_start"] = idx
            state["header_end"] = None
            state["data_start"] = None
            page.snack_bar = ft.SnackBar(ft.Text("↻ Reiniciando seleção..."))
        
        page.snack_bar.open = True
        atualizar_cores()

    def carregar_arquivo(e):
        """Carrega o arquivo do caminho digitado"""
        path = txt_file_path.value.strip()
        
        if not path:
            txt_status.value = "❌ Digite o caminho do arquivo!"
            txt_status.color = "red"
            page.update()
            return
        
        # Remove aspas que o Windows adiciona ao arrastar
        path = path.strip('"').strip("'")
        
        if not os.path.exists(path):
            txt_status.value = f"❌ Arquivo não encontrado: {path}"
            txt_status.color = "red"
            page.update()
            return
        
        state["file_path"] = path
        txt_status.value = f"✓ Arquivo: {os.path.basename(path)}"
        txt_status.color = "green"
        
        lv_preview.controls.clear()
        state["header_start"] = None
        state["header_end"] = None
        state["data_start"] = None
        
        try:
            enc = detect_encoding(path)
            with open(path, "r", encoding=enc, errors="replace") as f:
                head = [f.readline().strip() for _ in range(50)]
            
            state["lines_preview"] = [x for x in head if x]
            
            for i, txt in enumerate(state["lines_preview"]):
                row = ft.Container(
                    content=ft.Text(
                        txt, 
                        size=12, 
                        font_family="Consolas", 
                        color="black",
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    padding=5,
                    border=get_border("#E0E0E0"),
                    bgcolor="white",
                    data=i,
                    on_click=on_line_click,
                    tooltip=f"Linha {i}"
                )
                lv_preview.controls.append(row)
            
            txt_status.value = f"✓ {os.path.basename(path)} ({len(state['lines_preview'])} linhas carregadas)"
            txt_status.color = "green"
            page.update()
            
        except Exception as err:
            txt_status.value = f"❌ Erro ao ler arquivo: {err}"
            txt_status.color = "red"
            page.update()

    def run_process(e):
        print("=== DEBUG: run_process iniciado ===")
        print(f"file_path: {state['file_path']}")
        print(f"header_start: {state['header_start']}")
        print(f"header_end: {state['header_end']}")
        print(f"data_start: {state['data_start']}")
        
        if not state["file_path"]:
            print("ERRO: Sem arquivo")
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Selecione um arquivo!"))
            page.snack_bar.open = True
            page.update()
            return
            
        if state["data_start"] is None:
            print("ERRO: Sem data_start")
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Defina o início dos dados (linha azul)!"))
            page.snack_bar.open = True
            page.update()
            return

        try:
            print("Desabilitando botão...")
            btn_process.disabled = True
            btn_process.content.value = "⏳ Processando..."
            page.update()
            
            sep = "\t" if dd_sep.value == "TAB" else dd_sep.value
            he = state["header_end"] if state["header_end"] else state["header_start"]
            
            layout = {
                "header": {"start_line": state["header_start"], "end_line": he},
                "data": {"start_line": state["data_start"]},
                "separator": sep
            }
            
            print(f"Layout: {layout}")
            
            out = state["file_path"] + "_anonimizado.txt"
            print(f"Arquivo saída: {out}")
            
            print("Chamando processar()...")
            resultado = processar(state["file_path"], out, layout)
            print(f"Resultado processar: {resultado}")
            
            if os.path.exists(out):
                print(f"✓ Arquivo criado com sucesso: {out}")
                dlg = ft.AlertDialog(
                    title=ft.Text("✓ Sucesso!"),
                    content=ft.Text(f"Arquivo anonimizado salvo em:\n\n{out}"),
                    actions=[
                        ft.TextButton("Abrir pasta", on_click=lambda _: open_folder(out)),
                        ft.TextButton("OK", on_click=lambda _: close_dialog(dlg))
                    ]
                )
            else:
                print("✗ Arquivo NÃO foi criado!")
                dlg = ft.AlertDialog(
                    title=ft.Text("⚠️ Aviso"),
                    content=ft.Text(f"O processamento finalizou mas o arquivo não foi criado.\n\nVerifique o console para mais detalhes."),
                    actions=[ft.TextButton("OK", on_click=lambda _: close_dialog(dlg))]
                )
                
            page.dialog = dlg
            dlg.open = True
            page.update()
            
        except Exception as err:
            import traceback
            print("=== ERRO CAPTURADO ===")
            print(f"Tipo: {type(err).__name__}")
            print(f"Mensagem: {str(err)}")
            print("Traceback completo:")
            traceback.print_exc()
            print("======================")
            
            dlg = ft.AlertDialog(
                title=ft.Text("❌ Erro"),
                content=ft.Text(f"Erro ao processar:\n\n{type(err).__name__}: {str(err)}\n\nVerifique o console para mais detalhes."),
                actions=[ft.TextButton("OK", on_click=lambda _: close_dialog(dlg))]
            )
            page.dialog = dlg
            dlg.open = True
            page.update()
        finally:
            print("Reabilitando botão...")
            btn_process.disabled = False
            btn_process.content.value = "Anonimizar"
            page.update()
            print("=== DEBUG: run_process finalizado ===")

    def close_dialog(dlg):
        dlg.open = False
        page.update()
    
    def open_folder(filepath):
        try:
            import subprocess
            folder = os.path.dirname(filepath)
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except:
            pass

    # ==========================================================================
    # 4. BOTÕES
    # ==========================================================================
    btn_load = ft.ElevatedButton(
        content=ft.Text("Carregar"),
        icon=ft.Icons.UPLOAD_FILE,
        on_click=carregar_arquivo,
        bgcolor=ft.Colors.GREEN_700,
        color=ft.Colors.WHITE
    )

    btn_process = ft.ElevatedButton(
        content=ft.Text("Anonimizar"),
        icon=ft.Icons.SECURITY,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        on_click=run_process
    )

    # ==========================================================================
    # 5. MONTAGEM
    # ==========================================================================
    top_bar = ft.Row([txt_file_path, btn_load, dd_sep, btn_process], spacing=10)
    
    instrucoes = ft.Container(
        content=ft.Column([
            ft.Text(
                "📋 Como usar:", 
                size=13,
                weight=ft.FontWeight.BOLD
            ),
            ft.Text(
                "1. Cole o caminho do arquivo no campo acima (ou arraste o arquivo para a janela)", 
                size=11
            ),
            ft.Text(
                "2. Clique em 'Carregar' para visualizar o arquivo", 
                size=11
            ),
            ft.Text(
                "3. Clique nas linhas para marcar: HEADER (Verde) e DADOS (Azul)", 
                size=11
            ),
            ft.Text(
                "4. Escolha o separador e clique em 'Anonimizar'", 
                size=11
            ),
        ], spacing=3),
        bgcolor="#E3F2FD", 
        padding=15, 
        border_radius=5,
        border=get_border("#90CAF9")
    )

    area_preview = ft.Container(
        content=lv_preview,
        expand=True,
        border=get_border("#BDBDBD"),
        border_radius=5,
        bgcolor="#FAFAFA"
    )

    page.add(
        top_bar, 
        txt_status, 
        instrucoes, 
        area_preview
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)