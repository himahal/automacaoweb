import time
import pyautogui


def selecionar_dropdown_pyautogui(driver, elemento_select, texto_alvo):
    """Seleciona uma opção em um <select> no Promax usando script JS."""
    print(f"🎯 Selecionando '{texto_alvo}' no dropdown via JS...")
    try:
        driver.execute_script(r"""
            var select = arguments[0];
            var textoParaSelecionar = arguments[1];
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
        """, elemento_select, texto_alvo)
        time.sleep(0.5)
    except Exception as e:
        print(f"⚠️ Erro ao selecionar dropdown via JS: {e}")


def confirmar_download_ie(driver, timeout_segundos=20):
    """Interage com a barra de download nativa do IE/Edge para clicar em 'Salvar'."""
    import re
    import time
    from pywinauto import Application

    print("📥 Confirmando download na barra do Windows...")

    titulo_janela = driver.title
    titulo_seguro = re.escape(titulo_janela)

    inicio = time.time()
    while time.time() - inicio < timeout_segundos:
        try:
            app = Application(backend="uia").connect(title_re=f".*{titulo_seguro}.*", timeout=5)
            janela_ie = app.window(title_re=f".*{titulo_seguro}.*")

            janela_ie.set_focus()

            barra_notificacao = janela_ie.child_window(title="Notificação", control_type="ToolBar")
            botao_salvar = barra_notificacao.child_window(title="Salvar", control_type="SplitButton")

            botao_salvar.click_input()
            print("✅ Download confirmado com sucesso!")

            time.sleep(1.5)
            try:
                for termo in ["Fechar", "Close"]:
                    try:
                        botao_fechar = barra_notificacao.child_window(title=termo, control_type="Button")
                        botao_fechar.click_input()
                        print("🧹 Barra de download fechada.")
                        break
                    except Exception:
                        pass
            except Exception:
                pass

            return True

        except Exception as e:
            time.sleep(1)

    print("⚠️ Não foi possível interagir com a barra de download.")
    return False


def mudar_unidade_com_fallback(driver, wait, indice):
    """Muda a unidade no dropdown 'unidade' da top_rotina."""
    import time
    import pyautogui
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from pywinauto import Desktop
    import re

    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top_rotina")))
    
    select_el = wait.until(EC.presence_of_element_located((By.NAME, "unidade")))

    js_get_selected = "var s = document.getElementsByName('unidade')[0]; return s.options[s.selectedIndex].text;"
    texto_original = driver.execute_script(js_get_selected)
    print(f"📍 Unidade atual no dropdown antes da troca: '{texto_original}'")

    print(f"⚡ Selecionando o índice {indice} via JavaScript...")
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
        time.sleep(2)
    except Exception as e_js:
        print(f"⚠️ Erro na execução do JS de troca de unidade: {e_js}")

    try:
        texto_novo = driver.execute_script(js_get_selected)
        if texto_novo != texto_original:
            print(f"✅ Sucesso! Unidade alterada via JS para: '{texto_novo}'")
            return
    except Exception:
        print("✅ Recarregamento de página detectado após o JS.")
        return

    print("⚠️ Alternando para fallback via PyAutoGUI...")
    try:
        titulo_seguro = re.escape(driver.title)
        Desktop(backend="uia").window(title_re=f".*{titulo_seguro}.*").set_focus()
    except Exception as e_foco:
        print(f"⚠️ Erro ao focar janela principal: {e_foco}")

    try:
        select_el.click()
    except Exception as e_click:
        print(f"⚠️ Erro ao clicar no select: {e_click}")
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
        driver.execute_script("document.getElementsByName('unidade')[0].blur();")
    except:
        pass
