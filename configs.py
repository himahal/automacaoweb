import os
import winreg
from selenium.webdriver.ie.service import Service
from selenium.webdriver.ie.options import Options

def obter_config_ie():
    base_path = os.path.dirname(os.path.abspath(__file__))
    ie_driver_path = r"C:\Users\Breno\Documents\Projetos\IEDriverServer.exe"

    options = Options()
    
    # 1. Compatibilidade com Edge (Obrigatório no Win 11)
    options.attach_to_edge_chrome = True
    options.edge_executable_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    # 2. Segurança (Para evitar a barra amarela de erro)
    options.ignore_protected_mode_settings = True
    options.ignore_zoom_level = True
    
    # --- O PULO DO GATO: EVITAR REINICIALIZAÇÃO ---
    # Força o driver a focar na janela antes de clicar (evita o crash da aba)
    options.require_window_focus = True 
    # Impede que o IE tente "limpar" a sessão e causar o refresh infinito
    options.ensure_clean_session = False
    
    # Remove aquele aviso de "sinalizador sem suporte" que aparece no topo
    options.add_argument("--disable-features=IEToEdge") 

    service = Service(
        executable_path=ie_driver_path,
        log_output=os.path.join(base_path, "iedriver.log")
    )

    return service, options

def configurar_pasta_download():
    caminho = r"C:\Users\Breno\Documents\Projetos\promax\downloads"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\Main", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Default Download Directory", 0, winreg.REG_SZ, caminho)
        winreg.CloseKey(key)
    except: pass