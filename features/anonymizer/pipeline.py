# ============================================================================
# ARQUIVO: features/anonymizer/pipeline.py
# ============================================================================

import os
from core.file_utils import detect_encoding
from features.anonymizer.column_detector import detectar_tipos
from features.anonymizer.anonymizer_core import anonimizar

def processar(entrada, filename_original, layout):
    """
    Processa o arquivo e retorna dados para comparação visual.
    Salva na pasta 'saida/' do projeto.
    """
    print("🚀 Iniciando pipeline...")
    
    # 1. Definir local de saída (Pasta 'saida' no projeto)
    pasta_saida = os.path.join(os.getcwd(), "saida")
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
    
    caminho_saida = os.path.join(pasta_saida, f"ANON_{filename_original}")
    
    # Configurações
    sep = layout["separator"]
    start_data_idx = layout["data"]["start_line"]
    hs = layout["header"].get("start_line")
    he = layout["header"].get("end_line")
    enc = detect_encoding(entrada)
    
    # 2. Amostragem para detecção de tipos
    print("🔍 Detectando tipos...")
    amostra_dados = []
    with open(entrada, 'r', encoding=enc, errors="replace") as f:
        # Pula header
        for _ in range(start_data_idx): 
            next(f, None)
        # Lê amostra
        for _ in range(150):
            try:
                line = next(f).strip()
                if line: amostra_dados.append(line)
            except StopIteration:
                break
    
    tipos = detectar_tipos(amostra_dados, sep)
    
    # 3. Processamento e Captura de Comparação (Streaming)
    print("💾 Processando...")
    
    comparacao = [] # Lista para guardar (original, novo)
    count = 0
    
    with open(entrada, 'r', encoding=enc, errors="replace") as fin, \
         open(caminho_saida, "w", encoding="utf-8") as fout:
        
        # Copia cabeçalho se existir
        fin.seek(0)
        linhas_lidas = enumerate(fin)
        
        # Reset para ler e gravar
        for idx, linha in linhas_lidas:
            linha_raw = linha.strip()
            
            # Cabeçalho: Copia e salva para comparação se quiser
            if hs is not None and he is not None and hs <= idx <= he:
                fout.write(linha_raw + "\n")
                continue
            
            if idx < start_data_idx or not linha_raw:
                continue

            # Dados: Anonimiza
            campos = linha_raw.split(sep)
            novos_campos = []
            
            for i, val in enumerate(campos):
                tipo = tipos.get(i, "texto")
                val_anon = anonimizar(val, tipo)
                novos_campos.append(str(val_anon))
            
            nova_linha = sep.join(novos_campos)
            fout.write(nova_linha + "\n")
            
            # Guarda as primeiras 20 linhas para mostrar ao usuário
            if len(comparacao) < 20:
                comparacao.append((linha_raw, nova_linha))
            
            count += 1

    print(f"✅ Arquivo salvo em: {caminho_saida}")
    return caminho_saida, comparacao