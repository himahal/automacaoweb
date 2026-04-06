import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta

# --- CÁLCULO DAS DATAS ---
hoje = datetime.now()
# Primeiro dia do mês atual (01/MM/2026)
data_inicio = hoje.replace(day=1).strftime("%d/%m/%Y")
# Ontem (Dia anterior ao atual)
data_fim = (hoje - timedelta(days=1)).strftime("%d/%m/%Y")

print(f"📅 Definindo período: {data_inicio} até {data_fim}")

from configlinux import obter_config_ie
from fecharPopups import fechar_popups

login = "pizolitto"
senha = "Nerd12lol"
rotina = "031120"

def realizar_automacao():
    # --- 2. CARREGA AS CONFIGURAÇÕES DO IE ---
    service, options = obter_config_ie()

    try:
        print("🚀 Iniciando motor Selenium (Internet Explorer)...")
        
        # --- 3. INICIALIZAÇÃO DO NAVEGADOR ---
        # Trocamos Chrome por Ie para bater com o driver que você baixou
        driver = webdriver.Ie(service=service, options=options)
        
        driver.maximize_window()
        
        # Aumentamos o tempo para 30s por segurança, já que o IE pode ser lento
        wait = WebDriverWait(driver, 30)

        print("🌐 Acessando Revalle/Promax...")
        driver.get("https://revalle.promaxcloud.com.br/pw/")

        # LÓGICA DE LOGIN
        print("📥 Entrando no frame de login...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "frame")))

        # Tela de login
        print(f"🔑 Preenchendo login para '{login}'...")
        # No IE, 'visibility_of' funciona melhor que 'presence_of' para evitar erros de foco
        campo_user = wait.until(EC.visibility_of_element_located((By.NAME, "Usuario")))
        campo_user.send_keys(login)
        
        driver.find_element(By.NAME, "Senha").send_keys(senha)
        driver.find_element(By.ID, "BtnConfirm").click()

        print("✅ Login efetuado! Voltando ao contexto principal...")
        driver.switch_to.default_content()

        # Selecionar a revenda e confirmar
        print("Mudando para o frame de confirmação...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))
        
        botao_confirma = wait.until(EC.element_to_be_clickable((By.NAME, "cmdConfirma")))
        botao_confirma.click()

        # Fechar PopUps
        fechar_popups(driver, max_popups_to_check=4)
        driver.switch_to.default_content()

        # Inserir rotina
        print("Retornando ao frame de comandos...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))
        
        print("📂 Entrando no IframeMenu...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameMenu")))
        
        print(f"⌨️ Inserindo a rotina: {rotina}")
        botao_rotina = wait.until(EC.visibility_of_element_located((By.ID, "atalho")))
        botao_rotina.clear()
        botao_rotina.send_keys(rotina)

        # Botão OK da rotina
        botao_ok = driver.find_element(By.XPATH, '//*[@id="atal"]/div[1]/table/tbody/tr[2]/td/input[2]')
        botao_ok.click()

        print("⏳ Aguardando carregamento da rotina...")
        # 1. Volta para o topo da página para limpar frames anteriores
        driver.switch_to.default_content()

        # 1. Pega todas as janelas abertas
        janela_principal = driver.current_window_handle

    # Espera até que 2 janelas estejam abertas (Sua lógica perfeita)
        wait.until(EC.number_of_windows_to_be(2)) 

        janelas = driver.window_handles

        for janela in janelas:
            if janela != janela_principal:
                driver.switch_to.window(janela)
                # Pausa de 1s para o Windows terminar de carregar o processo da janela
                time.sleep(1) 
                print(f"🔀 Mudamos para a nova janela: {driver.title}")
                break
        # 2. Entra no frame 'rotina' (visto na sua image_c67283.png)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "rotina")))

        print("🎯 Localizando o campo 'Classificação'...")

        # 3. Localiza o select (usando o nome 'opcaoRel' que é mais seguro que o XPath longo)
        dropdown_element = wait.until(EC.presence_of_element_located((By.NAME, "opcaoRel")))
        print("🎯 Dropdown localizado! Selecionando 'Mapa'")
        # 4. Tentando interagir com o dropdown

        driver.execute_script("""
            var select = arguments[0];
            var textoParaSelecionar = "Mapa";
            
            for (var i = 0; i < select.options.length; i++) {
                // Usamos replace com Regex para limpar espaços, já que o IE não tem .trim()
                var textoOption = select.options[i].text.replace(/^\s+|\s+$/g, '');
                
                if (textoOption === textoParaSelecionar) {
                    select.selectedIndex = i;
                    
                    // Dispara o evento de mudança (padrão antigo para IE)
                    if ("createEvent" in document) {
                        var evt = document.createEvent("HTMLEvents");
                        evt.initEvent("change", false, true);
                        select.dispatchEvent(evt);
                    } else if ("fireEvent" in select) {
                        select.fireEvent("onchange");
                    }
                    break;
                }
            }
        """, dropdown_element)

        print("✅ Opção selecionada!")  

        # 1. Preencher Data Inicial
        campo_data_ini = wait.until(EC.presence_of_element_located((By.NAME, "dataInicial")))
        print("🎯 Campo de data inicial localizado!")
        # Injetamos o valor direto no atributo 'value' para evitar o erro de HTMLFormElement
        driver.execute_script("arguments[0].value = arguments[1];", campo_data_ini, data_inicio)
        print(f"✅ Data inicial ({data_inicio}) preenchida!")

        # 2. Preencher Data Final
        campo_data_fim = wait.until(EC.presence_of_element_located((By.NAME, "dataFinal")))
        driver.execute_script("arguments[0].value = arguments[1];", campo_data_fim, data_fim)
        print(f"✅ Data final ({data_fim}) preenchida!")

# --- 3. CLICAR EM VISUALIZAR ---
        print("🖱️ Clicando em Visualizar...")
        # No IE, SEMPRE use JavaScript para clicar em botões de formulário se o .click() falhar
        try:
            # Tenta localizar pelo NAME que você usou, mas se falhar, o ID no print parece ser 'Visualizar'
            btn_visualizar = wait.until(EC.element_to_be_clickable((By.NAME, "BotVisualizar")))
            driver.execute_script("arguments[0].click();", btn_visualizar)
        except:
            # Caso o NAME esteja errado, tentamos pelo texto do botão (Visualizar)
            btn_visualizar = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/button")
            driver.execute_script("arguments[0].click();", btn_visualizar)

        print("🚀 Relatório solicitado!")

        print("⏳ Aguardando a geração do relatório (terceira janela)...")

        # 1. Espera até que existam 3 janelas abertas

        # 2. Pega todos os IDs e pula para a última janela aberta
        time.sleep(10)
        # 1. Lista todas as janelas
        janelas = driver.window_handles
        print(f"🗔 Janelas abertas detectadas: {len(janelas)}")

        # 2. Vamos testar cada uma até achar a que tem frames
        encontrou_relatorio = False
        for h in janelas:
            driver.switch_to.window(h)
            driver.switch_to.default_content()

            # Verificamos se ESSA janela tem frames
            frames_na_janela = driver.find_elements(By.TAG_NAME, "frame")
            if len(frames_na_janela) > 0:
                print(f"🎯 Achei! Esta é a janela do relatório (Frames: {len(frames_na_janela)})")
                encontrou_relatorio = True
                break

        if not encontrou_relatorio:
            print("⚠️ Não achei a janela com frames. Talvez ela ainda esteja carregando...")
            # Como plano B, voltamos para a última, mas o loop acima é mais seguro
            driver.switch_to.window(janelas[-1])

        print("🔎 LISTANDO TODOS OS FRAMES DA PÁGINA (RAIZ)...")
        # --- Esperar ---
        input("\n[Pressione ENTER para encerrar o bot e fechar as janelas]")

    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    realizar_automacao()