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
from subprocess import check_output
from selenium.webdriver.common.action_chains import ActionChains
from pathlib import Path
import shutil


opcoes_chrome = Options()

# 3. Passa o caminho do User Data para as opções do Selenium
opcoes_chrome.add_argument(
    r"--user-data-dir=C:\ChromeAutomation\User Data"
)

# 4. Define qual perfil você quer usar
opcoes_chrome.add_argument("--profile-directory=Profile 2")
# Pasta de download da automação
prefs = {
    "download.default_directory": r"C:\ChromeAutomation\Downloads",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

opcoes_chrome.add_experimental_option(
    "prefs",
    prefs
)
opcoes_chrome.add_argument("--no-first-run")
opcoes_chrome.add_argument("--no-default-browser-check")
opcoes_chrome.add_argument("--disable-dev-shm-usage")
opcoes_chrome.add_argument(
    "--disable-features=OptimizationGuideModelDownloading")

url_do_bi = "https://app.powerbi.com/groups/me/apps/a44ca4f3-ad02-4e6d-b2f9-523d74c0a272/reports/67b52c11-a1cb-433f-adee-e18e506d552a/ReportSection?ctid=cef04b19-7776-4a94-b89b-375c77a8f936&experience=power-bi"

caminho_driver = ChromeDriverManager().install()
print(caminho_driver)
print(
    check_output(
        [caminho_driver, "--version"],
        text=True
    )
)

servico_chrome = Service(
    ChromeDriverManager().install()
)

print("🌐 Abrindo o Google Chrome...")
servico_chrome = Service(ChromeDriverManager().install())

# 5. INSERE AS OPÇÕES NA INICIALIZAÇÃO DO DRIVER
driver_chrome = webdriver.Chrome(
    service=servico_chrome, options=opcoes_chrome)
print(f"✅ Conectado! Título da aba: {driver_chrome.title}")
driver_chrome.get(url_do_bi)
print(driver_chrome.current_url)
print(f"✅ Página aberta: {driver_chrome.title}")

time.sleep(20)
# define a função de selecionar revenda

# lista as regiões
# regioes = [
#     "1031287 - REVALLE AGRESTE/ALAGOINHAS (BA)",
#     "1031295 - REVALLE AGRESTE/SERRINHA (BA)",
#     "505145 - REVALLE/JUAZEIRO(BA)",
#     "538663 - REVALLE/SENHOR DO BONFIM(BA)",
#     "585505 - BEIRA RIO/PETROLINA(PE)",
#     "826588 - REVALLE NORDESTE/RIB. POMBAL (BA)",
#     "983616 - REVALLE PAULO AFONSO"
# ]
# mapeia as revendas
regioes = {
    "1031287 - REVALLE AGRESTE/ALAGOINHAS (BA)": "Revalle Alagoinhas",
    "1031295 - REVALLE AGRESTE/SERRINHA (BA)": "Revalle Serrinha",
    "505145 - REVALLE/JUAZEIRO(BA)": "Revalle Juazeiro",
    "538663 - REVALLE/SENHOR DO BONFIM(BA)": "Revalle Bonfim",
    "585505 - BEIRA RIO/PETROLINA(PE)": "Beira Rio",
    "826588 - REVALLE NORDESTE/RIB. POMBAL (BA)": "Revalle Nordeste",
    "983616 - REVALLE PAULO AFONSO": "Revalle P Afonso"
}


def selecionar_regiao(wait, driver, nome_regiao):

    # abre o dropdown
    dropdown = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "[data-testid='slicer-dropdown']"
            )
        )
    )

    driver.execute_script(
        "arguments[0].click();",
        dropdown
    )

    time.sleep(4)

    # seleciona a região desejada
    regiao = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//div[@role='option' and @title='{nome_regiao}']"
            )
        )
    )

    driver.execute_script(
        "arguments[0].click();",
        regiao
    )

    time.sleep(4)

    # verifica o texto exibido
    texto_selecionado = driver.find_element(
        By.CSS_SELECTOR,
        ".slicer-restatement"
    ).text

    print(
        f"Filtro retornou: "
        f"{texto_selecionado}"
    )

    if nome_regiao in texto_selecionado:
        print(
            "✅ Região selecionada corretamente"
        )

    else:
        print(
            "⚠️ Região incorreta. "
            "Tentando corrigir..."
        )
        # abre dropdown novamente
        dropdown = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "[data-testid='slicer-dropdown']"
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            dropdown
        )

        time.sleep(1)

        # clica em Selecionar tudo
        selecionar_tudo = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[@role='option' and @title='Selecionar tudo']"
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            selecionar_tudo
        )

        time.sleep(2)

    # fecha o dropdown clicando novamente
    dropdown.click()

    print(f"✅ Região selecionada: {nome_regiao}")


