# ============================================================================
# ARQUIVO: features/anonymizer/ui.py
# ============================================================================

import os
import flet as ft
import tkinter as tk
from tkinter import filedialog
from core.file_utils import detect_encoding
from core.ui_components import get_border, open_folder, StatusText
from features.anonymizer.pipeline import processar

class AnonymizerTab(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page 
        self.expand = True
        
        self.state = {
            "file_path": None,
            "header_start": None,
            "header_end": None,
            "data_start": None,
            "lines_preview": [],
            "separator": "|"
        }
        self._build_ui()
    #
    
    def _build_ui(self):
        self.txt_status = StatusText()
        self.txt_status.set_info("Selecione um arquivo para começar...")
        
        # Lista de preview (inicial)
        self.lv_preview = ft.ListView(expand=True, spacing=4, padding=12)
        
        # Tabela de comparação (inicialmente oculta)
        self.dt_comparison = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Original", weight="bold", color="red")),
                ft.DataColumn(ft.Text("Anonimizado", weight="bold", color="green")),
            ],
            rows=[],
            visible=False,
            heading_row_color=ft.Colors.BLUE_50,
            border=get_border("#BDBDBD"),
            expand=True,
        )

        # Container que alterna entre Preview e Comparação
        self.content_area = ft.Container(
            content=ft.Column([self.lv_preview, self.dt_comparison], scroll="auto", expand=True),
            expand=True,
            border=get_border("#BDBDBD"),
            border_radius=5,
            bgcolor="#FAFAFA",
            padding=10
        )
        
        self.txt_file_path = ft.TextField(
            label="Caminho do arquivo",
            read_only=True,
            expand=True,
            text_size=12
        )
        
        self.dd_sep = ft.Dropdown(
            label="Separador",
            options=[
                ft.dropdown.Option("|", "| Pipe"),
                ft.dropdown.Option("TAB", "TAB"),
                ft.dropdown.Option(";", "; Ponto-vírgula"),
                ft.dropdown.Option(",", ", Vírgula"),
            ],
            value="|",
            width=120
        )
        
        # Botões
        btn_pick = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.FOLDER_OPEN), ft.Text("Buscar")]),
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY, color="white"),
            on_click=self._pick_file_native
        )
        
        btn_reset = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Resetar visualização",
            on_click=self._reset_view
        )
        
        self.btn_process = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.SECURITY), ft.Text("Mascarar Dados")]),
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color="white"),
            on_click=self._run_process
        )
        
        top_bar = ft.Row([self.txt_file_path, btn_pick, self.dd_sep, self.btn_process, btn_reset])
        
        self.content = ft.Column([
            top_bar,
            self.txt_status,
            self.content_area
        ], expand=True)

    def _pick_file_native(self, e):
        try:
            root = tk.Tk()
            root.withdraw() 
            root.attributes('-topmost', True)
            path = filedialog.askopenfilename()
            root.destroy()
            
            if path:
                self.txt_file_path.value = path
                self.main_page.update()
                self._load_file(path)
        except:
            pass
            
    def _load_file(self, path):
        self._reset_view(None) # Limpa views anteriores
        self.state["file_path"] = path
        self.lv_preview.controls.clear()
        
        try:
            enc = detect_encoding(path)
            with open(path, "r", encoding=enc, errors="replace") as f:
                lines = [f.readline().strip() for _ in range(50)]
            
            self.state["lines_preview"] = [x for x in lines if x]
            
            for i, txt in enumerate(self.state["lines_preview"]):
                self.lv_preview.controls.append(ft.Container(
                    content=ft.Text(txt, size=12, font_family="Consolas", color="black"),
                    padding=5,
                    bgcolor="white",
                    border=get_border("#E0E0E0"),
                    data=i,
                    on_click=self._on_line_click
                ))
            
            self.txt_status.set_success("✅ Arquivo carregado. Selecione HEADER (Verde) e DADOS (Azul).")
            self.main_page.update()
        except Exception as e:
            self.txt_status.set_error(f"Erro: {e}")
            self.main_page.update()

    def _on_line_click(self, e):
        idx = e.control.data
        if self.state["header_start"] is None:
            self.state["header_start"] = idx
        elif self.state["header_end"] is None:
            self.state["header_end"] = idx
            if self.state["header_start"] > idx:
                self.state["header_end"] = self.state["header_start"]
                self.state["header_start"] = idx
        elif self.state["data_start"] is None:
            self.state["data_start"] = idx
        else:
            self.state["header_start"] = idx
            self.state["header_end"] = None
            self.state["data_start"] = None
        self._update_colors()

    def _update_colors(self):
        hs, he, ds = self.state["header_start"], self.state["header_end"], self.state["data_start"]
        for c in self.lv_preview.controls:
            idx = c.data
            if hs is not None and idx == hs: c.bgcolor = "#A5D6A7" # Verde claro
            elif he is not None and idx == he: c.bgcolor = "#A5D6A7"
            elif hs is not None and he is not None and hs < idx < he: c.bgcolor = "#E8F5E9"
            elif ds is not None and idx >= ds: c.bgcolor = "#BBDEFB" # Azul claro
            else: c.bgcolor = "white"
        self.main_page.update()

    def _run_process(self, e):
        if not self.state["file_path"] or self.state["data_start"] is None:
            self.main_page.snack_bar = ft.SnackBar(ft.Text("❌ Selecione arquivo e linha de dados!"))
            self.main_page.snack_bar.open = True
            self.main_page.update()
            return

        self.btn_process.disabled = True
        self.btn_process.content = ft.Row([ft.ProgressRing(width=16, height=16), ft.Text(" Processando...")])
        self.main_page.update()

        try:
            sep = "\t" if self.dd_sep.value == "TAB" else self.dd_sep.value
            he = self.state["header_end"] if self.state["header_end"] else self.state["header_start"]
            
            layout = {
                "header": {"start_line": self.state["header_start"], "end_line": he},
                "data": {"start_line": self.state["data_start"]},
                "separator": sep
            }
            
            filename = os.path.basename(self.state["file_path"])
            
            # --- CHAMA O PIPELINE ATUALIZADO ---
            caminho_saida, dados_comparacao = processar(self.state["file_path"], filename, layout)
            
            # --- MOSTRAR COMPARAÇÃO NA TELA ---
            self._show_comparison(caminho_saida, dados_comparacao)
            
        except Exception as err:
            import traceback
            traceback.print_exc()
            self.txt_status.set_error(f"Erro fatal: {str(err)}")
        finally:
            self.btn_process.disabled = False
            self.btn_process.content = ft.Row([ft.Icon(ft.Icons.SECURITY), ft.Text("ANONIMIZAR")])
            self.main_page.update()

    def _show_comparison(self, caminho_saida, dados):
        """Exibe a tabela de comparação."""
        self.lv_preview.visible = False
        self.dt_comparison.visible = True
        self.dt_comparison.rows.clear()
        
        for original, novo in dados:
            self.dt_comparison.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(original, size=11, font_family="Consolas", color="red")),
                    ft.DataCell(ft.Text(novo, size=11, font_family="Consolas", color="green")),
                ])
            )
            
        self.txt_status.set_success(f"✅ Concluído! Salvo em: .../saida/{os.path.basename(caminho_saida)}")
        
        # Botão para abrir a pasta
        dlg = ft.AlertDialog(
            title=ft.Text("Sucesso!"),
            content=ft.Text("Arquivo gerado com sucesso na pasta 'saida'."),
            actions=[
                ft.TextButton("Abrir Pasta", on_click=lambda _: self._open_folder_dlg(caminho_saida)),
                ft.TextButton("Fechar", on_click=lambda _: self._close_dlg())
            ]
        )
        self.main_page.dialog = dlg
        dlg.open = True
        self.main_page.update()

    def _reset_view(self, e):
        self.lv_preview.visible = True
        self.dt_comparison.visible = False
        self.main_page.update()

    def _close_dlg(self):
        self.main_page.dialog.open = False
        self.main_page.update()
        
    def _open_folder_dlg(self, path):
        open_folder(path)
        self._close_dlg()