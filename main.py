from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Importação de módulos personalizados
from configs import obter_config_ie, configurar_pasta_download
from fecharPopups import fechar_popups
from rotinas import rotinas  # 🚀 Orquestrador liberado!

# --- Variáveis Globais ---
login = "pizolitto"
senha = "Nerd12lol!"


def login_e_menu():
    """Realiza o acesso inicial, login e limpeza de alertas do Promax"""
    print("\n" + "="*50)
    print("🚀 INICIANDO PROCESSO DE LOGIN PROMAX")
    print("="*50)

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


if __name__ == "__main__":
    # 1. Executa o fluxo de entrada
    driver, wait = login_e_menu()

    try:
        print("\n" + "-"*50)
        print("🎯 INICIANDO EXECUÇÃO DAS ROTINAS")
        print("-"*50)

        # 🚀 CHAMADA DAS ROTINAS

        # rotinas.chamar_rotina(driver, wait, "031120", revendas)
        rotinas.chamar_rotina(driver, wait, "030224", revendas)  # está tudo ok
        # rotinas.chamar_rotina(driver, wait, "01200147", revendas)
        # rotinas.chamar_rotina(driver, wait, "03014701", revendas)
        # rotinas.chamar_rotina(driver, wait, "030237", revendas)

        print("\n🏆 Todas as rotinas solicitadas foram processadas!")

    except Exception as e:
        print(f"\n❌ OCORREU UM ERRO NO FLUXO DE ROTINAS: {e}")

    finally:
        print("\n" + "="*50)
        input("🏁 Automação finalizada. Pressione [ENTER] para sair...")
        print("👋 Fechando navegador e limpando sessão...")
        driver.quit()
