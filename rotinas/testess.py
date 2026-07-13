import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("🔌 Tentando conectar ao Chrome aberto na porta 9222...")
opcoes = Options()
opcoes.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# Conecta ao navegador aberto!
driver = webdriver.Chrome(options=opcoes)
wait = WebDriverWait(driver, 10)

print("✅ Conectado com sucesso!")

# Tenta encontrar a janela da rotina pelo título
for handle in driver.window_handles:
    driver.switch_to.window(handle)
    if "Relatório do Cliente" in driver.title:
        print(f"🎯 Foco ajustado para a janela: {driver.title}")
        break

try:
    # Garante que está na raiz
    driver.switch_to.default_content()
    
    # PAUSA 1: Antes de abrir o modal
    print("\n" + "="*40)
    input("🛑 PAUSA 1: Olhe o navegador. Vou tentar ABRIR O MODAL agora. Pressione [ENTER] no teclado para executar...")
    
    try:
        print("📍 Executando JS: PY070000TelaUnidades();")
        driver.execute_script("PY070000TelaUnidades();")
    except Exception as e:
        print(f"❌ Erro ao abrir modal via JS. Detalhe técnico:\n{e}")
        print("Tentando o clique nativo do Selenium como plano B...")
        botao_abrir_modal = wait.until(EC.element_to_be_clickable((By.ID, "unidadeMenu2")))
        botao_abrir_modal.click()

    # PAUSA 2: Selecionando a Filial
    print("\n" + "="*40)
    input("🛑 PAUSA 2: O modal abriu? Vou tentar SELECIONAR A FILIAL (Beira Rio) agora. Pressione [ENTER]...")
    
    nome_busca = "BEIRA RIO"
    xpath_filial = f"//td[contains(text(), '{nome_busca}')]"
    
    try:
        linha_filial = wait.until(EC.presence_of_element_located((By.XPATH, xpath_filial)))
        print(f"📍 Achei a filial no HTML! Tag: {linha_filial.tag_name}")
        linha_filial.click()
        print("✅ Cliquei na filial!")
    except Exception as e:
         print(f"❌ Erro ao clicar na filial. Detalhe técnico:\n{e}")
         print("HTML atual da página para debug:")
         print(driver.page_source[:500]) # Mostra o começo do HTML para entendermos onde o robô acha que está

    # PAUSA 3: O clique em Todos
    print("\n" + "="*40)
    input("🛑 PAUSA 3: A tela recarregou? Vou tentar clicar em 'TODOS' agora. Pressione [ENTER]...")
    
    try:
        xpath_checkbox_todos = '//*[@id="dvLstPreferencias"]/ul/li/a/ins[1]'
        checkbox_todos = wait.until(EC.presence_of_element_located((By.XPATH, xpath_checkbox_todos)))
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_todos)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", checkbox_todos)
        print("✅ Opção 'Todos' selecionada com sucesso!")
    except Exception as e:
         print(f"❌ Erro ao clicar em 'Todos'. Detalhe técnico:\n{e}")

except Exception as e_geral:
    print(f"💥 ERRO GERAL NO SCRIPT: {e_geral}")

print("\n🏁 Script de teste finalizado. O navegador continuará aberto.")