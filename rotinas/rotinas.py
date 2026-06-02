import time
import os
from datetime import datetime, timedelta
import pygetwindow as gw

# --- IMPORTAÇÕES DAS ROTINAS (Todas relativas para evitar conflitos) ---
from . import r031120
from . import r030224
from . import r01200147
from . import r03014701  # Ajustado para o padrão
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

def tratar_arquivo_baixado(prefixo_arquivo, nome_personalizado=None, nome_subpasta=""):
    """Localiza o arquivo, renomeia e move para a pasta e subpasta desejadas"""
    
    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    dir_downloads = os.path.join(diretorio_base, "..", "downloads")
    
    # 🌟 NOVIDADE 1: Agora ele aceita criar subpastas dentro de 'relatorios_finalizados'
    dir_final = os.path.join(diretorio_base, "..", "relatorios_finalizados", nome_subpasta)
    
    # Garante que a pasta (e a subpasta) existam
    os.makedirs(dir_final, exist_ok=True)

    print(f"📂 Processando arquivo da rotina {prefixo_arquivo}...")
    time.sleep(2) 
    
    padrao = os.path.join(dir_downloads, f"*{prefixo_arquivo}*.csv.inf")
    arquivos = glob.glob(padrao)

    if arquivos:
        arquivo_original = max(arquivos, key=os.path.getctime)
        nome_base = os.path.basename(arquivo_original)
        
        # 🌟 NOVIDADE 2: Decide o novo nome
        if nome_personalizado:
            # Garante que a extensão seja .csv, caso você esqueça de colocar
            if not nome_personalizado.endswith('.csv'):
                nome_personalizado += '.csv'
            novo_nome = nome_personalizado
        else:
            # Se não passar nome, ele limpa o .inf como fazia antes
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

    # 🎯 Define a janela principal logo no início
    driver.switch_to.default_content()
    janela_menu = driver.window_handles[0]

    # Buscando a função pelo dicionário
    funcao_rotina = MAPA_ROTINAS.get(codigo)

    if funcao_rotina:
        try:
            print(f"🎯 Rotina {codigo} localizada! Iniciando...")
            funcao_rotina(driver, wait, data_inicio, data_fim, janela_menu)
        except Exception as e:
            print(f"💥 Falha na execução da rotina {codigo}: {e}")
        finally:
            # 🏁 FAXINA TOTAL: Garante que o bot não se perca em janelas abertas
            time.sleep(2)
            limpar_ambiente(driver, janela_menu)
    else:
        print(f"❌ ERRO: A rotina {codigo} não está cadastrada.")

    print("-" * 30 + "\n")
