import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def obter_config_chrome():
    # --- 1. CONFIGURAÇÃO DE DIRETÓRIOS ---
    base_path = "/home/brenonote/PycharmProjects/promax"
    perfil_local = os.path.join(base_path, "perfil_promax")
    download_dir = os.path.join(base_path, "Arquivos_Excel", "Download")

    # Garante que as pastas existam no Linux antes de iniciar o navegador
    #os.makedirs(perfil_local, exist_ok=True)
    #os.makedirs(download_dir, exist_ok=True)

    options = Options()
    # No CachyOS, o binário padrão costuma ser o chromium ou google-chrome-stable
    options.binary_location = "/usr/bin/chromium"

    # --- 2. PREFERÊNCIAS DE DOWNLOAD E SEGURANÇA---
    # Ajustei os nomes das chaves para o padrão Chromium moderno
    prefs = {
        "profile.default_content_settings_values.popups": 1,
        "profile.default_content_settings_values.notifications": 1,
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,  # Desabilita o bloqueio de downloads "perigosos" (.inf/.csv)
        "safebrowsing.disable_download_protection": True,
        "download.extensions_to_open": "csv",
    }
    options.add_experimental_option("prefs", prefs)

    # --- 3. FLAGS DE COMPATIBILIDADE PROMAX (SEGURANÇA DESATIVADA) ---
    # Estas flags substituem as "Opções da Internet" do Windows
    options.add_argument("--disable-web-security")  # Permite acesso entre domínios/frames
    options.add_argument("--disable-site-isolation-trials")  # Crucial para navegar em frames aninhados
    options.add_argument("--allow-running-insecure-content")  # Permite o mix de HTTP/HTTPS do sistema legado
    options.add_argument("--ignore-certificate-errors")  # Ignora alertas de SSL inválido
    options.add_argument("--allow-untrusted-downloads")  # Força o download de arquivos sem certificado

    # Bloqueia o redirecionamento forçado para HTTPS (Problema que você relatou)
    options.add_argument("--disable-features=HttpsUpgrades,DownloadBubble")

    # --- 4. FLAGS DE PERFORMANCE E AMBIENTE (PLASMA 6 / WAYLAND) ---
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Evita crashes por falta de memória compartilhada
    options.add_argument("--ozone-platform-hint=auto")  # Suporte nativo ao Wayland do KDE 6
    options.add_argument(f"--user-data-dir={perfil_local}")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")

    # Remove a barra de "O Chrome está sendo controlado por software de automação"
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # --- 5. INICIALIZAÇÃO DO SERVICE ---
    # Log configurado para ajudar a debugar se o frame falhar
    service = Service(
        executable_path="/usr/bin/chromedriver",
        log_output=os.path.join(base_path, "chromedriver.log")
    )

    return service, options