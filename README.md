# Automação PromaxWEB (Ambiente de Demonstração / Portfolio)

> [!IMPORTANT]
> **Observação Importante:** As páginas HTML contidas na pasta `portfolio/` são **telas fictícias de teste (mockup)**. Elas foram criadas e adaptadas exclusivamente para demonstrar e ilustrar o funcionamento prático da automação no sistema **PromaxWEB**, permitindo executar e validar os scripts de automação de forma segura, isolada e sem expor dados corporativos ou confidenciais.

---

## 📌 Visão Geral do Projeto

Este projeto consiste em uma automação desenvolvida em Python para navegação, login, tratamento de alertas e execução de rotinas relatóriais e operacionais no ERP **PromaxWEB** via **Selenium WebDriver** em ambiente Internet Explorer (ou Modo IE).

Para fins de demonstração, o projeto inclui um servidor/ambiente mock que simula o fluxo completo do sistema:
1. **Login de Usuário** (`Login.html`)
2. **Seleção de Unidade / Revenda** (`Escolha de unidade.html`)
3. **Seleção de Rotina do Sistema** (`Escolha da rotina.html`)
4. **Execução e Filtragem da Rotina** (`Janela da rotina.html`)

---

## 🏗️ Estrutura do Código

A arquitetura do projeto é dividida em módulos responsáveis por cada etapa da automação:

```text
promax/
├── main.py                   # Ponto de entrada do script (inicialização, fluxo principal e commit)
├── configs.py                # Configurações do IE Driver, caminhos de download e capabilities
├── fecharPopups.py           # Utilitário para fechamento automático de pop-ups e modais do sistema
├── rotinas/                  # Módulos contendo os scripts de automação de rotinas específicas
│   ├── __init__.py           # Centralizador e gerenciador dinâmico de chamadas de rotinas
│   ├── rotinas.py            # Mapeamento e encadeamento de rotinas
│   └── r030224.py            # Automação da rotina 030224 (Planilha de Acompanhamento)
├── portfolio/                # Páginas HTML fictícias e CSS de demonstração
│   ├── Login.html            # Tela de Login adaptada
│   ├── Escolha de unidade.html # Tela de seleção de unidade operacional
│   ├── Escolha da rotina.html # Tela de busca/seleção de código da rotina
│   ├── Janela da rotina.html  # Tela de filtros e geração de relatórios
│   └── login.css             # Estilização CSS responsiva e compatível com Internet Explorer
├── logs_v2/                  # Logs detalhados de cada execução com timestamp
├── IEDriverServer.exe        # Driver do Internet Explorer
├── pyproject.toml / requirements.txt # Dependências do projeto Python
└── README.md                 # Documentação do projeto
```

### Detalhamento dos Componentes principais:

- **`main.py`**:
  - Inicializa o interceptador de logs (`InterceptadorLog`), registrando todas as saídas no terminal e em arquivos `.log`.
  - Executa a limpeza de processos órfãos do `IEDriverServer.exe` e `iexplore.exe`.
  - Instancia o navegador via Selenium, navega pelas etapas de login, unidade e alertas, chamando a rotina desejada.
  - Oferece opção ao final da execução para subir os resultados para o repositório GitHub.

- **`configs.py`**:
  - Define o diretório padrão de download de relatórios.
  - Configura opções e capacidades do Internet Explorer (`InternetExplorerOptions`), como desabilitar zoom, ignorar configurações de modo protegido e definir preferências do navegador.

- **`fecharPopups.py`**:
  - Varredura defensiva que localiza e clica em botões de confirmação/fechamento de pop-ups e alertas do sistema antes e durante a execução das rotinas.

- **`rotinas/r030224.py`**:
  - Exemplo de script de rotina específica (Código `030224` - Planilha de Acompanhamento). Insere o código da rotina, preenche intervalo de datas (`dataInicial`, `dataFinal`) e dispara o comando de visualização do relatório.

- **`portfolio/`**:
  - Contém as telas simuladas com preservação exata das tags HTML, nomes de inputs (`idUsuario`, `senha`, `unidade`, `call`, `dataInicial`, etc.) e IDs de botões (`BotEntrar`, `BotConfirmar`, `BotAcessar`, `BotVisualizar`).
  - Inclui suporte a meta tags de compatibilidade (`X-UA-Compatible: IE=edge`) e fallbacks CSS flexbox/grid para execução perfeita no **Internet Explorer 11 / Modo IE**.

---

## 🛠️ Bibliotecas e Tecnologias Utilizadas

### Python (Back-end & Automação)
- **`selenium`**: Framework principal para navegação, interação com elementos DOM, controle de frames e espera dinâmica (`WebDriverWait`, `expected_conditions`).
- **`webdriver_manager`**: Gerenciamento e download automático das versões adequadas do driver do navegador.
- **`subprocess`**: Execução de comandos do sistema operacional para finalização de processos (`taskkill`) e integração com Git.
- **`os` & `sys`**: Manipulação de caminhos de arquivos, diretórios e captura de saídas padrão (`stdout` / `stderr`).
- **`datetime` & `atexit`**: Geração de registros de data/hora únicos para logs e fechamento seguro de arquivos ao encerrar a execução.

### Front-end (Ambiente de Testes / Portfolio)
- **HTML5 Semantic & Form Elements**: Estruturação dos formulários respeitando a arquitetura do ERP original.
- **CSS3 / Vanilla CSS (`login.css`)**: Regras nativas com suporte completo ao Internet Explorer (`-ms-flexbox`, grid fallbacks, remoção de controles padrão do IE).
- **Tailwind CSS (CDN)**: Estilização moderna e responsiva dos cards e layouts.
- **Google Fonts & Icons**: Tipografia *Inter* e ícones *Material Symbols Outlined*.

---

## 🚀 Como Executar o Projetos

1. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```
   *Ou utilizando o gerenciador `uv`:*
   ```bash
   uv sync
   ```

2. **Servidor Local (Ambiente Mock)**:
   Em um terminal, inicie o servidor HTTP na raiz do projeto:
   ```bash
   python -m http.server 8000
   ```

3. **Executar a Automação**:
   Em outro terminal, execute o script principal:
   ```bash
   python main.py
   ```
