import time
import os
import glob
import shutil
from datetime import datetime, timedelta
import pygetwindow as gw

from . import r030224

hoje = datetime.now()
if hoje.day == 1:
    primeiro_dia_mes_atual = hoje.replace(day=1)
    primeiro_dia_mes_anterior = (
        primeiro_dia_mes_atual - timedelta(days=1)
    ).replace(day=1)

    data_inicio = primeiro_dia_mes_anterior.strftime("%d/%m/%Y")
    data_fim = (hoje - timedelta(days=1)).strftime("%d/%m/%Y")
else:
    data_inicio = hoje.replace(day=1).strftime("%d/%m/%Y")
    data_fim = (hoje - timedelta(days=1)).strftime("%d/%m/%Y")


JANELA_MENU = None


def matar_overlay_processando(driver):
    """Fecha a janela 'Processando' via Windows (gw)"""
    print("🎯 Procurando janelas 'Processando' no sistema...")
    try:
        janelas = gw.getWindowsWithTitle('Processando')

        if janelas:
            for j in janelas:
                titulo = j.title.lower()
                if "edge" in titulo and (j.width > 600 or j.height > 500):
                    print(f"🛡️ Ignorando janela principal do navegador: {j.title}")
                    continue
                print(f"💥 Janela encontrada: {j.title}. Fechando...")
                j.close()
            print("✅ Processo(s) encerrado(s) com sucesso!")
        else:
            print("💡 Nenhuma janela 'Processando' detectada.")

    except Exception as e:
        print(f"⚠️ Erro ao tentar fechar janela via Windows: {e}")


def aguardar_processamento_e_botao(driver, wait_obj, by, identificador, timeout_segundos=300):
    """Aguarda um elemento ficar presente enquanto fecha janelas 'Processando' do Windows e mede o tempo."""
    print(f"⏳ Aguardando até {timeout_segundos}s pelo elemento {identificador}...")
    inicio = time.time()
    while time.time() - inicio < timeout_segundos:
        if time.time() - inicio > 15:
            try:
                janelas = gw.getWindowsWithTitle('Processando')
                if janelas:
                    for j in janelas:
                        titulo = j.title.lower()
                        if "edge" in titulo and (j.width > 600 or j.height > 500):
                            continue
                        print(f"💥 Janela 'Processando' detectada. Fechando {j.title}...")
                        j.close()
            except Exception:
                pass
        else:
            time.sleep(1)

        try:
            elementos = driver.find_elements(by, identificador)
            if elementos:
                tempo_decorrido = round(time.time() - inicio, 2)
                print(f"✅ Elemento {identificador} carregado! (Tempo: {tempo_decorrido}s)")
                return elementos[0]
        except Exception:
            pass

        time.sleep(2)

    raise TimeoutError(f"Timeout aguardando {identificador} apos {timeout_segundos} segundos.")


MAPA_ROTINAS = {
    "030224": r030224.executar,
}


def limpar_ambiente(driver, janela_menu):
    """Fecha todas as janelas que não são o menu principal"""
    print("\n🧹 Fechando janelas secundárias...")
    todas_janelas = driver.window_handles

    for janela in todas_janelas:
        if janela != janela_menu:
            try:
                driver.switch_to.window(janela)
                print(f"❌ Fechando janela: {driver.title}")
                driver.close()
            except:
                pass

    driver.switch_to.window(janela_menu)
    driver.switch_to.default_content()
    print("✨ Ambiente limpo.")


