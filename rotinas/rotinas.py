from datetime import datetime, timedelta

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

def chamar_rotina(driver, wait, codigo):

    print(f"\n" + "🔍" + "-"*30)
    print(f"Buscando lógica para: {codigo}")

    janela_menu = driver.window_handles[0]
    
    # Buscando a função pelo dicionário
    funcao_rotina = MAPA_ROTINAS.get(codigo)

    if funcao_rotina:
        print(f"🎯 Rotina {codigo} localizada! Iniciando execução...")
        # Chamamos a função encontrada passando os parâmetros necessários
        funcao_rotina(driver, wait, data_inicio, data_fim, janela_menu)
        print(f"✅ Execução da rotina {codigo} concluída.")
    else:
        print(f"❌ ERRO: A rotina {codigo} não está cadastrada no MAPA_ROTINAS.")
        print("Verifique se o código está correto ou se o arquivo foi importado.")
    
    print("-"*30 + "\n")