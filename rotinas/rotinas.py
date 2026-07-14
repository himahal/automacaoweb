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
from . import r0105070402

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

def aguardar_processamento_e_botao(driver, wait_obj, by, identificador, timeout_segundos=300):
    """Aguarda um elemento ficar presente enquanto fecha janelas 'Processando' do Windows e mede o tempo."""
    print(f"⏳ Aguardando até {timeout_segundos}s pelo elemento {identificador}...")
    inicio = time.time()
    while time.time() - inicio < timeout_segundos:
        # Só tenta matar a janela 'Processando' se já passaram 15 segundos para dar tempo do download iniciar
        if time.time() - inicio > 15:
            try:
                janelas = gw.getWindowsWithTitle('Processando')
                if janelas:
                    for j in janelas:
                        print(f"💥 Janela 'Processando' detectada. Fechando {j.title}...")
                        j.close()
            except Exception:
                pass
        else:
            time.sleep(1)
        
        # Verifica se o elemento já está na tela (mesmo que com is_displayed falso)
        try:
            elementos = driver.find_elements(by, identificador)
            if elementos:
                tempo_decorrido = round(time.time() - inicio, 2)
                print(f"✅ Elemento {identificador} carregado! (Tempo de processamento: {tempo_decorrido}s)")
                return elementos[0]
        except Exception:
            pass
        
        time.sleep(2) # Pausa curta antes de verificar novamente
    
    raise TimeoutError(f"Timeout aguardando {identificador} apos {timeout_segundos} segundos.")


# 🗺️ MAPA DE ROTINAS (Agora os nomes coincidem com os imports acima)
MAPA_ROTINAS = {
    "031120": r031120.executar,
    "030224": r030224.executar,
    "01200147": r01200147.executar,
    "03014701": r03014701.executar,
    "030237": r030237.executar,
    "0105070402": r0105070402.executar,
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
    dir_downloads = os.path.abspath(
        os.path.join(diretorio_base, "..", "downloads"))

    # Na branch v2, vamos forçar o salvamento na própria pasta de downloads para conferência
    dir_final = dir_downloads
    os.makedirs(dir_final, exist_ok=True)

    print(f"📂 Processando arquivo da rotina {prefixo_arquivo}...")
    time.sleep(2)

    # 🌟 CORREÇÃO 2: O asterisco no final garante que ele ache '.csv', '.csv.inf', etc.
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
        # Print extra para você ter certeza de onde ele tentou procurar:
        print(f"🔍 Procurou na pasta: {dir_downloads}")
        return None


def chamar_rotina(driver, wait, codigo):

    print(f"\n" + "🔍" + "-"*30)
    print(f"Buscando lógica para: {codigo}")

    revendas = [
        "Beira Rio",
        "Revalle Juazeiro",
        "Revalle Nordeste",
        "Revalle Bonfim",
        "Revalle P Afonso",
        "Revalle Alagoinhas",
        "Revalle Serrinha"
    ]

    # 🎯 Define a janela principal logo no início
    driver.switch_to.default_content()
    janela_menu = driver.window_handles[0]

    # Buscando a função pelo dicionário
    funcao_rotina = MAPA_ROTINAS.get(codigo)

    if funcao_rotina:
        try:
            print(
                f"🎯 Rotina {codigo} localizada! Iniciando processamento em lote...")

            # 🌟 MUDANÇA AQUI: Removemos o 'for' e passamos a lista 'revendas' inteira
            funcao_rotina(driver, wait, data_inicio,
                          data_fim, janela_menu, revendas)

            print(
                f"\n🏁 Todas as revendas da rotina {codigo} foram processadas com sucesso!")
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
