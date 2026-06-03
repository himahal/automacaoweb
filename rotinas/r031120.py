import time
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from . import rotinas


def executar(driver, wait, data_inicio, data_fim, janela_menu):
    """Lógica da Planilha de Acompanhamento (Rotina 031120)"""
    codigo_rotina = "031120"

    print(f"\n🚀 Iniciando execução da Rotina {codigo_rotina}...")

    try:
        # --- 1. ACESSO À ROTINA ---
        print("📂 Navegando pelos frames de comando...")

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))
        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.ID, "iFrameMenu")))

        print(f"⌨️ Inserindo código da rotina: {codigo_rotina}")
        # Inserindo Rotina
        botao_rotina = driver.find_element(By.ID, "atalho")
        print("Elemento localizado")
        print("Tag:", botao_rotina.tag_name)
        print("Botão atalho encontrado")
        botao_rotina.clear()
        print("Campo limpo")
        botao_rotina.send_keys(codigo_rotina)
        print("campo enviado")

        # Botão OK
        driver.find_element(
            By.XPATH, '//*[@id="atal"]/div[1]/table/tbody/tr[2]/td/input[2]').click()

        print("⏳ Aguardando abertura da janela do relatório...")
        driver.switch_to.default_content()

        # --- 2. GESTÃO DE JANELAS ---
        janela_principal = driver.current_window_handle
        wait.until(EC.number_of_windows_to_be(2))

        for janela in driver.window_handles:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                time.sleep(1)  # Tempo para o Windows processar a nova janela
                print(f"🔀 Mudamos para: {driver.title}")
                break

        # --- 3. PREENCHIMENTO DO RELATÓRIO ---
        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.NAME, "rotina")))

        print("🎯 Selecionando 'Mapa' no dropdown...")
        dropdown = wait.until(
            EC.presence_of_element_located((By.NAME, "opcaoRel")))

        driver.execute_script("""
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

        # --- 4. GERAÇÃO E DOWNLOAD ---
        print("🖱️ Clicando em Visualizar...")
        try:
            btn_v = wait.until(EC.element_to_be_clickable(
                (By.NAME, "BotVisualizar")))
            driver.execute_script("arguments[0].click();", btn_v)
        except:
            btn_v = driver.find_element(
                By.XPATH, "//button[contains(., 'Visualizar')]")
            driver.execute_script("arguments[0].click();", btn_v)

        print("🚀 Relatório solicitado! Aguardando botão CSV...")

        # O Promax leva tempo para gerar o relatório na tela
        time.sleep(10)

        btn_csv = wait.until(
            EC.presence_of_element_located((By.NAME, "GerExecl")))
        btn_csv.click()
        print("📊 Botão CSV acionado!")

        # --- 5. INTERAÇÃO COM O WINDOWS (DOWNLOAD BAR) ---
        print("⏳ Aguardando barra de download do IE...")
        time.sleep(3)

        try:
            print("⌨️ Salvando arquivo via PyAutoGUI (Alt+N -> Tab -> Tab -> Enter)...")
            pyautogui.hotkey('alt', 'n')
            time.sleep(1)
            pyautogui.press('tab')
            pyautogui.press('tab')
            pyautogui.press('enter')

            print("🧹 Fechando janela do relatório e retornando ao menu...")
            time.sleep(3)  # Espera o Windows processar o início do download

            driver.close()  # Fecha a janela atual (o relatório)
            driver.switch_to.window(janela_menu)  # Volta para a janela do menu

            dia, mes, ano = data_fim.split("/")
            # O f"" permite injetar as variáveis direto no texto
            nome_dinamico = f"Revalle Juazeiro.{mes}.{ano}"

            print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")
            rotinas.tratar_arquivo_baixado(
                prefixo_arquivo="03.11.20",
                nome_personalizado=nome_dinamico,
                caminho_destino=r"T:\ATENDIMENTO\BEES DELIVERY\03.11.20\Juazeiro\2026"
            )

            print(f"✅ Download da rotina {codigo_rotina} concluído!")
        except Exception as e_kbd:
            print(f"❌ Falha ao interagir com o teclado: {e_kbd}")

    except Exception as e:
        print(f"❌ Erro crítico na rotina {codigo_rotina}: {e}")

    return
