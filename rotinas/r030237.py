import time
import pyautogui
import re
from pywinauto import Desktop
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from . import rotinas
from fecharPopups import fechar_popups


def executar(driver, wait, data_inicio, data_fim, janela_menu, lista_revendas):
    """Lógica específica da rotina 030237"""

    codigo_rotina = "030237"
    revendas_com_alerta = []

    try:
        # ====================================================================
        # FASE 1: SETUP E ABERTURA DA JANELA (Roda apenas UMA vez)
        # ====================================================================
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
        driver.execute_script("arguments[0].click();", botao_ok)

        print("⏳ Aguardando carregamento da rotina...")
        driver.switch_to.default_content()

        # Muda para a nova janela da rotina
        janela_principal = driver.current_window_handle
        wait.until(EC.number_of_windows_to_be(2))
        janelas = driver.window_handles

        for janela in janelas:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                time.sleep(1)
                print(f"🔀 Mudamos para a nova janela: {driver.title}")
                
                # Garante o foco físico na nova janela da rotina via win32
                try:
                    from pywinauto import Application
                    import re
                    titulo_seguro = re.escape(driver.title)
                    app = Application(backend="win32").connect(title_re=f".*{titulo_seguro}.*", timeout=5)
                    app.window(title_re=f".*{titulo_seguro}.*").set_focus()
                    print("🎯 Foco da nova janela da rotina restaurado via win32!")
                except Exception as e_foco:
                    print(f"⚠️ Erro ao focar na nova janela da rotina: {e_foco}")
                break

        # ====================================================================
        # FASE 2: O LOOP DE REVENDAS
        # ====================================================================
        for indice, revenda in enumerate(lista_revendas):
            print(f"\n{'='*40}")
            print(
                f"🔄 PROCESSANDO FILIAL [{indice + 1}/{len(lista_revendas)}]: {revenda}")
            print(f"{'='*40}")

            try:
                # 🛡️ O ESCUDO INICIAL
                print("🧹 Limpando alertas iniciais antes de interagir com a tela...")
                fechar_popups(driver, 4)

                print("📍 DEBUG 1: Resetando para a raiz da página (default_content)...")
                driver.switch_to.default_content()
                time.sleep(2)

                from rotinas.utils_ui import mudar_revenda_com_fallback
                mudar_revenda_com_fallback(driver, wait, indice)

                # --- 2.2 LIDA COM OS POP-UPS DA TROCA ---
                print("⏳ Aguardando e fechando pop-ups de carregamento da troca...")
                try:
                    WebDriverWait(driver, 10).until(EC.alert_is_present())
                    print(
                        "🚨 Primeiro alerta detectado pelo Guarda-Costas! Iniciando limpeza...")
                    fechar_popups(driver, 4)
                except Exception:
                    print(
                        "✅ Nenhum alerta detectado nos últimos 10 segundos. Seguindo o fluxo...")
                time.sleep(3) # Aguarda o frame rotina atualizar após a troca de revenda


                # --- 2.3 PREENCHIMENTO DE CAMPOS (Específico da 030237) ---
                driver.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it(
                    (By.NAME, "rotina")))

                print("🎯 Preenchendo campos específicos da rotina...")

                # Quebra 1
                try:
                    dropdown_element_1 = wait.until(
                        EC.presence_of_element_located((By.NAME, "quebra1")))
                except Exception:
                    print("⚠️ Demora na atualização do frame. Tentando novamente...")
                    driver.switch_to.default_content()
                    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "rotina")))
                    dropdown_element_1 = wait.until(EC.presence_of_element_located((By.NAME, "quebra1")))
                from rotinas.utils_ui import selecionar_dropdown_pyautogui

                selecionar_dropdown_pyautogui(driver, dropdown_element_1, "Operacao")

                # Quebra 2
                dropdown_element_2 = wait.until(
                    EC.presence_of_element_located((By.NAME, "quebra2")))
                from rotinas.utils_ui import selecionar_dropdown_pyautogui

                selecionar_dropdown_pyautogui(driver, dropdown_element_2, "Vendedor")

                # Quebra 3
                dropdown_element_3 = wait.until(
                    EC.presence_of_element_located((By.NAME, "quebra3")))
                from rotinas.utils_ui import selecionar_dropdown_pyautogui

                selecionar_dropdown_pyautogui(driver, dropdown_element_3, "Motorista")

                campo_ini = wait.until(
                    EC.presence_of_element_located((By.NAME, "dataInicial")))
                driver.execute_script(
                    "arguments[0].value = arguments[1];", campo_ini, data_inicio)

                campo_fim = wait.until(
                    EC.presence_of_element_located((By.NAME, "dataFinal")))
                driver.execute_script(
                    "arguments[0].value = arguments[1];", campo_fim, data_fim)

                itens = wait.until(
                    EC.presence_of_element_located((By.NAME, "itens")))
                driver.execute_script(
                    "arguments[0].scrollIntoView(true);", itens)
                itens.click()

                # --- 2.4 GERAÇÃO E DOWNLOAD ---
                print("🖱️ Clicando em Visualizar...")
                try:
                    btn_v = wait.until(EC.element_to_be_clickable(
                        (By.NAME, "BotVisualizar")))
                    driver.execute_script("arguments[0].click();", btn_v)
                except:
                    btn_v = driver.find_element(
                        By.XPATH, "//button[contains(., 'Visualizar')]")
                    driver.execute_script("arguments[0].click();", btn_v)

                # ==========================================================
                # CAPTURA DE ALERTA APÓS VISUALIZAR (ESPERA INTELIGENTE)
                # ==========================================================
                import pygetwindow as gw
                import time
                tem_aviso = False
                inicio_espera = time.time()
                timeout_alerta = 30  # Espera até 30 segundos
                
                print(f"⏳ Aguardando até {timeout_alerta}s para verificar se há alerta...")
                while time.time() - inicio_espera < timeout_alerta:
                    try:
                        alert = driver.switch_to.alert
                        print(f"⚠️ Aviso detectado: {alert.text}")
                        alert.accept()
                        revendas_com_alerta.append(revenda)
                        tem_aviso = True
                        break
                    except Exception:
                        pass
                    
                    # Se começou a processar, não terá alerta
                    try:
                        janelas = gw.getWindowsWithTitle('Processando')
                        if any(j for j in janelas if "edge" not in j.title.lower() or j.width < 600):
                            print("✅ Janela 'Processando' detectada. O relatório está sendo gerado (sem alerta).")
                            break
                    except Exception:
                        pass
                    
                    # Se o botão já apareceu, também é sucesso
                    try:
                        if driver.find_elements(By.NAME, "GerExecl"):
                            break
                    except Exception:
                        pass
                        
                    time.sleep(1)

                if tem_aviso:
                    print(f"⏭️ Pulando geração de CSV para a revenda {revenda} devido ao aviso.")
                    continue

                print("🚀 Relatório solicitado! Aguardando processamento e botão CSV...")
                # 5. Clica no botão CSV (GerExecl) com espera ativa do Processando
                botaoCsv = rotinas.aguardar_processamento_e_botao(driver, wait, By.NAME, "GerExecl", timeout_segundos=300)
                driver.execute_script("arguments[0].click();", botaoCsv)

                # --- CONFIRMAÇÃO DO DOWNLOAD (Nativo do Windows via PyWinAuto) ---
                from rotinas.utils_ui import confirmar_download_ie
                confirmar_download_ie(driver)

                # Aguarda o download concluir antes de tentar mover o arquivo
                dia, mes, ano = data_fim.split("/")
                nome_dinamico = f"{revenda}.{mes}.{ano}"
                print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")

                rotinas.tratar_arquivo_baixado(
                    prefixo_arquivo="03.02.37",  # Atualizado para o prefixo da 030237
                    nome_personalizado=nome_dinamico,
                    caminho_destino=r"C:\Users\usuario\Desktop\Promax\promax\downloads"
                )

            except Exception as inner_e:
                print(
                    f"❌ Erro crítico ao processar a filial {revenda}: {inner_e}")
                print("⏭️ Pulando para a próxima revenda da lista...")
                continue

        # ====================================================================
        # FASE 3: ROTINA 09.10 PARA REVENDAS COM ALERTA
        # ====================================================================
        if revendas_com_alerta:
            print("\n" + "="*40)
            print("🚀 INICIANDO ROTINA 09.10 PARA AS REVENDAS COM AVISO")
            print("="*40)

            print("Fechando a janela atual...")
            driver.close()

            print("Retornando ao menu principal...")
            driver.switch_to.window(janela_menu)
            driver.switch_to.default_content()
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameMenu")))

            codigo_rotina_2 = "09.10"
            print(f"⌨️ Inserindo a rotina: {codigo_rotina_2}")
            botao_rotina = driver.find_element(By.ID, "atalho")
            botao_rotina.clear()
            botao_rotina.send_keys(codigo_rotina_2)
            botao_ok = driver.find_element(By.XPATH, '//*[@id="atal"]/div[1]/table/tbody/tr[2]/td/input[2]')
            driver.execute_script("arguments[0].click();", botao_ok)

            print("⏳ Aguardando carregamento da rotina...")
            driver.switch_to.default_content()

            janela_principal = driver.current_window_handle
            wait.until(EC.number_of_windows_to_be(2))
            janelas = driver.window_handles

            for janela in janelas:
                if janela != janela_principal:
                    driver.switch_to.window(janela)
                    time.sleep(1)
                    print(f"🔀 Mudamos para a nova janela da 09.10: {driver.title}")
                    
                    try:
                        from pywinauto import Application
                        import re
                        titulo_seguro = re.escape(driver.title)
                        app = Application(backend="win32").connect(title_re=f".*{titulo_seguro}.*", timeout=5)
                        app.window(title_re=f".*{titulo_seguro}.*").set_focus()
                    except Exception:
                        pass
                    break
            
            input("\n⏸️ Rotina 09.10 aberta. Confira a página e pressione ENTER para continuar o mesmo processo...")

            for indice_salvo, revenda in enumerate(revendas_com_alerta):
                print(f"\n{'='*40}")
                print(f"🔄 PROCESSANDO FILIAL NA 09.10 [{indice_salvo + 1}/{len(revendas_com_alerta)}]: {revenda}")
                print(f"{'='*40}")

                try:
                    print("🧹 Limpando alertas iniciais antes de interagir com a tela...")
                    fechar_popups(driver, 4)

                    driver.switch_to.default_content()
                    time.sleep(2)
                    
                    # Recupera o índice real original para selecionar a revenda corretamente
                    indice_real = lista_revendas.index(revenda)

                    from rotinas.utils_ui import mudar_revenda_com_fallback
                    mudar_revenda_com_fallback(driver, wait, indice_real)

                    print("⏳ Aguardando e fechando pop-ups de carregamento da troca...")
                    try:
                        WebDriverWait(driver, 10).until(EC.alert_is_present())
                        fechar_popups(driver, 4)
                    except Exception:
                        pass
                    time.sleep(3)

                    driver.switch_to.default_content()
                    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "rotina")))

                    print("🎯 Preenchendo campos específicos da rotina 09.10 (mesmo processo)...")

                    try:
                        dropdown_element_1 = wait.until(EC.presence_of_element_located((By.NAME, "quebra1")))
                        from rotinas.utils_ui import selecionar_dropdown_pyautogui
                        selecionar_dropdown_pyautogui(driver, dropdown_element_1, "Operacao")
                    except Exception:
                        print("Campo quebra1 nao encontrado.")

                    try:
                        dropdown_element_2 = wait.until(EC.presence_of_element_located((By.NAME, "quebra2")))
                        selecionar_dropdown_pyautogui(driver, dropdown_element_2, "Vendedor")
                    except Exception:
                        print("Campo quebra2 nao encontrado.")

                    try:
                        dropdown_element_3 = wait.until(EC.presence_of_element_located((By.NAME, "quebra3")))
                        selecionar_dropdown_pyautogui(driver, dropdown_element_3, "Motorista")
                    except Exception:
                        print("Campo quebra3 nao encontrado.")

                    try:
                        campo_ini = wait.until(EC.presence_of_element_located((By.NAME, "dataInicial")))
                        driver.execute_script("arguments[0].value = arguments[1];", campo_ini, data_inicio)
                    except Exception:
                        pass

                    try:
                        campo_fim = wait.until(EC.presence_of_element_located((By.NAME, "dataFinal")))
                        driver.execute_script("arguments[0].value = arguments[1];", campo_fim, data_fim)
                    except Exception:
                        pass

                    try:
                        itens = wait.until(EC.presence_of_element_located((By.NAME, "itens")))
                        driver.execute_script("arguments[0].scrollIntoView(true);", itens)
                        itens.click()
                    except Exception:
                        pass

                    print("🖱️ Clicando em Visualizar na 09.10...")
                    try:
                        btn_v = wait.until(EC.element_to_be_clickable((By.NAME, "BotVisualizar")))
                        driver.execute_script("arguments[0].click();", btn_v)
                    except:
                        try:
                            btn_v = driver.find_element(By.XPATH, "//button[contains(., 'Visualizar')]")
                            driver.execute_script("arguments[0].click();", btn_v)
                        except Exception:
                            print("Botao Visualizar nao encontrado na 09.10.")

                    # Lidar com possivel aviso (ESPERA INTELIGENTE NA 09.10)
                    import pygetwindow as gw
                    import time
                    tem_aviso_0910 = False
                    inicio_espera_0910 = time.time()
                    
                    print(f"⏳ Aguardando até {timeout_alerta}s para verificar se há alerta na 09.10...")
                    while time.time() - inicio_espera_0910 < timeout_alerta:
                        try:
                            alert = driver.switch_to.alert
                            print(f"⚠️ Aviso detectado na 09.10: {alert.text}")
                            alert.accept()
                            tem_aviso_0910 = True
                            break
                        except Exception:
                            pass
                        
                        try:
                            janelas = gw.getWindowsWithTitle('Processando')
                            if any(j for j in janelas if "edge" not in j.title.lower() or j.width < 600):
                                break
                        except Exception:
                            pass
                            
                        try:
                            if driver.find_elements(By.NAME, "GerExecl"):
                                break
                        except Exception:
                            pass
                            
                        time.sleep(1)
                        
                    if tem_aviso_0910:
                        print(f"⏭️ Pulando geração de CSV para a revenda {revenda} devido ao aviso na 09.10.")
                        continue

                    print("🚀 Relatório solicitado! Aguardando processamento e botão CSV...")
                    try:
                        botaoCsv = rotinas.aguardar_processamento_e_botao(driver, wait, By.NAME, "GerExecl", timeout_segundos=300)
                        driver.execute_script("arguments[0].click();", botaoCsv)
                        
                        from rotinas.utils_ui import confirmar_download_ie
                        confirmar_download_ie(driver)

                        dia, mes, ano = data_fim.split("/")
                        nome_dinamico = f"{revenda}.{mes}.{ano}"
                        print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")

                        rotinas.tratar_arquivo_baixado(
                            prefixo_arquivo="09.10", 
                            nome_personalizado=nome_dinamico,
                            caminho_destino=r"C:\Users\usuario\Desktop\Promax\promax\downloads"
                        )
                    except Exception:
                        print("Nao foi possivel baixar o relatorio da 09.10.")

                except Exception as inner_e:
                    print(f"❌ Erro crítico ao processar a filial {revenda} na 09.10: {inner_e}")
                    continue

    except Exception as e:
        print(f"❌ Erro fatal na rotina {codigo_rotina} (Fase de Setup): {e}")