def tratar_arquivo_baixado(prefixo_arquivo, nome_personalizado=None, caminho_destino=None):
    """Localiza o arquivo, renomeia e move para a pasta desejada"""

    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    dir_downloads = os.path.abspath(
        os.path.join(diretorio_base, "..", "downloads"))

    dir_final = caminho_destino if caminho_destino else dir_downloads
    os.makedirs(dir_final, exist_ok=True)

    print(f"📂 Processando arquivo da rotina {prefixo_arquivo}...")

    inicio_espera = time.time()
    while time.time() - inicio_espera < 90:
        parciais = (
            glob.glob(os.path.join(dir_downloads, "*.partial")) +
            glob.glob(os.path.join(dir_downloads, "*.crdownload")) +
            glob.glob(os.path.join(dir_downloads, "*.tmp"))
        )
        parciais_rotina = [f for f in parciais if prefixo_arquivo in os.path.basename(f)]
        if not parciais_rotina:
            break
        print("⏳ Aguardando conclusão do download...")
        time.sleep(1)

    time.sleep(2)

    padrao = os.path.join(dir_downloads, f"*{prefixo_arquivo}*.csv*")
    arquivos = glob.glob(padrao)

    if arquivos:
        arquivo_original = max(arquivos, key=os.path.getctime)
        nome_base = os.path.basename(arquivo_original)

        if nome_personalizado:
            if not nome_personalizado.endswith('.csv'):
                nome_personalizado += '.csv'
            novo_nome = nome_personalizado
        else:
            novo_nome = nome_base.replace(".inf", "")

        caminho_final = os.path.join(dir_final, novo_nome)

        if os.path.exists(caminho_final):
            os.remove(caminho_final)

        shutil.move(arquivo_original, caminho_final)
        print(f"✅ Arquivo renomeado para: {novo_nome}")
        print(f"📁 Salvo em: {dir_final}")
        return caminho_final
    else:
        print(f"⚠️ Nenhum arquivo encontrado com o padrão: {prefixo_arquivo}")
        print(f"🔍 Procurou na pasta: {dir_downloads}")
        return None


def chamar_rotina(driver, wait, codigo):

    print(f"\n" + "🔍" + "-"*30)
    print(f"Buscando lógica para: {codigo}")

    unidades = [
        "Beira Rio",
        "Juazeiro",
        "Nordeste",
        "Bonfim",
        "Paulo Afonso",
        "Alagoinhas",
        "Serrinha"
    ]

    time.sleep(2)

    global JANELA_MENU
    if JANELA_MENU is None:
        JANELA_MENU = driver.current_window_handle
        print(f"🔒 Janela principal (Menu) registrada com handle: {JANELA_MENU}")
    else:
        try:
            driver.switch_to.window(JANELA_MENU)
            print(f"🔄 Retornamos para a janela principal (Menu) registrada: {JANELA_MENU}")
        except Exception as e:
            print(f"⚠️ Erro ao focar na janela registrada ({e}). Redefinindo handle...")
            JANELA_MENU = driver.window_handles[0]
            driver.switch_to.window(JANELA_MENU)

    try:
        from pywinauto import Application
        import re
        titulo_seguro = re.escape(driver.title)
        app = Application(backend="win32").connect(title_re=f".*{titulo_seguro}.*", timeout=5)
        app.window(title_re=f".*{titulo_seguro}.*").set_focus()
        print("🎯 Foco da janela principal (Menu) restaurado via win32!")
    except Exception as e_foco:
        print(f"⚠️ Erro ao focar na janela do menu principal: {e_foco}")

    try:
        alert = driver.switch_to.alert
        print(f"🚨 Alerta residual detectado e aceito na janela principal: '{alert.text}'")
        alert.accept()
        time.sleep(1)
    except:
        pass

    driver.switch_to.default_content()
    janela_menu = JANELA_MENU

    funcao_rotina = MAPA_ROTINAS.get(codigo)

    if funcao_rotina:
        try:
            print(f"🎯 Rotina {codigo} localizada! Iniciando processamento em lote...")
            funcao_rotina(driver, wait, data_inicio, data_fim, janela_menu, unidades)
            print(f"\n🏁 Todas as unidades da rotina {codigo} foram processadas com sucesso!")
        except Exception as e:
            print(f"💥 Falha na execução da rotina {codigo}: {e}")
        finally:
            time.sleep(2)
            limpar_ambiente(driver, janela_menu)
    else:
        print(f"❌ ERRO: A rotina {codigo} não está cadastrada.")

    print(f"✅ Rotina {codigo} finalizada!")
    print("-" * 30 + "\n")
