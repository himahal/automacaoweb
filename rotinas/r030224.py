from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException

from fecharPopups import fechar_popups
from . import rotinas


def executar(driver, wait, data_inicio, data_fim, janela_menu, lista_unidades):
    """Lógica específica da rotina 030224"""

    codigo_rotina = "030224"
    try:
        print(f"⌨️ Inserindo a rotina: {codigo_rotina}")
        print("Procurando campo atalho...")

        wait.until(EC.presence_of_element_located((By.ID, "call")))

        campo_rotina = driver.find_element(By.ID, "call")
        campo_rotina.send_keys(Keys.CONTROL + "a")
        campo_rotina.send_keys(Keys.DELETE)
        campo_rotina.send_keys("030224")

        driver.find_element(By.ID, "BotAcessar").click()

        print("⏳ Aguardando carregamento da rotina...")
        driver.switch_to.default_content()

        print("🎯 Sincronizando com a janela da rotina...")
        driver.switch_to.default_content()

        try:
            WebDriverWait(driver, 3).until(
                EC.frame_to_be_available_and_switch_to_it((By.NAME, "rotina"))
            )
        except:
            print("⚠️ Frame 'rotina' não encontrado (Ambiente local). Operando na raiz.")

        print("📅 Preenchendo datas...")
        campo_data_ini = wait.until(
            EC.presence_of_element_located((By.NAME, "dataInicial")))
        driver.execute_script(
            "arguments[0].value = arguments[1];", campo_data_ini, data_inicio)

        campo_data_fim = wait.until(
            EC.presence_of_element_located((By.NAME, "dataFinal")))
        driver.execute_script(
            "arguments[0].value = arguments[1];", campo_data_fim, data_fim)

        print("🖱️ Clicando em Visualizar...")
        try:
            btn_v = wait.until(EC.element_to_be_clickable(
                (By.NAME, "BotVisualizar")))
            driver.execute_script("arguments[0].click();", btn_v)
        except:
            btn_v = driver.find_element(
                By.XPATH, "//button[contains(., 'Visualizar')]")
            driver.execute_script("arguments[0].click();", btn_v)

        print("✅ Fluxo concluído com sucesso!")

    except Exception as e:
        print(f"❌ Erro na rotina {codigo_rotina}: {e}")
