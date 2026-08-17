from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Importação de módulos personalizados
from configs import obter_config_ie, configurar_pasta_download
from fecharPopups import fechar_popups
from rotinas import rotinas

import sys
import os
from datetime import datetime
import atexit

# ====================================================================
# INTERCEPTADOR DE LOGS
# ====================================================================


class InterceptadorLog:
    def __init__(self, caminho_arquivo):
        self.terminal = sys.stdout
        self.arquivo_log = open(caminho_arquivo, "a", encoding="utf-8")
        atexit.register(self.fechar)

    def write(self, mensagem):
        self.terminal.write(mensagem)
        self.arquivo_log.write(mensagem)
        self.arquivo_log.flush()

    def flush(self):
        self.terminal.flush()
        self.arquivo_log.flush()

    def fechar(self):
        if not self.arquivo_log.closed:
            self.arquivo_log.flush()
            self.arquivo_log.close()


pasta_logs = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "logs_v2")
os.makedirs(pasta_logs, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nome_arquivo_log = os.path.join(pasta_logs, f"execucao_{timestamp}.log")

logger = InterceptadorLog(nome_arquivo_log)
sys.stdout = logger
sys.stderr = logger

# --- Variáveis Globais ---
login = "Teste"
senha = "Teste"


def limpar_processos_antigos():
    """Fecha processos órfãos do IEDriverServer e iexplore para evitar travamento na inicialização"""
    import subprocess
    print("🧹 Limpando processos antigos (IEDriverServer e Internet Explorer) do Windows...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "IEDriverServer.exe"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/F", "/IM", "iexplore.exe"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def login_e_menu():
    """Realiza o acesso inicial, login e limpeza de alertas do Promax"""
    print("\n" + "="*50)
    print("🚀 INICIANDO PROCESSO DE LOGIN PROMAX")
    print("="*50)

    limpar_processos_antigos()

    configurar_pasta_download()
    service, options = obter_config_ie()

    print("🌐 Abrindo navegador Internet Explorer...")
    driver = webdriver.Ie(service=service, options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 1000)

    print("\U0001f4e5 Acessando a URL do sistema (Ambiente Mock)...")

    diretorio_projeto = os.path.dirname(os.path.abspath(__file__))
    caminho_mock = os.path.join(diretorio_projeto, "portfolio", "Login.html")

    url_mock = "http://localhost:8000/Login.html"

    driver.get(url_mock)

    # --- Etapa: Login ---
    print("🔑 Identificando frames e preenchendo credenciais...")

    try:
        wait.until(EC.presence_of_element_located((By.NAME, "idUsuario")))
        loginI = driver.find_element(By.NAME, "idUsuario")
    except Exception:
        wait.until(EC.presence_of_element_located((By.NAME, "Usuario")))
        loginI = driver.find_element(By.NAME, "Usuario")

    loginI.send_keys(Keys.CONTROL + "a")
    loginI.send_keys(Keys.DELETE)
    loginI.send_keys(login)

    try:
        senhaI = driver.find_element(By.NAME, "senha")
    except Exception:
        senhaI = driver.find_element(By.NAME, "Senha")

    senhaI.send_keys(Keys.CONTROL + "a")
    senhaI.send_keys(Keys.DELETE)
    senhaI.send_keys(senha)

    try:
        driver.find_element(By.ID, "BotEntrar").click()
    except Exception:
        driver.find_element(By.ID, "BtnConfirm").click()

    print("✅ Login efetuado com sucesso!")

    try:
        tela_senha = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.ID, "algum_id_da_tela_de_senha"))
        )
        print("⚠️ Aviso: Tela de alteração de senha detectada!")
        html_senha = driver.page_source
        with open("html_tela_senha.html", "w", encoding="utf-8") as f:
            f.write(html_senha)
    except Exception:
        print("✅ Nenhum aviso de senha. Seguindo para o sistema...")

    # --- Etapa: Seleção de Unidade ---
    driver.switch_to.default_content()
    print("🏢 Selecionando unidade...")
    driver.find_element(By.NAME, "BotConfirmar").click()
    print("📍 Unidade confirmada!")

    # --- Etapa: Limpeza de Alertas ---
    print("🧹 Fechando pop-ups de alerta...")
    fechar_popups(driver, 5)
    print("✨ Varredura de alertas concluída.")

    return driver, wait


def subir_github():
    try:
        print("📦 Preparando arquivos para o commit...")
        import subprocess
        subprocess.run(["git", "add", "."], check=True)

        commit_msg = f"Execucao automatica das rotinas - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        print("🚀 Enviando para o GitHub (branch atual)...")
        subprocess.run(["git", "push"], check=True)

        print("✅ Atualização enviada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao tentar subir para o GitHub: {e}")


if __name__ == "__main__":
    driver, wait = login_e_menu()

    try:
        print("\n" + "-"*50)
        print("🎯 INICIANDO EXECUÇÃO DAS ROTINAS")
        print("-"*50)

        rotinas.chamar_rotina(driver, wait, "030224")

        print("\n🏆 Todas as rotinas solicitadas foram processadas!")

    except Exception as e:
        print(f"\n❌ OCORREU UM ERRO NO FLUXO DE ROTINAS: {e}")

    finally:
        print("\n" + "="*50)
        print("👋 Fechando navegador e limpando sessão...")
        driver.quit()
        subir_github()
