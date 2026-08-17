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


def matar_overlay_processando(driver):
    """Fecha a janela 'Processando' via Windows (gw)"""
    print("🎯 Procurando janelas 'Processando' no sistema...")
    try:
        janelas = gw.getWindowsWithTitle('Processando')

        if janelas:
            for j in janelas:
                print(f"💥 Janela encontrada: {j.title}. Fechando agora...")
                j.close()
            print("✅ Processo(s) encerrado(s) com sucesso!")
        else:
            print("💡 Nenhuma janela 'Processando' detectada no momento.")

    except Exception as e:
        print(f"⚠️ Erro ao tentar fechar janela via Windows: {e}")


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
    """Localiza o arquivo, renomeia e move para a pasta desejada no computador"""

    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    dir_downloads = os.path.abspath(
        os.path.join(diretorio_base, "..", "downloads"))

    if caminho_destino:
        dir_final = caminho_destino
    else:
        dir_final = os.path.join(diretorio_base, "relatorios_finalizados")

    os.makedirs(dir_final, exist_ok=True)

    print(f"📂 Processando arquivo da rotina {prefixo_arquivo}...")
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

    driver.switch_to.default_content()
    janela_menu = driver.window_handles[0]

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
