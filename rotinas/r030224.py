import time
import pyautogui
import re
import os
from pywinauto import Desktop
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException

from fecharPopups import fechar_popups
from . import rotinas


def executar(driver, wait, data_inicio, data_fim, janela_menu, lista_revendas):
    """Lógica específica da rotina 030224"""

    codigo_rotina = "030224"
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
        botao_ok.click()

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
                # 🛡️ O ESCUDO INICIAL: Limpa a sujeira que a rodada anterior possa ter deixado
                print("🧹 Limpando alertas iniciais antes de interagir com a tela...")
                fechar_popups(driver, 4)

                print("📍 DEBUG 1: Resetando para a raiz da página (default_content)...")
                driver.switch_to.default_content()

                # --- 2.1 TROCA DE REVENDA ---
                print("📍 DEBUG 2: Tentando entrar no frame superior...")
                wait.until(EC.frame_to_be_available_and_switch_to_it(
                    (By.NAME, "top_rotina")))
                print("📍 DEBUG 3: Sucesso! Entrou no frame superior.")

                print(
                    "📍 DEBUG 4: Focando no dropdown com Selenium e navegando com PyAutoGUI...")
                select_principal = wait.until(
                    EC.presence_of_element_located((By.NAME, "unidade")))

                select_principal.click()
                time.sleep(0.5)

                # PyAutoGUI assume o volante (Teclado puro não sofre de StaleElement)
                pyautogui.press('home')
                time.sleep(0.5)

                if indice > 0:
                    print(f"⬇️ Descendo {indice} posições via teclado...")
                    for _ in range(indice):
                        pyautogui.press('down')
                        time.sleep(0.1)

                pyautogui.press('enter')
                time.sleep(0.5)
                pyautogui.press('tab')

                try:
                    driver.execute_script(
                        "document.getElementsByName('unidade')[0].blur();")
                except:
                    pass

                # --- 2.2 LIDA COM OS POP-UPS DA TROCA ---
                print("⏳ Aguardando e fechando pop-ups de carregamento da troca...")

                try:
                    WebDriverWait(driver, 15).until(EC.alert_is_present())
                    print(
                        "🚨 Primeiro alerta detectado pelo Guarda-Costas! Iniciando limpeza...")

                    fechar_popups(driver, 6)
                except Exception:
                    # Se passarem 10 segundos e nada aparecer, assumimos que o Promax não vai mandar alerta nenhum.
                    print(
                        "✅ Nenhum alerta detectado nos últimos 10 segundos. Seguindo o fluxo...")

                # --- 2.3 PREENCHIMENTO DE CAMPOS ---
                driver.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it(
                    (By.NAME, "rotina")))

                print("🎯 Selecionando 'Mapa' no dropdown...")
                try:
                    dropdown_element = wait.until(
                        EC.presence_of_element_located((By.NAME, "opcaoRel")))
                except Exception:
                    print("⚠️ Demora na atualização do frame. Tentando novamente...")
                    driver.switch_to.default_content()
                    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "rotina")))
                    dropdown_element = wait.until(EC.presence_of_element_located((By.NAME, "opcaoRel")))

                driver.execute_script(r"""
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

                # Checkboxes
                checks = ["selecionouAS",
                          "responsabProcesso", "todasOperacoes"]
                for check in checks:
                    el = wait.until(
                        EC.presence_of_element_located((By.NAME, check)))
                    driver.execute_script(
                        "arguments[0].scrollIntoView(true);", el)
                    el.click()

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

                print("🚀 Relatório solicitado! Aguardando processamento e botão CSV...")
                # Clica no botão CSV (GerExecl) com espera ativa do Processando
                botaoCsv = rotinas.aguardar_processamento_e_botao(driver, wait, By.NAME, "GerExecl", timeout_segundos=300)
                driver.execute_script("arguments[0].click();", botaoCsv)

                # --- INÍCIO DO PYWINAUTO PARA MÚLTIPLAS JANELAS ---
                titulo_janela_atual = driver.title
                titulo_seguro = re.escape(titulo_janela_atual)
                try:
                    # 1. Isola a janela principal do navegador
                    janela_ie = Desktop(backend="uia").window(
                        title_re=f".*{titulo_seguro}.*")

                    # 2. Encontra a barra de notificação usando o título exato indicado no log
                    barra_notificacao = janela_ie.child_window(
                        title="Notificação", control_type="ToolBar")

                    # 3. Encontra o botão "Salvar" usando o tipo correto: SplitButton
                    botao_salvar = barra_notificacao.child_window(
                        title="Salvar", control_type="SplitButton")

                    # Garante o foco na janela e realiza o clique físico com o rato
                    janela_ie.set_focus()
                    botao_salvar.click_input()

                    print("Download confirmado com sucesso no SplitButton!")

                except Exception as e:
                    print(f"Erro ao interagir com a barra de download: {e}")

                dia, mes, ano = data_fim.split("/")
                nome_dinamico = f"{revenda}.{mes}.{ano}"

                print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")

                rotinas.tratar_arquivo_baixado(
                    prefixo_arquivo="03.02.24",
                    nome_personalizado=nome_dinamico,
                    caminho_destino=r"T:\ATENDIMENTO\BEES DELIVERY\03.02.24"
                )

            except Exception as inner_e:
                print(
                    f"❌ Erro crítico ao processar a filial {revenda}: {inner_e}")
                print("⏭️ Pulando para a próxima revenda da lista...")
                continue

    except Exception as e:
        print(f"❌ Erro fatal na rotina {codigo_rotina} (Fase de Setup): {e}")
