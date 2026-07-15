import time
import os
import pyautogui
import subprocess
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pywinauto import Desktop
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from . import rotinas
from subprocess import check_output
from fecharPopups import fechar_popups


def executar(driver, wait, data_inicio, data_fim, janela_menu, lista_revendas):
    """Lógica específica da rotina 01200147"""
    codigo_rotina = "01200147"
    print(f"\n🚀 Iniciando execução da Rotina {codigo_rotina}...")

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
        # FASE 2: O LOOP DE REVENDAS (Repete até acabar a lista)
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

                # --- 2.2 LIDA COM OS POP-UPS DA TROCA (O Guarda-Costas) ---
                print("⏳ Vigiando ativamente a tela aguardando os pop-ups da troca...")
                try:
                    WebDriverWait(driver, 10).until(EC.alert_is_present())
                    print(
                        "🚨 Primeiro alerta detectado pelo Guarda-Costas! Iniciando limpeza...")
                    fechar_popups(driver, 4)
                except Exception:
                    print(
                        "✅ Nenhum alerta detectado nos últimos 10 segundos. Seguindo o fluxo...")
                time.sleep(3)                # --- 2.3 PREENCHIMENTO DE CAMPOS (Específico da 01200147) ---
                driver.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it(
                    (By.NAME, "rotina")))

                print("🎯 Selecionando 'Numerica' no dropdown...")
                try:
                    dropdown_element = wait.until(
                        EC.presence_of_element_located((By.NAME, "opcaoRel")))
                except Exception:
                    print("⚠️ Demora na atualização do frame. Tentando novamente...")
                    driver.switch_to.default_content()
                    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "rotina")))
                    dropdown_element = wait.until(EC.presence_of_element_located((By.NAME, "opcaoRel")))

                from rotinas.utils_ui import selecionar_dropdown_pyautogui
                selecionar_dropdown_pyautogui(driver, dropdown_element, "Numerica")

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

                print("🚀 Relatório solicitado! Aguardando processamento e botão CSV...")
                # 5. Clica no botão CSV (GerExecl) com espera ativa do Processando
                botaoCsv = rotinas.aguardar_processamento_e_botao(driver, wait, By.NAME, "GerExecl", timeout_segundos=300)
                driver.execute_script("arguments[0].click();", botaoCsv)

                # --- CONFIRMAÇÃO DO DOWNLOAD (Nativo do Windows via PyWinAuto) ---
                from rotinas.utils_ui import confirmar_download_ie
                confirmar_download_ie(driver)

                # LIMPEZA DO NOME E DIRETÓRIO
                dia, mes, ano = data_fim.split("/")
                nome_dinamico = f"{revenda}"

                print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")
                rotinas.tratar_arquivo_baixado(
                    prefixo_arquivo="01.20.01.47",  # Mantido conforme o padrão do seu template original
                    nome_personalizado=nome_dinamico,
                    caminho_destino=r"T:\ATENDIMENTO\BEES DELIVERY\01.20.01.47"
                )

            except Exception as inner_e:
                print(
                    f"❌ Erro crítico ao processar a filial {revenda}: {inner_e}")
                print("⏭️ Pulando para a próxima revenda da lista...")
                continue

    except Exception as e:
        print(f"❌ Erro fatal na rotina {codigo_rotina} (Fase de Setup): {e}")
