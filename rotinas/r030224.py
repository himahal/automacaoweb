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
        # ====================================================================
        # FASE 1: SETUP E ABERTURA DA JANELA (Roda apenas UMA vez)
        # ====================================================================

        print(f"⌨️ Inserindo a rotina: {codigo_rotina}")
        print("Procurando campo atalho...")

        # 1. Aguarda o campo da rotina carregar na tela
        wait.until(EC.presence_of_element_located((By.ID, "call")))

        # 2. Localiza o campo, limpa e digita o código
        campo_rotina = driver.find_element(By.ID, "call")
        campo_rotina.send_keys(Keys.CONTROL + "a")
        campo_rotina.send_keys(Keys.DELETE)
        campo_rotina.send_keys("031120")

        # 3. Localiza e clica no botão "Acessar Rotina"
        driver.find_element(By.ID, "BotAcessar").click()

        print("⏳ Aguardando carregamento da rotina...")
        driver.switch_to.default_content()

        # ====================================================================
        # TRECHO ISOLADO: Lógica de Janelas Secundárias e Loop de Revendas
        # ====================================================================
        """
        # Muda para a nova janela da rotina
        janela_principal = driver.current_window_handle
        wait.until(EC.number_of_windows_to_be(2))
        janelas = driver.window_handles

        for janela in janelas:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                time.sleep(1)
                
                # Foco via pywinauto...
                try:
                    from pywinauto import Application
                    titulo_seguro = re.escape(driver.title)
                    app = Application(backend="win32").connect(title_re=f".*{titulo_seguro}.*", timeout=5)
                    app.window(title_re=f".*{titulo_seguro}.*").set_focus()
                except Exception:
                    pass
                break

        # LOOP DE UNIDADES
        for indice, unidade in enumerate(lista_unidades):
            fechar_popups(driver, 4)
            driver.switch_to.default_content()
            
            from rotinas.utils_ui import mudar_revenda_com_fallback
            mudar_revenda_com_fallback(driver, wait, indice)
            
            try:
                WebDriverWait(driver, 15).until(EC.alert_is_present())
                fechar_popups(driver, 6)
            except Exception:
                pass
            time.sleep(3)
        """

        # ====================================================================
        # FASE 2: PREENCHIMENTO E DOWNLOAD (Fora do loop para o mock)
        # ====================================================================
        print("🎯 Sincronizando com a janela da rotina...")
        driver.switch_to.default_content()

        # Resiliência de Ambiente (Portfólio vs Produção)
        try:
            WebDriverWait(driver, 3).until(
                EC.frame_to_be_available_and_switch_to_it((By.NAME, "rotina"))
            )
        except:
            print("⚠️ Frame 'rotina' não encontrado (Ambiente local). Operando na raiz.")

        '''
        print("🎯 Selecionando 'Mapa' no dropdown...")
        dropdown_element = wait.until(EC.presence_of_element_located((By.NAME, "opcaoRel")))
        from rotinas.utils_ui import selecionar_dropdown_pyautogui
        selecionar_dropdown_pyautogui(driver, dropdown_element, "Mapa")

        checks = ["selecionouAS", "responsabProcesso", "todasOperacoes"]
        for check in checks:
            el = wait.until(EC.presence_of_element_located((By.NAME, check)))
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            el.click()
        '''

        # Preencher Datas
        print("📅 Preenchendo datas...")
        campo_data_ini = wait.until(
            EC.presence_of_element_located((By.NAME, "dataInicial")))
        driver.execute_script(
            "arguments[0].value = arguments[1];", campo_data_ini, data_inicio)

        campo_data_fim = wait.until(
            EC.presence_of_element_located((By.NAME, "dataFinal")))
        driver.execute_script(
            "arguments[0].value = arguments[1];", campo_data_fim, data_fim)

        # Geração de Relatório
        print("🖱️ Clicando em Visualizar...")
        try:
            btn_v = wait.until(EC.element_to_be_clickable(
                (By.NAME, "BotVisualizar")))
            driver.execute_script("arguments[0].click();", btn_v)
        except:
            btn_v = driver.find_element(
                By.XPATH, "//button[contains(., 'Visualizar')]")
            driver.execute_script("arguments[0].click();", btn_v)
        """
        # Validação do Arquivo
        from rotinas.utils_ui import confirmar_download_ie
        confirmar_download_ie(driver)

        dia, mes, ano = data_fim.split("/")

        # Pega a primeira unidade da lista apenas para dar nome ao arquivo falso
        unidade_mock = lista_unidades[0] if lista_unidades else "unidade_padrao"
        nome_dinamico = f"{unidade_mock}.{mes}.{ano}"
        print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")

        # Caminho oculto no Github
        diretorio_saida = os.getenv("CAMINHO_RELATORIOS_SAIDA", "./downloads")

        rotinas.tratar_arquivo_baixado(
            prefixo_arquivo="03.02.24",
            nome_personalizado=nome_dinamico,
            caminho_destino=diretorio_saida
        )
        """
        print("✅ Fluxo de demonstração concluído com sucesso!")

    except Exception as e:
        print(f"❌ Erro fatal na rotina {codigo_rotina}: {e}")
