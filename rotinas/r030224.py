import time
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def executar(driver, wait, data_inicio, data_fim):
    """Lógica específica da rotina 030224"""
    
    # IMPORTANTE: Definimos o código da rotina aqui dentro ou usamos o que o orquestrador sabe
    codigo_rotina = "030224" 

    try:
        # 1. Inserir rotina
        print("Retornando ao frame de comandos...")
        driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))
        
        print("📂 Entrando no IframeMenu...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameMenu")))
        
        print(f"⌨️ Inserindo a rotina: {codigo_rotina}")
        botao_rotina = wait.until(EC.visibility_of_element_located((By.ID, "atalho")))
        botao_rotina.clear()
        botao_rotina.send_keys(codigo_rotina)

        # Botão OK da rotina
        botao_ok = driver.find_element(By.XPATH, '//*[@id="atal"]/div[1]/table/tbody/tr[2]/td/input[2]')
        botao_ok.click()

        print("⏳ Aguardando carregamento da rotina...")
        driver.switch_to.default_content()

        # 2. Gestão de Janelas
        janela_principal = driver.current_window_handle
        wait.until(EC.number_of_windows_to_be(2)) 
        janelas = driver.window_handles

        for janela in janelas:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                time.sleep(1) 
                print(f"🔀 Mudamos para a nova janela: {driver.title}")
                break

        # 3. Preenchimento dos Campos
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "rotina")))

        print("🎯 Selecionando 'Mapa' no dropdown...")
        dropdown_element = wait.until(EC.presence_of_element_located((By.NAME, "opcaoRel")))
        
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

        # Clicar nos Checkboxes específicos desta rotina
        print("🔘 Marcando opções do relatório...")
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'checkAs')] | //input[@type='checkbox'][1]"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'respProc')] | //input[@type='checkbox'][2]"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'todasOperacoes')] | //input[@type='checkbox'][3]"))).click()

        # 4. Preencher Datas
        print("📅 Preenchendo datas...")
        campo_data_ini = wait.until(EC.presence_of_element_located((By.NAME, "dataInicial")))
        driver.execute_script("arguments[0].value = arguments[1];", campo_data_ini, data_inicio)
        
        campo_data_fim = wait.until(EC.presence_of_element_located((By.NAME, "dataFinal")))
        driver.execute_script("arguments[0].value = arguments[1];", campo_data_fim, data_fim)

        # 5. Visualizar e Download
        print("🖱️ Clicando em Visualizar...")
        btn_visualizar = wait.until(EC.element_to_be_clickable((By.NAME, "BotVisualizar")))
        driver.execute_script("arguments[0].click();", btn_visualizar)

        print("🚀 Relatório solicitado! Aguardando CSV...")
        time.sleep(10)
        
        # Clica no botão CSV (GerExecl)
        botaoCsv = driver.find_element(By.NAME, "GerExecl")
        botaoCsv.click()

        # 6. Salvar via PyAutoGUI
        print("⌨️ Acionando comandos de teclado para salvar...")
        time.sleep(4) 
        pyautogui.hotkey('alt', 'n')
        time.sleep(1)
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('enter')
        
        print(f"✅ Rotina {codigo_rotina} finalizada!")

    except Exception as e:
        print(f"❌ Erro na rotina {codigo_rotina}: {e}")
        # Não damos driver.quit() aqui para não matar o processo das outras rotinas