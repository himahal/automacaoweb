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
    
    # Focar no elemento
    elemento_select.click()
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
