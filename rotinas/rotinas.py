import time
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