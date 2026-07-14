import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

from configs import obter_config_ie

# --- Variáveis Globais ---
login = "pizolitto"
senha = "Nerd12lol!"

def capturar_tela_senha():
    print("\n" + "="*50)
    print("🚀 INICIANDO SCRIPT DE CAPTURA DA TELA DE SENHA")
    print("="*50)

    service, options = obter_config_ie()
    
    print("🌐 Abrindo navegador Internet Explorer...")
    driver = webdriver.Ie(service=service, options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 30)

    try:
        print("📥 Acessando a URL do sistema...")
        driver.get("https://revalle.promaxcloud.com.br/pw/")
        janela_principal = driver.current_window_handle

        # --- Etapa: Login ---
        print("🔑 Identificando frames e preenchendo credenciais...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "frame")))

        wait.until(EC.presence_of_element_located((By.NAME, "Usuario")))
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
        
        # Volta para o contexto raiz
        driver.switch_to.default_content()

        # --- Etapa: Lidar com o Popup e Nova Janela ---
        print("⏳ Aguardando o popup de alteração de senha...")
        
        # Tenta lidar com um alert javascript se houver
        try:
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alerta = driver.switch_to.alert
            print(f"🚨 Alerta detectado: '{alerta.text}'")
            alerta.accept()
            print("✅ Alerta fechado!")
        except TimeoutException:
            print("Nenhum alerta Javascript detectado. Verificando janelas...")

        print("⏳ Aguardando a abertura da nova janela de alteração de senha...")
        
        # Espera que o número de janelas seja pelo menos 2
        wait.until(lambda d: len(d.window_handles) > 1)
        
        for janela in driver.window_handles:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                time.sleep(2) # Aguarda renderizar o HTML da nova janela
                print(f"🔀 Focado na nova janela: {driver.title}")
                
                # Gera e salva o HTML da página atual
                html_code = driver.page_source
                caminho_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html_tela_senha_capturado.html")
                
                with open(caminho_arquivo, "w", encoding="utf-8") as f:
                    f.write(html_code)
                print(f"💾 HTML da tela de alteração de senha salvo com sucesso em:\n{caminho_arquivo}")
                break

    except Exception as e:
        print(f"❌ Ocorreu um erro no processo: {e}")
    finally:
        print("\n" + "="*50)
        print("👋 Fechando navegador e limpando sessão...")
        # Pode comentar o driver.quit() se quiser ver a tela aberta
        driver.quit()

if __name__ == "__main__":
    capturar_tela_senha()
