import time
import pyautogui

def selecionar_dropdown_pyautogui(driver, elemento_select, texto_alvo):
    """
    Seleciona uma opção em um <select> no Promax usando teclado (pyautogui).
    Isso previne erros de StaleElement e contorna bugs do IE ao disparar eventos onChange.
    """
    indice = driver.execute_script(r"""
        var select = arguments[0];
        var alvo = arguments[1];
        for (var i = 0; i < select.options.length; i++) {
            var texto = select.options[i].text.replace(/^\s+|\s+$/g, '');
            if (texto === alvo) { return i; }
        }
        return -1;
    """, elemento_select, texto_alvo)

    if indice == -1:
        print(f"⚠️ Alvo '{texto_alvo}' não encontrado no dropdown.")
        return

    print(f"🎯 Selecionando '{texto_alvo}' via teclado (posição {indice})...")
    
    # Focar no elemento sem clicar (o .click() trava o IEDriver em selects nativos)
    driver.execute_script("arguments[0].focus();", elemento_select)
    time.sleep(0.5)
    
    # Ir para a primeira opção do dropdown
    pyautogui.press('home')
    time.sleep(0.5)
    
    # Descer a quantidade de vezes necessárias
    if indice > 0:
        print(f"⬇️ Descendo {indice} posições via teclado...")
        for _ in range(indice):
            pyautogui.press('down')
            time.sleep(0.1)
            
    # Confirmar e sair
    pyautogui.press('enter')
    time.sleep(0.5)
    pyautogui.press('tab')
    time.sleep(0.5)


def confirmar_download_ie(driver, timeout_segundos=20):
    """
    Interage com a barra de download nativa do IE/Edge para clicar em 'Salvar'.
    Usa PyWinAuto de forma segura, conectando diretamente à janela para evitar travamentos.
    """
    import re
    import time
    from pywinauto import Application

    print("📥 Confirmando download na barra do Windows...")

    titulo_janela = driver.title
    titulo_seguro = re.escape(titulo_janela)

    inicio = time.time()
    while time.time() - inicio < timeout_segundos:
        try:
            # Conecta diretamente à janela do Edge/IE por título para evitar varredura lenta no Desktop
            app = Application(backend="uia").connect(title_re=f".*{titulo_seguro}.*", timeout=5)
            janela_ie = app.window(title_re=f".*{titulo_seguro}.*")

            # Traz a janela para o foco principal
            janela_ie.set_focus()

            # Localiza a barra de notificação
            barra_notificacao = janela_ie.child_window(title="Notificação", control_type="ToolBar")

            # Procura o botão Salvar
            botao_salvar = barra_notificacao.child_window(title="Salvar", control_type="SplitButton")

            # Clica no botão Salvar
            botao_salvar.click_input()
            print("✅ Download confirmado com sucesso no SplitButton!")

            # Espera 1.5s para o download iniciar e tenta fechar a barra de download para devolver o foco
            time.sleep(1.5)
            try:
                # Tenta achar o botão Fechar (X) na barra
                for termo in ["Fechar", "Close"]:
                    try:
                        botao_fechar = barra_notificacao.child_window(title=termo, control_type="Button")
                        botao_fechar.click_input()
                        print("🧹 Barra de download fechada para limpar o foco.")
                        break
                    except Exception:
                        pass
            except Exception:
                pass

            return True

        except Exception as e:
            # Se não achou os elementos da barra ainda, aguarda um pouco e tenta novamente
            time.sleep(1)

    print("⚠️ Não foi possível interagir com a barra de download (Timeout ou elemento não localizado).")
    return False


def mudar_revenda_com_fallback(driver, wait, indice):
    """
    Muda a revenda no dropdown 'unidade' da top_rotina.
    Primeiro tenta usar JavaScript (muito mais rápido e seguro).
    Se não detectar mudança/recarregamento, tenta o fallback com PyAutoGUI.
    """
    import time
    import pyautogui
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from pywinauto import Desktop
    import re

    # 1. Garante que estamos no frame top_rotina
    print("📍 default_content para ir para a raiz...")
    driver.switch_to.default_content()
    print("📍 Entrando no frame top_rotina...")
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top_rotina")))
    
    select_el = wait.until(EC.presence_of_element_located((By.NAME, "unidade")))
    
    # Debug para logar a estrutura do elemento
    try:
        outer_html = select_el.get_attribute("outerHTML")
        print(f"📊 DEBUG SELECT HTML: {outer_html}")
    except Exception as e_html:
        print(f"⚠️ Erro ao capturar HTML do select: {e_html}")

    # Captura o valor/texto atual antes de tentar mudar
    js_get_selected = "var s = document.getElementsByName('unidade')[0]; return s.options[s.selectedIndex].text;"
    texto_original = driver.execute_script(js_get_selected)
    print(f"📍 Filial atual no dropdown antes da troca: '{texto_original}'")

    # --- MÉTODO 1: JAVASCRIPT (Preferencial) ---
    print(f"⚡ Tentando selecionar o índice {indice} via JavaScript...")
    try:
        driver.execute_script("""
            var select = document.getElementsByName('unidade')[0];
            var targetIndex = arguments[0];
            if (targetIndex >= 0 && targetIndex < select.options.length) {
                select.selectedIndex = targetIndex;
                if (select.onchange) {
                    select.onchange();
                } else {
                    var event = document.createEvent('HTMLEvents');
                    event.initEvent('change', true, true);
                    select.dispatchEvent(event);
                }
            }
        """, indice)
        time.sleep(2) # Aguarda para ver se disparou recarregamento
    except Exception as e_js:
        print(f"⚠️ Erro na execução do JS de troca de revenda: {e_js}")

    # Verifica se o texto mudou
    try:
        texto_novo = driver.execute_script(js_get_selected)
        if texto_novo != texto_original:
            print(f"✅ Sucesso! Revenda alterada via JS para: '{texto_novo}'")
            return
    except Exception:
        # Se deu erro de StaleElement aqui, significa que a página recarregou (o que é ótimo!)
        print("✅ Sucesso! Recarregamento de página detectado após o JS.")
        return

    # --- MÉTODO 2: FALLBACK COM PYAUTOGUI (Teclado) ---
    print("⚠️ JavaScript não surtiu efeito. Iniciando fallback via PyAutoGUI...")
    try:
        # Garante o foco físico na janela do Edge
        titulo_seguro = re.escape(driver.title)
        Desktop(backend="uia").window(title_re=f".*{titulo_seguro}.*").set_focus()
        print("🎯 Foco da janela principal restaurado via PyWinAuto!")
    except Exception as e_foco:
        print(f"⚠️ Erro ao focar janela principal: {e_foco}")

    # Clica usando Selenium para abrir a lista no IE
    print("🖱️ Clicando no dropdown via Selenium para abrir...")
    try:
        select_el.click()
    except Exception as e_click:
        print(f"⚠️ Erro ao clicar no select via Selenium: {e_click}")
    time.sleep(0.5)

    print("⌨️ Enviando teclas PyAutoGUI...")
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
        driver.execute_script("document.getElementsByName('unidade')[0].blur();")
    except:
        pass
