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
