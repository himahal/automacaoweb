import os
import winreg
from selenium.webdriver.ie.service import Service
from selenium.webdriver.ie.options import Options

def obter_config_ie():
    base_path = os.path.dirname(os.path.abspath(__file__))
    ie_driver_path = os.path.join(base_path, "IEDriverServer.exe")

    options = Options()

    """
    # 1. Busca o caminho do Program Files (x86) dinamicamente
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    
    # 2. Monta o caminho do Edge baseado na variável do sistema
    caminho_edge = os.path.join(program_files_x86, "Microsoft", "Edge", "Application", "msedge.exe")

    # --- Opções do Driver ---
    options.attach_to_edge_chrome = True
    
    # Define o caminho que acabamos de descobrir
    options.edge_executable_path = caminho_edge
    
    print(f"🌐 Microsoft Edge localizado em: {caminho_edge}")
    """

    # 1. Compatibilidade com Edge (Obrigatório no Win 11)
    options.attach_to_edge_chrome = True
    #options.edge_executable_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    # 2. Segurança (Para evitar a barra amarela de erro)
    options.ignore_protected_mode_settings = True
    options.ignore_zoom_level = True
    
    # --- EVITAR REINICIALIZAÇÃO ---
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
    """Configura o registro do Windows para salvar downloads na pasta do projeto"""
    
    # 1. Descobre a raiz do projeto (onde este arquivo está)
    diretorio_projeto = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Define o caminho da pasta 'downloads' dentro do projeto
    caminho_downloads = os.path.join(diretorio_projeto, "downloads")

    # 3. Segurança: Se a pasta não existir, o Python cria ela para você
    if not os.path.exists(caminho_downloads):
        try:
            os.makedirs(caminho_downloads)
            print(f"📁 Pasta 'downloads' criada em: {caminho_downloads}")
        except Exception as e:
            print(f"⚠️ Não foi possível criar a pasta: {e}")

    # 4. Grava no Registro do Windows
    print(f"⚙️ Configurando IE para baixar em: {caminho_downloads}")
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            r"Software\Microsoft\Internet Explorer\Main", 
            0, 
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "Default Download Directory", 0, winreg.REG_SZ, caminho_downloads)
        winreg.CloseKey(key)
        print("✅ Registro atualizado com sucesso!")
    except Exception as e:
        print(f"❌ Falha ao acessar o Registro do Windows: {e}")