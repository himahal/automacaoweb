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


def executar(driver, wait, data_inicio, data_fim, janela_menu, lista_unidades):
    """Lógica específica da rotina 030224"""

    codigo_rotina = "030224"
    try:
        print("Retornando ao frame de comandos...")
        driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))

        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.ID, "iFrameMenu")))

        print(f"⌨️ Inserindo a rotina: {codigo_rotina}")

        botao_rotina = driver.find_element(By.ID, "atalho")
        botao_rotina.clear()
        botao_rotina.send_keys(codigo_rotina)
        botao_ok = driver.find_element(
            By.XPATH, '//*[@id="atal"]/div[1]/table/tbody/tr[2]/td/input[2]')
        botao_ok.click()

        print("⏳ Aguardando carregamento da rotina...")
        driver.switch_to.default_content()

        janela_principal = driver.current_window_handle
        wait.until(EC.number_of_windows_to_be(2))
        janelas = driver.window_handles

        for janela in janelas:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                time.sleep(1)
                print(f"🔀 Mudamos para a nova janela: {driver.title}")
                break

        for indice, unidade in enumerate(lista_unidades):
            print(f"\n{'='*40}")
            print(
                f"🔄 PROCESSANDO FILIAL [{indice + 1}/{len(lista_unidades)}]: {unidade}")
            print(f"{'='*40}")

            try:
                fechar_popups(driver, 4)

                driver.switch_to.default_content()
                time.sleep(2)

                wait.until(EC.frame_to_be_available_and_switch_to_it(
                    (By.NAME, "top_rotina")))

                select_principal = wait.until(
                    EC.presence_of_element_located((By.NAME, "unidade")))

                select_principal.click()
                time.sleep(0.5)

                pyautogui.press('home')
                time.sleep(0.5)

                if indice > 0:
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

                try:
                    WebDriverWait(driver, 15).until(EC.alert_is_present())
                    fechar_popups(driver, 6)
                except Exception:
                    pass

                driver.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it(
                    (By.NAME, "rotina")))

                dropdown_element = wait.until(
                    EC.presence_of_element_located((By.NAME, "opcaoRel")))

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

                checks = ["selecionouAS",
                          "responsabProcesso", "todasOperacoes"]
                for check in checks:
                    el = wait.until(
                        EC.presence_of_element_located((By.NAME, check)))
                    driver.execute_script(
                        "arguments[0].scrollIntoView(true);", el)
                    el.click()

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

                time.sleep(15)
                rotinas.matar_overlay_processando(driver)

                print("🚀 Relatório solicitado! Aguardando botão CSV...")
                botaoCsv = wait.until(
                    EC.presence_of_element_located((By.NAME, "GerExecl")))
                botaoCsv.click()

                titulo_janela_atual = driver.title
                titulo_seguro = re.escape(titulo_janela_atual)
                try:
                    janela_ie = Desktop(backend="uia").window(
                        title_re=f".*{titulo_seguro}.*")

                    barra_notificacao = janela_ie.child_window(
                        title="Notificação", control_type="ToolBar")

                    botao_salvar = barra_notificacao.child_window(
                        title="Salvar", control_type="SplitButton")

                    janela_ie.set_focus()
                    botao_salvar.click_input()

                    print("Download confirmado com sucesso!")

                except Exception as e:
                    print(f"Erro ao interagir com a barra de download: {e}")

                dia, mes, ano = data_fim.split("/")
                nome_dinamico = f"{unidade}.{mes}.{ano}"

                print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")

                rotinas.tratar_arquivo_baixado(
                    prefixo_arquivo="03.02.24",
                    nome_personalizado=nome_dinamico,
                    caminho_destino=r"T:\ATENDIMENTO\BEES DELIVERY\03.02.24"
                )

            except Exception as inner_e:
                print(
                    f"❌ Erro crítico ao processar a filial {unidade}: {inner_e}")
                print("⏭️ Pulando para a próxima unidade da lista...")
                continue

    except Exception as e:
        print(f"❌ Erro fatal na rotina {codigo_rotina}: {e}")
