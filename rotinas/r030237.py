import time
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def executar(driver, wait, data_inicio, data_fim, janela_menu):
    """Lógica específica da rotina 01200147"""
    
    # IMPORTANTE: Definimos o código da rotina aqui dentro ou usamos o que o orquestrador sabe
    codigo_rotina = "030237" 

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

        print("🎯 Selecionando 'Quebra 1' no dropdown...")
        dropdown_element = wait.until(EC.presence_of_element_located((By.NAME, "quebra1")))
        
        driver.execute_script("""
            var select = arguments[0];
            var textoParaSelecionar = "Operacao";
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

        dropdown_element = wait.until(EC.presence_of_element_located((By.NAME, "quebra2")))
        
        driver.execute_script("""
            var select = arguments[0];
            var textoParaSelecionar = "Vendedor";
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

        dropdown_element = wait.until(EC.presence_of_element_located((By.NAME, "quebra3")))
        
        driver.execute_script("""
            var select = arguments[0];
            var textoParaSelecionar = "Motorista";
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

        campo_ini = wait.until(EC.presence_of_element_located((By.NAME, "dataInicial")))
        driver.execute_script("arguments[0].value = arguments[1];", campo_ini, data_inicio)
        
        campo_fim = wait.until(EC.presence_of_element_located((By.NAME, "dataFinal")))
        driver.execute_script("arguments[0].value = arguments[1];", campo_fim, data_fim)
        """
        statusNota = wait.until(EC.presence_of_element_located((By.NAME, "statusNota")))
        driver.execute_script("arguments[0].scrollIntoView(true);", statusNota)
        statusNota.click()
        """
        itens = wait.until(EC.presence_of_element_located((By.NAME, "itens")))
        driver.execute_script("arguments[0].scrollIntoView(true);", itens)
        itens.click()

        # --- 4. GERAÇÃO E DOWNLOAD ---
        print("🖱️ Clicando em Visualizar...")
        try:
            btn_v = wait.until(EC.element_to_be_clickable((By.NAME, "BotVisualizar")))
            driver.execute_script("arguments[0].click();", btn_v)
        except:
            btn_v = driver.find_element(By.XPATH, "//button[contains(., 'Visualizar')]")
            driver.execute_script("arguments[0].click();", btn_v)

        print("🚀 Relatório solicitado! Aguardando botão CSV...")
        time.sleep(10)
        
        # 5. Clica no botão CSV (GerExecl)
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
        driver.close() # Fecha a janela atual (o relatório)
        driver.switch_to.window(janela_menu) # Volta para a janela do menu
            
    except Exception as e:
        print(f"❌ Erro na rotina {codigo_rotina}: {e}")
        # Não damos driver.quit() aqui para não matar o processo das outras rotinas