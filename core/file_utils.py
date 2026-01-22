# ============================================================================
# ARQUIVO: core/file_utils.py
# Utilitários compartilhados para manipulação de arquivos
# ============================================================================

import chardet


def detect_encoding(file_path):
    """Detecta o encoding do arquivo lendo os primeiros bytes."""
    with open(file_path, 'rb') as f:
        rawdata = f.read(10000)
    result = chardet.detect(rawdata)
    return result['encoding'] or 'utf-8'


def read_file_lines(path, num_lines=None):
    """Lê linhas do arquivo com encoding automático."""
    enc = detect_encoding(path)
    with open(path, 'r', encoding=enc, errors="replace") as f:
        if num_lines:
            return [f.readline().strip() for _ in range(num_lines)]
        return f.readlines()


def parse_file_header(path, layout, preview_limit=None):
    """Lê o arquivo para extração baseada no layout."""
    enc = detect_encoding(path)
    
    with open(path, 'r', encoding=enc, errors="replace") as f:
        lines = f.readlines()

    hs = layout["header"]["start_line"]
    he = layout["header"]["end_line"]
    ds = layout["data"]["start_line"]

    # Extrai cabeçalho
    if hs is not None and he is not None:
        header = [line.strip() for line in lines[hs : he + 1]]
    else:
        header = []

    # Extrai dados
    if ds is not None:
        data = [line.strip() for line in lines[ds:]]
    else:
        data = []

    if preview_limit:
        return header, data[:preview_limit]
    
    return header, data