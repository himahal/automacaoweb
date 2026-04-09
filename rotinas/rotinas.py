from datetime import datetime, timedelta
import time

# Importações de rotinas
from . import r031120
from . import r030224
from . import r01200147
# from . import r050505  <-- Próximas rotinas entram aqui

# --- CÁLCULO DAS DATAS  ---
hoje = datetime.now()
data_inicio = hoje.replace(day=1).strftime("%d/%m/%Y")
data_fim = (hoje - timedelta(days=1)).strftime("%d/%m/%Y")

# 🗺️ MAPA DE ROTINAS
# Colocar mais rotinas aqui se precisar
MAPA_ROTINAS = {
    "031120": r031120.executar,
    "030224": r030224.executar,
    "01200147": r01200147.executar,
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