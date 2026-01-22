## Descrição

O **Data Fake Suite** é uma aplicação modular desenvolvida em Python com interface gráfica usando Flet. Seu objetivo principal é processar dados reais de arquivos (CSV, Excel, TXT) e anonimizar/mascarar informações sensíveis, garantindo segurança para testes, desenvolvimento e uso em bancos de dados empresariais. Ideal para cenários onde dados reais precisam ser protegidos, especialmente ao integrar com IA ou realizar testes de software.

A aplicação permite detectar tipos de colunas automaticamente, aplicar anonimização inteligente e exportar os dados processados, mantendo a estrutura original dos arquivos.

## Funcionalidades

- **Anonimizador de Dados**: Mascara dados pessoais como nomes, CPFs, emails, telefones e endereços, substituindo por valores fictícios realistas.
- **Detecção Automática de Tipos**: Identifica colunas numéricas, de texto, datas, emails, telefones e CPFs automaticamente.
- **Processamento Seguro**: Trata arquivos linha por linha para eficiência de memória, suportando grandes volumes de dados.
- **Interface Gráfica**: Aplicação desktop com abas para diferentes ferramentas (atualmente focada no anonimizer, com expansão para converter e validator).
- **Exportação**: Salva arquivos anonimizados em uma pasta dedicada (`saida/`).
- **Suporte a Múltiplos Formatos**: Arquivos delimitados (CSV, TXT) com separadores configuráveis (vírgula, tabulação, etc.).

## Instalação

### Pré-requisitos

- Python 3.8 ou superior.
- Dependências listadas em requirements.txt.

### Passos

1. Clone ou baixe o repositório.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```bash
   python main.py
   ```

## Uso

1. Abra a aplicação. A interface principal exibe abas para as ferramentas disponíveis.
2. Na aba **Anonimizador**:
   - Clique em "Selecionar Arquivo" para escolher um arquivo de entrada (CSV, Excel ou TXT).
   - Configure o layout: linhas de cabeçalho, início dos dados e separador.
   - Clique em "Processar" para anonimizar os dados.
   - Visualize a comparação entre dados originais e anonimizados na tabela.
   - O arquivo anonimizado será salvo automaticamente em `saida/`.
3. Para outros recursos (converter, validator), aguarde implementações futuras.

### Exemplo de Uso

- Arquivo de entrada: `dados_clientes.csv` com colunas como Nome, CPF, Email.
- Após processamento: Nomes substituídos por nomes fictícios, CPFs mascarados, emails alterados para domínios genéricos.

## Estrutura do Projeto

```
DATA FAKE SUITE/
├── main.py                    # Ponto de entrada da aplicação
├── requirements.txt           # Dependências Python
├── .gitignore                 # Arquivos ignorados pelo Git
├── assets/                    # Recursos (ícones)
├── core/                      # Funcionalidades compartilhadas
│   ├── __init__.py
│   ├── file_utils.py          # Utilitários para arquivos
│   └── ui_components.py       # Componentes de UI reutilizáveis
├── features/                  # Recursos independentes
│   ├── __init__.py
│   ├── anonymizer/            # Módulo de anonimização
│   │   ├── __init__.py
│   │   ├── anonymizer_core.py # Lógica de anonimização
│   │   ├── column_detector.py # Detecção de tipos de coluna
│   │   ├── pipeline.py        # Pipeline de processamento
│   │   └── ui.py              # Interface da aba anonimizer
│   ├── converter/             # (Planejado) Conversor de formatos
│   └── validator/             # (Planejado) Validador de dados
└── saida/                     # Pasta de saída para arquivos processados
```

## Desenvolvimento

### Arquitetura

- **Modular**: Cada feature (anonimizer, converter) é independente, facilitando expansão.
- **Streaming**: Processamento linha a linha para lidar com arquivos grandes sem sobrecarregar a memória.

### Contribuição

1. Fork o repositório.
2. Crie uma branch para sua feature.
3. Implemente e teste.
4. Envie um pull request.

### Testes

Execute testes unitários (se implementados) com:
```bash
python -m pytest tests/
```

## Licença

Este projeto é licenciado sob a MIT License. Consulte o arquivo LICENSE para detalhes.

## Autor

Desenvolvido por Gabriel Kalichak. Versão 1.0.

