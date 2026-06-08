import time
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from . import rotinas
from fecharPopups import fechar_popups


def executar(driver, wait, data_inicio, data_fim, janela_menu, lista_revendas):
    """Lógica da Planilha de Acompanhamento (Rotina 031120)"""

    codigo_rotina = "031120"
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

        print(f"⌨️ Inserindo código da rotina: {codigo_rotina}")
        botao_rotina = wait.until(
            EC.visibility_of_element_located((By.ID, "atalho")))
        botao_rotina.clear()
        botao_rotina.send_keys(codigo_rotina)

        botao_ok = driver.find_element(
            By.XPATH, '//*[@id="atal"]/div[1]/table/tbody/tr[2]/td/input[2]')
        botao_ok.click()

        print("⏳ Aguardando abertura da janela do relatório...")
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

                # --- 2.2 LIDA COM OS POP-UPS DA TROCA ---
                print("⏳ Vigiando ativamente a tela aguardando os pop-ups da troca...")
                try:
                    WebDriverWait(driver, 10).until(EC.alert_is_present())
                    print(
                        "🚨 Primeiro alerta detectado pelo Guarda-Costas! Iniciando limpeza...")
                    fechar_popups(driver, 4)
                except Exception:
                    print(
                        "✅ Nenhum alerta detectado nos últimos 10 segundos. Seguindo o fluxo...")

                # --- 2.3 PREENCHIMENTO DO RELATÓRIO (Específico da 031120) ---
                driver.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it(
                    (By.NAME, "rotina")))

                print("🎯 Selecionando 'Mapa' no dropdown...")
                dropdown = wait.until(
                    EC.presence_of_element_located((By.NAME, "opcaoRel")))

                driver.execute_script(r"""
                    var select = arguments[0];
                    var alvo = "Mapa";
                    for (var i = 0; i < select.options.length; i++) {
                        var texto = select.options[i].text.replace(/^\s+|\s+$/g, '');
                        if (texto === alvo) {
                            select.selectedIndex = i;
                            if ("createEvent" in document) {
                                var evt = document.createEvent("HTMLEvents");
                                evt.initEvent("change", false, true);
                                select.dispatchEvent(evt);
                            } else { select.fireEvent("onchange"); }
                            break;
                        }
                    }
                """, dropdown)

                print(f"📅 Preenchendo datas: {data_inicio} até {data_fim}")
                campo_ini = wait.until(
                    EC.presence_of_element_located((By.NAME, "dataInicial")))
                driver.execute_script(
                    "arguments[0].value = arguments[1];", campo_ini, data_inicio)

                campo_fim = wait.until(
                    EC.presence_of_element_located((By.NAME, "dataFinal")))
                driver.execute_script(
                    "arguments[0].value = arguments[1];", campo_fim, data_fim)

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

                time.sleep(15)
                rotinas.matar_overlay_processando(driver)

                print("🚀 Relatório solicitado! Aguardando botão CSV...")
                botaoCsv = wait.until(
                    EC.presence_of_element_located((By.NAME, "GerExecl")))
                botaoCsv.click()

                print("⌨️ Acionando comandos de teclado para salvar...")
                time.sleep(4)
                pyautogui.hotkey('alt', 'n')
                time.sleep(1)
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('enter')

                # Dupla confirmação de teclado (padrão que você estabeleceu)
                time.sleep(2)
                pyautogui.hotkey('alt', 'n')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('enter')

                # Tempo vital para o Windows concluir o download
                time.sleep(10)

                # LIMPEZA DO NOME E CAMINHO DINÂMICO
                cidade_limpa = revenda.split("-")[-1].strip()
                dia, mes, ano = data_fim.split("/")

                nome_dinamico = f"{cidade_limpa}.{mes}.{ano}"
                print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")

                # O caminho agora se ajusta automaticamente à cidade e ao ano
                caminho_pasta_dinamico = rf"C:\Users\usuario\Desktop\Promax\promax\downloads"

                rotinas.tratar_arquivo_baixado(
                    prefixo_arquivo="03.11.20",
                    nome_personalizado=nome_dinamico,
                    caminho_destino=caminho_pasta_dinamico
                )

            except Exception as inner_e:
                print(
                    f"❌ Erro crítico ao processar a filial {revenda}: {inner_e}")
                print("⏭️ Pulando para a próxima revenda da lista...")
                continue

    except Exception as e:
        print(f"❌ Erro fatal na rotina {codigo_rotina} (Fase de Setup): {e}")
