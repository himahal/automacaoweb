import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# imnportar aqruivos
from configlinux import obter_config_chrome
from fecharPopups import fechar_popups

login = "pizolitto"
senha = "Nerd12lol"
rotina = "01.20.01.47"

def realizar_automacao():
    # Carrega as configurações do motor
    service, options = obter_config_chrome()

    try:
        print("🚀 Iniciando motor Selenium (Python 3.12)...")
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 20)

        print("🌐 Acessando Revalle/Promax...")
        driver.get("https://revalle.promaxcloud.com.br/pw/")

        # LÓGICA DE LOGIN
        print("📥 Entrando no frame de login...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "frame")))

        #Tela de login
        print("🔑 Preenchendo login para 'pizolitto'...")
        wait.until(EC.presence_of_element_located((By.NAME, "Usuario"))).send_keys(login)
        driver.find_element(By.NAME, "Senha").send_keys(senha)
        driver.find_element(By.ID, "BtnConfirm").click()

        print("✅ Login efetuado! Voltando ao contexto principal...")
        driver.switch_to.default_content()

        #Selecionar a revenda e confirmar
        print("Mudando para o segundo frame!")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))
        print("✅ Frame alterado!")
        botao_confirma = wait.until(EC.element_to_be_clickable((By.NAME, "cmdConfirma")))
        botao_confirma.click()

        #Fechar PopUps

        fechar_popups(driver, max_popups_to_check=4)
        driver.switch_to.default_content()

        #Inserir rotina
        print("Mudando para o segundo frame!")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))
        print("✅ Frame alterado!")
        print("📂 Entrando no IframeMenu...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameMenu")))
        print(f"⌨️ Inserindo a rotina: {rotina}")
        botao_rotina = wait.until(EC.presence_of_element_located((By.ID, "atalho")))
        botao_rotina.clear()
        botao_rotina.send_keys(rotina)

        botao_ok = driver.find_element(By.XPATH, '//*[@id="atal"]/div[1]/table/tbody/tr[2]/td/input[2]')
        botao_ok.click()

        input("\n[Pressione ENTER para encerrar o bot]")

    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()


if __name__ == "__main__":
    realizar_automacao()