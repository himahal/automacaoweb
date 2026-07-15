import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from pywinauto import Desktop

from fecharPopups import fechar_popups
from . import rotinas


def executar(driver, wait, data_inicio, data_fim, janela_menu, lista_revendas):
    """Lógica específica da rotina 0105070402 (Troca por Modal via JS)"""

    codigo_rotina = "0105070402"
    print(f"\n🚀 Iniciando execução da Rotina {codigo_rotina}...")

    try:
        # ====================================================================
        # FASE 1: SETUP E ABERTURA DA JANELA
        # ====================================================================
        print("Retornando ao frame de comandos...")
        driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))

        print("📂 Entrando no IframeMenu...")
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

        # ====================================================================
        # FASE 2: O LOOP DE REVENDAS
        # ====================================================================
        for indice, revenda in enumerate(lista_revendas):
            print(f"\n{'='*40}")
            print(
                f"🔄 PROCESSANDO FILIAL [{indice + 1}/{len(lista_revendas)}]: {revenda}")
            print(f"{'='*40}")

            try:
                # Garante que estamos na raiz da página
                driver.switch_to.default_content()
                time.sleep(1)

                # --- 2.1 TROCA DE REVENDA PELO PAINEL MODAL ---
                print("📍 Abrindo painel modal de unidades via Chave Mestra (JS)...")
                driver.execute_script("PY070000TelaUnidades();")

                print("⏳ Aguardando o modal renderizar...")
                time.sleep(1.5)

                # Tradutor de nomes para o padrão do Promax
                nome_busca = revenda.split("-")[-1].strip().upper()
                if "REVALLE" in revenda.upper() and "-" not in revenda:
                    cidade = revenda.upper().replace("REVALLE", "").strip()
                    nome_busca = f"REVALLE - {cidade}"
                elif "BEIRA RIO" in revenda.upper():
                    nome_busca = "BEIRA RIO"

                print(f"📍 Buscando a filial '{nome_busca}' na lista...")

                xpath_filial = f"//td[contains(text(), '{nome_busca}')]"

                # 🌟 CORREÇÃO CRUCIAL: Voltamos para presence_of_element_located (igual ao teste)
                linha_filial = wait.until(
                    EC.presence_of_element_located((By.XPATH, xpath_filial)))

                # Clique físico simulado direto no elemento encontrado
                linha_filial.click()
                print(f"✅ Filial {nome_busca} selecionada no modal!")

                # --- 2.2 PREENCHIMENTO DE CAMPOS (Árvore jsTree) ---
                print(
                    "⏳ Aguardando a página recarregar a árvore de opções após a troca...")
                # Respiro OBRIGATÓRIO para evitar o erro de JavaScript
                time.sleep(2)

                print(
                    "🎯 Buscando a caixa de seleção 'Todos' na árvore de Preferências...")
                xpath_checkbox_todos = '//*[@id="dvLstPreferencias"]/ul/li/a/ins[1]'

                checkbox_todos = wait.until(
                    EC.presence_of_element_located((By.XPATH, xpath_checkbox_todos)))
                driver.execute_script(
                    "arguments[0].scrollIntoView(true);", checkbox_todos)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", checkbox_todos)
                print("✅ Opção 'Todos' selecionada com sucesso!")

                # --- 2.3 GERAÇÃO E CAPTURA DO ALERTA ---
                print("🖱️ Clicando em Gerar CSV...")
                botaoCSV = driver.find_element(By.ID, "btnGerarCSV")
                botaoCSV.click()

                print("⏳ Aguardando o servidor processar e gerar o CSV...")

                try:
                    alerta_sucesso = WebDriverWait(
                        driver, 500).until(EC.alert_is_present())
                    texto_alerta = alerta_sucesso.text
                    alerta_sucesso.accept()
                    print(f"✅ Sucesso! Promax avisou: '{texto_alerta}'")
                except Exception:
                    print(
                        "⚠️ Aviso: O alerta de sucesso não apareceu em 15s. Indo direto para a captura do download...")

                # --- CONFIRMAÇÃO DO DOWNLOAD (Nativo do Windows via PyWinAuto) ---
                from rotinas.utils_ui import confirmar_download_ie
                confirmar_download_ie(driver)

                # --- 2.5 TRATAMENTO DO ARQUIVO BAIXADO ---
                time.sleep(10)

                nome_dinamico = f"{revenda}"

                print(f"🏷️ Nome dinâmico gerado: {nome_dinamico}.csv")
                rotinas.tratar_arquivo_baixado(
                    prefixo_arquivo="PY",
                    nome_personalizado=nome_dinamico,
                    caminho_destino=r"T:\ATENDIMENTO\BEES DELIVERY\01.05.07.04.02"
                )

            except Exception as inner_e:
                print(
                    f"❌ Erro crítico ao processar a filial {revenda}: {inner_e}")
                print("⏭️ Pulando para a próxima revenda da lista...")
                continue

    except Exception as e:
        print(f"❌ Erro fatal na rotina {codigo_rotina} (Fase de Setup): {e}")