# 1. Calcular as datas dinamicamente usando a biblioteca nativa do Python
# Espera a data aparecer
wait = WebDriverWait(driver_chrome, 1000)

# looping principal
campo_data_inicio = wait.until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            "//input[contains(@aria-label,'Data de início')]"
        )
    )
)
campo_data_fim = wait.until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            "//input[contains(@aria-label,'Data de término')]"
        )
    )
)
for regiao_bi, nome_arquivo in regioes.items():

    print(f"📍 Processando: {regiao_bi}")

    # 1. Seleciona a região
    selecionar_regiao(
        wait,
        driver_chrome,
        regiao_bi
    )
    hoje = datetime.today()
    data_inicial = hoje.replace(day=1).strftime("%d/%m/%Y")  # Ex: 01/06/2026
    data_final = hoje.strftime("%d/%m/%Y")                  # Ex: 09/06/2026
    campo_data_inicio = driver_chrome.find_element(
        By.XPATH, "//input[contains(@aria-label, 'Data de início')]")
    campo_data_fim = driver_chrome.find_element(
        By.XPATH, "//input[contains(@aria-label, 'Data de término')]")

    print(campo_data_inicio.get_attribute("aria-label"))
    print(campo_data_fim.get_attribute("aria-label"))

    # 3. Preencher a Data Inicial
    driver_chrome.execute_script("""
    arguments[0].value = arguments[1];
    arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
    arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
    """, campo_data_inicio, data_inicial)
    time.sleep(1)

    # 4. Preencher a Data Final
    driver_chrome.execute_script("""
    arguments[0].value = arguments[1];
    arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
    arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
    """, campo_data_fim, data_final)
    time.sleep(1)

    visuais = driver_chrome.find_elements(
        By.TAG_NAME,
        "visual-container"
    )

    cabecalho = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "[data-query-ref='Tour_Visit_Rev.estimated_time_arrival']"
            )
        )
    )

    ActionChains(driver_chrome)\
        .move_to_element(cabecalho)\
        .pause(2)\
        .perform()

    print("✅ Hover realizado")

    botao_menu = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "[data-testid='visual-more-options-btn']"
            )
        )
    )
    driver_chrome.execute_script(
        "arguments[0].click();",
        botao_menu
    )

    print("✅ Botão Mais opções encontrado")
    time.sleep(1)
    opcao_exportar = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "[data-testid='pbimenu-item.Exportar dados']"
            )
        )
    )

    driver_chrome.execute_script(
        "arguments[0].click();",
        opcao_exportar
    )

    print("✅ Exportar dados clicado")
    time.sleep(2)

    # mapeia os arquivos ja existentes na pasta download
    pasta_download = Path(r"C:\ChromeAutomation\Downloads")

    arquivos_antes = {
        f.name
        for f in pasta_download.glob("*.xlsx")
    }
    # Tenta clicar no botao de download "exportar"
    try:
        # 1. Encontra o botão usando o seletor perfeito (data-testid)
        # Usamos CSS_SELECTOR para buscar exatamente esse atributo
        botao_exportar = driver_chrome.find_element(
            By.CSS_SELECTOR, "[data-testid='export-btn']")

        # 2. Força o clique diretamente via JavaScript
        # Isso ignora completamente a interface gráfica (CSS, Hover, Transparência)
        driver_chrome.execute_script("arguments[0].click();", botao_exportar)

        print("✅ Botão de exportação clicado via JavaScript!")
        time.sleep(2)

    except Exception as e:
        print(f"Erro ao forçar o clique de exportação: {e}")
    # Espera timeout segundos pelo arquivo

    timeout = 360  # 6 minutos
    inicio = time.time()

    while time.time() - inicio < timeout:

        arquivos_agora = {
            f.name
            for f in pasta_download.glob("*.xlsx")
        }

        novos = arquivos_agora - arquivos_antes

        if novos:
            arquivo_baixado = novos.pop()
            print(f"✅ Download concluído: {arquivo_baixado}")
            # caminho completo do arquivo baixado
            arquivo_origem = pasta_download / arquivo_baixado
            hoje = datetime.today()

            novo_nome = (
                f"{nome_arquivo}."
                f"{hoje.month:02d}."
                f"{hoje.year}.xlsx"
            )
            # pasta destino
            pasta_destino = Path(
                r"T:\ATENDIMENTO\BEES DELIVERY\LOG.CO\2026"
            )
            arquivo_destino = pasta_destino / novo_nome
            # se já existir um arquivo com esse nome, remove
            if arquivo_destino.exists():
                arquivo_destino.unlink()
            # move e renomeia ao mesmo tempo
            shutil.move(
                str(arquivo_origem),
                str(arquivo_destino)
            )
            print(
                f"✅ Arquivo movido para: {arquivo_destino}"
            )
            break

        time.sleep(2)

    else:
        raise TimeoutError(
            "Download não encontrado após 6 minutos."
        )
