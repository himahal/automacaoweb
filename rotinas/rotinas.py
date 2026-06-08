import time
import os
import glob
import shutil
from datetime import datetime, timedelta
import pygetwindow as gw

# --- IMPORTAÇÕES DAS ROTINAS (Todas relativas para evitar conflitos) ---
from . import r031120
from . import r030224
from . import r01200147
from . import r03014701
from . import r030237

# --- CÁLCULO DAS DATAS ---
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
    print("🎯 Caçando janelas 'Processando' no sistema...")
    try:
        # Busca janelas que contenham o texto no título
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


# 🗺️ MAPA DE ROTINAS (Agora os nomes coincidem com os imports acima)
MAPA_ROTINAS = {
    "031120": r031120.executar,
    "030224": r030224.executar,
    "01200147": r01200147.executar,
    "03014701": r03014701.executar,
    "030237": r030237.executar,
}


def limpar_ambiente(driver, janela_menu):
    """Fecha todas as janelas que não são o menu principal"""
    print("\n🧹 Iniciando faxina de janelas secundárias...")
    todas_janelas = driver.window_handles

    for janela in todas_janelas:
        if janela != janela_menu:
            try:
                driver.switch_to.window(janela)
                print(f"❌ Fechando janela: {driver.title}")
                driver.close()
            except:
                pass

    # Retorna o controle para a principal
    driver.switch_to.window(janela_menu)
    driver.switch_to.default_content()
    print("✨ Ambiente limpo e pronto para a próxima!")


def tratar_arquivo_baixado(prefixo_arquivo, nome_personalizado=None, caminho_destino=None):
    """Localiza o arquivo, renomeia e move para a pasta desejada no computador"""

    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    dir_downloads = os.path.join(diretorio_base, "..", "downloads")

    # 🌟 NOVIDADE: Agora ele aceita qualquer caminho do seu computador
    if caminho_destino:
        dir_final = caminho_destino
    else:
        dir_final = os.path.join(diretorio_base, "..",
                                 "relatorios_finalizados")

    # Garante que a pasta exista (cria a árvore de pastas se não existir)
    os.makedirs(dir_final, exist_ok=True)

    print(f"📂 Processando arquivo da rotina {prefixo_arquivo}...")
    time.sleep(2)

    padrao = os.path.join(dir_downloads, f"*{prefixo_arquivo}*.csv.inf")
    arquivos = glob.glob(padrao)

    if arquivos:
        arquivo_original = max(arquivos, key=os.path.getctime)
        nome_base = os.path.basename(arquivo_original)

        # Decide o novo nome
        if nome_personalizado:
            if not nome_personalizado.endswith('.csv'):
                nome_personalizado += '.csv'
            novo_nome = nome_personalizado
        else:
            novo_nome = nome_base.replace(".inf", "")

        caminho_final = os.path.join(dir_final, novo_nome)

        # Se já existir um arquivo com esse nome exato, substitui
        if os.path.exists(caminho_final):
            os.remove(caminho_final)

        shutil.move(arquivo_original, caminho_final)
        print(f"✅ Arquivo renomeado para: {novo_nome}")
        print(f"📁 Salvo em: {dir_final}")
        return caminho_final
    else:
        print(f"⚠️ Nenhum arquivo encontrado com o padrão: {prefixo_arquivo}")
        return None


def chamar_rotina(driver, wait, codigo):

    print(f"\n" + "🔍" + "-"*30)
    print(f"Buscando lógica para: {codigo}")

    revendas = [
        "145.0004 - BEIRA RIO",
        "156.0001 - REVALLE - JUAZEIRO",
        "156.0002 - REVALLE - NORDESTE",
        "156.0003 - REVALLE - SR. BONFIM",
        "304.0005 - REVALLE - P AFONSO",
        "341.0006 - REVALLE - ALAGOINHAS",
        "341.0007 - REVALLE - SERRINHA"
    ]

    # 🎯 Define a janela principal logo no início
    driver.switch_to.default_content()
    janela_menu = driver.window_handles[0]

    # Buscando a função pelo dicionário
    funcao_rotina = MAPA_ROTINAS.get(codigo)

    if funcao_rotina:
        try:
            print(f"🎯 Rotina {codigo} localizada! Iniciando processamento em lote...")
            
            # 🌟 MUDANÇA AQUI: Removemos o 'for' e passamos a lista 'revendas' inteira
            funcao_rotina(driver, wait, data_inicio, data_fim, janela_menu, revendas)
            
            print(f"\n🏁 Todas as revendas da rotina {codigo} foram processadas com sucesso!")
        except Exception as e:
            print(f"💥 Falha na execução da rotina {codigo}: {e}")
        finally:
            # 🏁 FAXINA TOTAL: Garante que o bot não se perca em janelas abertas
            time.sleep(2)
            limpar_ambiente(driver, janela_menu)
    else:
        print(f"❌ ERRO: A rotina {codigo} não está cadastrada.")

    codigoRotina = MAPA_ROTINAS

    print(f"✅ Rotina {codigoRotina} finalizada!")
    # driver.close()  # Fecha a janela atual
    # driver.switch_to.window(janela_menu)  # Volta para a janela do menu

    print("-" * 30 + "\n")
