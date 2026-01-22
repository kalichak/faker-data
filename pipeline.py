
# pipeline.py
from file_parser import parse_file_header, detect_encoding
from column_detector import detectar_tipos
from anonymizer import anonimizar

def processar(entrada, saida, layout):
    # 1. Lê o arquivo completo para pegar cabeçalho e identificar estrutura
    header, dados = parse_file_header(entrada, layout)
    sep = layout["separator"]

    # 2. Detecta tipos baseado em uma amostra dos dados
    # Isso garante a inteligência do processo
    print("Detectando tipos de colunas...")
    tipos = detectar_tipos(dados, sep)
    
    # 3. Processamento e Escrita (Streaming para eficiência de memória)
    enc = detect_encoding(entrada)
    
    start_data_idx = layout["data"]["start_line"]
    
    with open(entrada, 'r', encoding=enc, errors="replace") as fin, \
         open(saida, "w", encoding="utf-8") as fout:
        
        lines = fin.readlines()
        
        # Escreve cabeçalho original
        if header:
            for h in header:
                fout.write(h + "\n")
        
        # Processa dados linha a linha
        for idx, linha in enumerate(lines):
            # Pula linhas que são cabeçalho ou anteriores aos dados
            if idx < start_data_idx:
                continue 
            
            linha = linha.strip()
            if not linha: 
                continue

            campos = linha.split(sep)
            
            novos_campos = []
            for i, val in enumerate(campos):
                tipo = tipos.get(i, "texto")
                # Aplica a anonimização inteligente
                val_anon = anonimizar(val, tipo)
                novos_campos.append(val_anon)

            fout.write(sep.join(novos_campos) + "\n")

    return True
