import hashlib
import random
import re
from datetime import datetime, timedelta

_CACHE = {}

def _hash(valor: str) -> int:
    """Gera um seed numérico determinístico baseado no valor original."""
    return int(hashlib.sha256(valor.encode('utf-8', errors='ignore')).hexdigest()[:8], 16)

def _preservar_estrutura_numero(original: str, seed: int) -> str:
    """Mantém a estrutura exata de números (pontos, vírgulas, tamanho)"""
    # Extrai apenas os dígitos
    digitos = ''.join(c for c in original if c.isdigit())
    if not digitos:
        return original
    
    # Gera novos dígitos com mesmo tamanho
    random.seed(seed)
    novos_digitos = ''.join(str(random.randint(0, 9)) for _ in range(len(digitos)))
    
    # Reconstrói mantendo a estrutura
    resultado = []
    idx_digito = 0
    for char in original:
        if char.isdigit():
            resultado.append(novos_digitos[idx_digito])
            idx_digito += 1
        else:
            resultado.append(char)
    
    return ''.join(resultado)

def _preservar_estrutura_texto(original: str, seed: int, percentual_troca=0.5) -> str:
    """
    Mantém tamanho e estrutura do texto, trocando apenas parte das letras.
    percentual_troca: 0.5 = troca 50% das letras
    """
    if not original or len(original) < 2:
        return original
    
    random.seed(seed)
    letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    letras_lower = letras.lower()
    
    resultado = list(original)
    indices = [i for i, c in enumerate(original) if c.isalpha()]
    
    # Calcula quantas letras trocar
    num_trocar = max(1, int(len(indices) * percentual_troca))
    indices_trocar = random.sample(indices, min(num_trocar, len(indices)))
    
    for idx in indices_trocar:
        char = resultado[idx]
        if char.isupper():
            resultado[idx] = random.choice(letras)
        else:
            resultado[idx] = random.choice(letras_lower)
    
    return ''.join(resultado)

def _anonimizar_data(original: str, seed: int) -> str:
    """Mantém formato de data mas altera os valores"""
    random.seed(seed)
    
    # Tenta identificar o formato
    if re.match(r'\d{2}\.\d{2}\.\d{4}', original):  # DD.MM.YYYY
        dia = random.randint(1, 28)
        mes = random.randint(1, 12)
        ano = random.randint(2020, 2025)
        return f"{dia:02d}.{mes:02d}.{ano}"
    elif re.match(r'\d{2}/\d{2}/\d{4}', original):  # DD/MM/YYYY
        dia = random.randint(1, 28)
        mes = random.randint(1, 12)
        ano = random.randint(2020, 2025)
        return f"{dia:02d}/{mes:02d}/{ano}"
    elif re.match(r'\d{4}-\d{2}-\d{2}', original):  # YYYY-MM-DD
        dia = random.randint(1, 28)
        mes = random.randint(1, 12)
        ano = random.randint(2020, 2025)
        return f"{ano}-{mes:02d}-{dia:02d}"
    
    # Se não identificou, preserva estrutura de número
    return _preservar_estrutura_numero(original, seed)

def anonimizar(valor: str, tipo: str) -> str:
    """
    Anonimiza preservando a estrutura e tamanho do dado original.
    Mantém formatação, pontuação e tamanho.
    """
    if not valor or not valor.strip():
        return valor

    # Chave para cache (valor + tipo)
    chave = (valor, tipo)
    if chave in _CACHE:
        return _CACHE[chave]

    seed = _hash(valor)
    
    try:
        # EMAIL: mantém estrutura local@dominio.com
        if tipo == "email":
            if '@' in valor:
                local, dominio = valor.split('@', 1)
                novo_local = _preservar_estrutura_texto(local, seed, 0.7)
                if '.' in dominio:
                    nome_dom, ext_dom = dominio.rsplit('.', 1)
                    novo_dominio = _preservar_estrutura_texto(nome_dom, seed + 1, 0.7)
                    novo = f"{novo_local}@{novo_dominio}.{ext_dom}"
                else:
                    novo = f"{novo_local}@{_preservar_estrutura_texto(dominio, seed + 1, 0.7)}"
            else:
                novo = _preservar_estrutura_texto(valor, seed, 0.7)
        
        # CPF/CNPJ: mantém pontos, traços e tamanho
        elif tipo in ["cpf", "cnpj"]:
            novo = _preservar_estrutura_numero(valor, seed)
        
        # EMPRESA/PESSOA: troca apenas 40% das letras para parecer real
        elif tipo in ["empresa", "pessoa"]:
            novo = _preservar_estrutura_texto(valor, seed, 0.4)
        
        # CIDADE: troca 50% das letras
        elif tipo == "cidade":
            novo = _preservar_estrutura_texto(valor, seed, 0.5)
        
        # UF: mantém 2 letras maiúsculas
        elif tipo == "uf":
            random.seed(seed)
            letras = 'ABCDEFGHIJKLMNOPRSTUVWXYZ'  # Estados brasileiros
            novo = random.choice(letras) + random.choice(letras)
        
        # NÚMERO: mantém estrutura exata
        elif tipo == "numero":
            novo = _preservar_estrutura_numero(valor, seed)
        
        # VALOR: mantém vírgulas, pontos e casas decimais
        elif tipo == "valor":
            novo = _preservar_estrutura_numero(valor, seed)
        
        # DATA: mantém formato mas altera valores
        elif tipo == "data":
            novo = _anonimizar_data(valor, seed)
        
        # TEXTO GENÉRICO: troca 30% das letras (mais conservador)
        else:
            if any(c.isalpha() for c in valor):
                novo = _preservar_estrutura_texto(valor, seed, 0.3)
            elif any(c.isdigit() for c in valor):
                novo = _preservar_estrutura_numero(valor, seed)
            else:
                novo = valor  # Mantém símbolos e espaços
                
    except Exception as e:
        # Fallback seguro
        print(f"Erro ao anonimizar '{valor}' (tipo: {tipo}): {e}")
        novo = valor

    _CACHE[chave] = novo
    return novo