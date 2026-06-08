import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException

from fecharPopups import fechar_popups
from . import rotinas


def executar(driver, wait, data_inicio, data_fim, janela_menu, revenda, indice):
    """Lógica específica da rotina 030224"""

    # IMPORTANTE: Definimos o código da rotina aqui dentro ou usamos o que o orquestrador sabe
    codigo_rotina = "030224"

    try:
        # ----------- 1. Inserindo a rotina ----------------

        print("Retornando ao frame de comandos...")
        driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))

        print("📂 Entrando no IframeMenu...")
        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.ID, "iFrameMenu")))

        print(f"⌨️ Inserindo a rotina: {codigo_rotina}")
        print("Procurando campo atalho...")

        botao_rotina = driver.find_element(By.ID, "atalho")
        botao_rotina.clear()
        botao_rotina.send_keys(codigo_rotina)
        botao_ok = driver.find_element(
            By.XPATH, '//*[@id="atal"]/div[1]/table/tbody/tr[2]/td/input[2]')
        botao_ok.click()

        print("⏳ Aguardando carregamento da rotina...")
        driver.switch_to.default_content()

        # ----------- 2. Mudando para a janela da rotina----------------
        janela_principal = driver.current_window_handle
        wait.until(EC.number_of_windows_to_be(2))
        janelas = driver.window_handles

        for janela in janelas:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                time.sleep(1)
                print(f"🔀 Mudamos para a nova janela: {driver.title}")
                break

        print("📍 DEBUG 1: Resetando para a raiz da página (default_content)...")
        driver.switch_to.default_content()
        time.sleep(2)  # Respiro vital para o IE estabilizar a nova janela

        print(f"🔄 Ajustando a filial via Selenium para: {revenda}")

        # --- TENTATIVA DE ENTRAR NO FRAME ---
        print("📍 DEBUG 2: Tentando entrar no frame superior...")
        try:
            # Atenção: Troquei de "top" para "top_rotina" baseado no seu HTML antigo!
            wait.until(EC.frame_to_be_available_and_switch_to_it(
                (By.NAME, "top_rotina")))
            print("📍 DEBUG 3: Sucesso! Entrou no frame superior.")
        except Exception as e:
            print(
                f"❌ ERRO FATAL: Não encontrou o frame superior. Detalhes: {e}")
            # Se der erro aqui, nem adianta tentar o XPath abaixo

        # --- TENTATIVA DO XPATH ---
        print("📍 DEBUG 4: Localizando o dropdown para enviar comandos de teclado...")
        try:
            # Pula direto para o dropdown (Adeus, 29 TABs!)
            select_principal = wait.until(
                EC.presence_of_element_located((By.NAME, "unidade")))

            # 1. Dá o "foco" e joga a seleção para a primeira opção da lista (Beira Rio)
            select_principal.send_keys(Keys.HOME)
            time.sleep(0.5)  # Respiro para o IE mudar a seleção visualmente

            # 2. Desce a quantidade de vezes exata usando o índice
            if indice > 0:
                print(
                    f"⬇️ Descendo {indice} posições via teclado do Selenium...")
                for _ in range(indice):
                    select_principal.send_keys(Keys.DOWN)
                    time.sleep(0.1)

            # 3. Dispara o Enter para o Promax entender que escolhemos a revenda e recarregar
            select_principal.send_keys(Keys.ENTER)
            print("✅ Dropdown alterado via Selenium (Modo Teclado)!")

        except UnexpectedAlertPresentException:
            # Mantemos nosso caça-alertas aqui por segurança!
            print("⚠️ Alerta do sistema detectado. Fechando...")
            try:
                alerta = driver.switch_to.alert
                alerta.accept()
            except NoAlertPresentException:
                pass
        except Exception as e:
            print(f"⚠️ Erro ao tentar navegar no dropdown: {e}")

        # --- 2. LIDA COM OS POP-UPS (O Pedágio) ---
        print("⏳ Aguardando e fechando pop-ups de carregamento...")
        time.sleep(3)
        fechar_popups(driver, 4)

        # ----------- 3. Preenchimento de campos ----------------

        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.NAME, "rotina")))

        print("🎯 Selecionando 'Mapa' no dropdown...")
        dropdown_element = wait.until(
            EC.presence_of_element_located((By.NAME, "opcaoRel")))

        driver.execute_script("""
            var select = arguments[0];
            var textoParaSelecionar = "Mapa";
            for (var i = 0; i < select.options.length; i++) {
                var textoOption = select.options[i].text.replace(/^\s+|\s+$/g, '');
                if (textoOption === textoParaSelecionar) {
                    select.selectedIndex = i;
                    if ("createEvent" in document) {
                        var evt = document.createEvent("HTMLEvents");
                        evt.initEvent("change", false, true);
                        select.dispatchEvent(evt);
                    } else if ("fireEvent" in select) {
                        select.fireEvent("onchange");
                    }
                    break;
                }
            }
        """, dropdown_element)

        # Checkboxes (Usando Scroll antes de clicar)
        checks = ["selecionouAS", "responsabProcesso", "todasOperacoes"]
        for check in checks:
            el = wait.until(EC.presence_of_element_located((By.NAME, check)))
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            el.click()

        # 4. Preencher Datas
        print("📅 Preenchendo datas...")
        campo_data_ini = wait.until(
            EC.presence_of_element_located((By.NAME, "dataInicial")))
        driver.execute_script(
            "arguments[0].value = arguments[1];", campo_data_ini, data_inicio)

        campo_data_fim = wait.until(
            EC.presence_of_element_located((By.NAME, "dataFinal")))
        driver.execute_script(
            "arguments[0].value = arguments[1];", campo_data_fim, data_fim)

        # --- 5. GERAÇÃO E DOWNLOAD ---
        print("🖱️ Clicando em Visualizar...")
        try:
            btn_v = wait.until(EC.element_to_be_clickable(
                (By.NAME, "BotVisualizar")))
            driver.execute_script("arguments[0].click();", btn_v)
        except:
            btn_v = driver.find_element(
                By.XPATH, "//button[contains(., 'Visualizar')]")
            driver.execute_script("arguments[0].click();", btn_v)

        time.sleep(15)  # Espera 1s para o overlay ser criado no HTML
        rotinas.matar_overlay_processando(driver)

        print("🚀 Relatório solicitado! Aguardando botão CSV...")
        # 5. Clica no botão CSV (GerExecl)
        botaoCsv = wait.until(
            EC.presence_of_element_located((By.NAME, "GerExecl")))
        botaoCsv.click()

        # 6. Salvar via PyAutoGUI
        print("⌨️ Acionando comandos de teclado para salvar...")
        time.sleep(4)
        pyautogui.hotkey('alt', 'n')
        time.sleep(1)
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.hotkey('alt', 'n')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('enter')
        time.sleep(2)

        dia, mes, ano = data_fim.split("/")
        # 👇 Agora o nome será dinâmico de verdade!
        nome_dinamico = f"{revenda}.{mes}.{ano}"

        print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")
        rotinas.tratar_arquivo_baixado(
            prefixo_arquivo="03.02.24",  # 👇 Ajuste para o prefixo correto desta rotina
            nome_personalizado=nome_dinamico,
            caminho_destino=r"C:\Users\usuario\Desktop\Promax\promax\downloads"
        )

    except Exception as e:
        print(f"❌ Erro na rotina {codigo_rotina}: {e}")

