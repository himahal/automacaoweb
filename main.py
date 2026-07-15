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

# ====================================================================
# 🛡️ INTERCEPTADOR DE LOGS (Salva tudo no terminal e no arquivo)
# ====================================================================


class InterceptadorLog:
    def __init__(self, caminho_arquivo):
        self.terminal = sys.stdout
        self.arquivo_log = open(caminho_arquivo, "a", encoding="utf-8")

    def write(self, mensagem):
        # Escreve no terminal (para você ver rodando)
        self.terminal.write(mensagem)
        # Escreve no arquivo txt
        self.arquivo_log.write(mensagem)
        # Força o salvamento imediato no disco rígido
        self.arquivo_log.flush()

    def flush(self):
        self.terminal.flush()
        self.arquivo_log.flush()


# Cria uma pasta chamada 'logs_v2' no mesmo local do main.py (se não existir)
pasta_logs = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "logs_v2")
os.makedirs(pasta_logs, exist_ok=True)

# Gera um nome de arquivo único com a data e hora atual
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nome_arquivo_log = os.path.join(pasta_logs, f"execucao_{timestamp}.log")

# Aplica a interceptação no sistema
logger = InterceptadorLog(nome_arquivo_log)
sys.stdout = logger  # Captura todos os seus 'prints'
sys.stderr = logger

# --- Variáveis Globais ---
login = "pizolitto"
senha = "Tatucac1!"


def limpar_processos_antigos():
    """Fecha processos órfãos do IEDriverServer e iexplore para evitar travamento na inicialização"""
    import subprocess
    print("🧹 Limpando processos antigos (IEDriverServer e Internet Explorer) do Windows...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "IEDriverServer.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/F", "/IM", "iexplore.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def login_e_menu():
    """Realiza o acesso inicial, login e limpeza de alertas do Promax"""
    print("\n" + "="*50)
    print("🚀 INICIANDO PROCESSO DE LOGIN PROMAX")
    print("="*50)

    # Limpa possíveis travamentos de instâncias antigas
    limpar_processos_antigos()

    configurar_pasta_download()
    service, options = obter_config_ie()

    print("🌐 Abrindo navegador Internet Explorer...")
    driver = webdriver.Ie(service=service, options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 1000)

    print("📥 Acessando a URL do sistema...")
    driver.get("https://revalle.promaxcloud.com.br/pw/")

    # --- Etapa: Login ---
    print("🔑 Identificando frames e preenchendo credenciais...")
    wait.until(EC.frame_to_be_available_and_switch_to_it(
        (By.TAG_NAME, "frame")))

    wait.until(EC.presence_of_element_located(
        (By.NAME, "Usuario")))
    loginI = driver.find_element(By.NAME, "Usuario")
    loginI.send_keys(Keys.CONTROL + "a")
    loginI.send_keys(Keys.DELETE)
    loginI.send_keys(login)
    senhaI = driver.find_element(By.NAME, "Senha")
    senhaI.send_keys(Keys.CONTROL + "a")
    senhaI.send_keys(Keys.DELETE)
    senhaI.send_keys(senha)
    driver.find_element(By.ID, "BtnConfirm").click()

    print("✅ Login efetuado com sucesso!")

    try:
        # Espera BEM CURTA (ex: 3 segundos) para não atrasar o dia a dia
        # Substitua "ID_DO_POPUP" por algum elemento que só existe nessa tela de senha
        tela_senha = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.ID, "algum_id_da_tela_de_senha"))
        )

        print("⚠️ Aviso: Tela de alteração de senha detectada!")

        # Salva o HTML para você estudar depois
        html_senha = driver.page_source
        with open("html_tela_senha.html", "w", encoding="utf-8") as f:
            f.write(html_senha)
        print("💾 HTML da tela de senha salvo como 'html_tela_senha.html'.")

    # TODO: Fechar o popup ou clicar em "Lembrar mais tarde"
    # botao_fechar = driver.find_element(By.ID, "id_do_botao_fechar")
    # botao_fechar.click()

    except Exception:
        # Se der erro por timeout (3s), significa que o popup não apareceu. Vida que segue!
        print("✅ Nenhum aviso de senha. Seguindo para o sistema...")

    # --- Etapa: Unidade/Revenda ---
    driver.switch_to.default_content()
    print("🏢 Selecionando unidade de revenda...")
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))
    driver.find_element(By.NAME, "cmdConfirma").click()
    print("📍 Unidade confirmada!")

    # --- Etapa: Limpeza de Terreno ---
    print("🧹 Chamando assistente para fechar pop-ups...")
    fechar_popups(driver, 5)
    print("✨ Varredura de alertas concluída.")

    return driver, wait


def subir_github():
    try:
        resposta = input(
            "\nDeseja subir as execuções/relatórios para o GitHub? (s/n): ").strip().lower()
        if resposta == 's':
            print("📦 Preparando arquivos para o commit...")
            import subprocess
            subprocess.run(["git", "add", "."], check=True)

            commit_msg = f"Execucao automatica das rotinas - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)

            print("🚀 Enviando para o GitHub (branch atual)...")
            subprocess.run(["git", "push"], check=True)

            print("✅ Atualização enviada com sucesso!")
        else:
            print("👍 Operação ignorada. Nada foi enviado para o GitHub.")
    except Exception as e:
        print(f"❌ Erro ao tentar subir para o GitHub: {e}")


if __name__ == "__main__":
    # 1. Executa o fluxo de entrada
    driver, wait = login_e_menu()

    try:
        print("\n" + "-"*50)
        print("🎯 INICIANDO EXECUÇÃO DAS ROTINAS")
        print("-"*50)

        # 🚀 CHAMADA DAS ROTINAS

        rotinas.chamar_rotina(driver, wait, "031120")
        rotinas.chamar_rotina(driver, wait, "030224")
        rotinas.chamar_rotina(driver, wait, "01200147")
        rotinas.chamar_rotina(driver, wait, "0105070402")
        rotinas.chamar_rotina(driver, wait, "03014701")
        rotinas.chamar_rotina(driver, wait, "030237")

        print("\n🏆 Todas as rotinas solicitadas foram processadas!")

    except Exception as e:
        print(f"\n❌ OCORREU UM ERRO NO FLUXO DE ROTINAS: {e}")

    finally:
        print("\n" + "="*50)
        print("👋 Fechando navegador e limpando sessão...")
        driver.quit()
        subir_github()
