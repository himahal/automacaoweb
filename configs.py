import os
import winreg
from selenium.webdriver.ie.service import Service
from selenium.webdriver.ie.options import Options


def obter_config_ie():
    base_path = os.path.dirname(os.path.abspath(__file__))
    ie_driver_path = os.path.join(base_path, "IEDriverServer.exe")

    options = Options()

    options.attach_to_edge_chrome = True
    options.ignore_protected_mode_settings = True
    options.ignore_zoom_level = True
    options.require_window_focus = True
    options.ensure_clean_session = False
    options.add_argument("--disable-features=IEToEdge")

    service = Service(
        executable_path=ie_driver_path,
        log_output=os.path.join(base_path, "iedriver.log")
    )

    return service, options


def configurar_pasta_download():
    """Configura o registro do Windows para salvar downloads na pasta do projeto"""

    diretorio_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_downloads = os.path.join(diretorio_projeto, "downloads")

    if not os.path.exists(caminho_downloads):
        try:
            os.makedirs(caminho_downloads)
            print(f"📁 Pasta 'downloads' criada em: {caminho_downloads}")
        except Exception as e:
            print(f"⚠️ Não foi possível criar a pasta: {e}")

    print(f"⚙️ Configurando IE para baixar em: {caminho_downloads}")
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Internet Explorer\Main",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "Default Download Directory",
                          0, winreg.REG_SZ, caminho_downloads)
        winreg.CloseKey(key)
        print("✅ Registro atualizado com sucesso!")
    except Exception as e:
        print(f"❌ Falha ao acessar o Registro do Windows: {e}")


def restaurar_downloads_padrao():
    """Devolve a pasta de downloads para o padrão do Windows"""

    caminho_padrao = r"C:\Users\usuario\Downloads"

    print("🔄 Restaurando pasta de Downloads do Windows para o padrão...")

    caminho_downloads = os.path.join(caminho_padrao)

    if not os.path.exists(caminho_downloads):
        try:
            os.makedirs(caminho_downloads)
            print(f"📁 Pasta 'downloads' criada em: {caminho_downloads}")
        except Exception as e:
            print(f"⚠️ Não foi possível criar a pasta: {e}")

    print(f"⚙️ Configurando IE para baixar em: {caminho_downloads}")
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Internet Explorer\Main",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "Default Download Directory",
                          0, winreg.REG_SZ, caminho_padrao)
        winreg.CloseKey(key)
        print("✅ Registro atualizado com sucesso!")
    except Exception as e:
        print(f"❌ Falha ao acessar o Registro do Windows: {e}")
