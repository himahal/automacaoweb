import os
from selenium.webdriver.ie.service import Service
from selenium.webdriver.ie.options import Options

def obter_config_ie():
    # --- 1. CAMINHOS ---
    # Usamos o os.path para pegar a pasta do projeto automaticamente no seu SSD
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # O log será criado na mesma pasta do script
    log_path = os.path.join(base_path, "iedriver.log")

    # Caminho onde o driver deve estar no Windows
    ie_driver_path = r"C:\Users\Breno\Documents\Projetos\IEDriverServer.exe"

    # --- 2. OPÇÕES DO IE ---
    options = Options()

    # Mantendo exatamente as opções que você pediu:
    options.ignore_protected_mode_settings = True
    options.ignore_zoom_level = True
    options.require_window_focus = False

    # --- 3. SERVICE ---
    service = Service(
        executable_path=ie_driver_path,
        log_output=log_path
    )

    return service, options