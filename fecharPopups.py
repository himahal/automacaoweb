import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def fechar_popups(driver_instance, max_popups_to_check, wait_timeout_per_popup=3):
    """
    Tenta fechar pop-ups de alerta (JavaScript alerts) que podem aparecer.
    Args:
        driver_instance: A instância do WebDriver (navegador).
        max_popups_to_check: O número máximo de pop-ups que o script tentará fechar.
        wait_timeout_per_popup: O tempo máximo de espera por cada pop-up.
    Returns:
        O número de pop-ups fechados.
    """
    popups_fechados = 0
    for i in range(max_popups_to_check):
        try:
            WebDriverWait(driver_instance, wait_timeout_per_popup).until(
                EC.alert_is_present())
            alerta = driver_instance.switch_to.alert
            # Imprime o texto do alerta
            print(f"Alerta {i + 1} encontrado: '{alerta.text}'\n")
            alerta.accept()  # Aceita/fecha o alerta
            popups_fechados += 1
            print(f"Alerta {i + 1} fechado com sucesso!\n")
            # Pequena pausa para garantir que o alerta foi processado
            time.sleep(1)
        except TimeoutException:  # Captura especificamente o TimeoutException
            print(
                f"Não há mais pop-ups ou tempo limite para o alerta {i + 1} atingido.\n")
            break
        except Exception as e:
            print(
                f"Erro inesperado ao tentar fechar pop-up {i + 1}: {str(e)}\n")
            break
    print(f"✅ Total de {popups_fechados} pop-ups fechados.\n")
    return popups_fechados
