import time
import os
import glob
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.ie.options import Options
from selenium.webdriver.ie.service import Service
import os
import shutil
from datetime import datetime
from pathlib import Path

# Tenta importar AutoIt para manipular diálogos/barras do IE via UI nativa
try:
    import autoit  # type: ignore[reportMissingImports]
    AUTOIT_AVAILABLE = True
except Exception:
    AUTOIT_AVAILABLE = False

# importar arquivos
#from fecharPopups import fechar_popups
#from configlinux import obter_config_ie

login = "pizolitto"
senha = "Nerd12lol"
rotina = "01.20.01.47"
dir_downloads = str(Path.home() / "Downloads")
DOWNLOAD_TARGET_DIR = str(Path.home() / "Documents" / "Projetos" / "Revalle" / "PRODUTIVIDADE" / "BEES DELIVERY" / "01.20.01.47")
MAIN_WINDOW_HANDLE = None

def fechar_popups(driver_instance, max_popups_to_check=5, wait_timeout_per_popup=5):
    """
    Fecha alertas JS, confirms e prompts.
    Funciona melhor com Internet Explorer / Promax.
    """

    popups_fechados = 0

    for i in range(max_popups_to_check):

        try:
            print(f"🔎 Verificando popup {i+1}...")

            WebDriverWait(driver_instance, wait_timeout_per_popup).until(
                EC.alert_is_present()
            )

            alerta = driver_instance.switch_to.alert

            try:
                print(f"⚠️ Texto do alerta: {alerta.text}")
            except:
                print("⚠️ Alerta sem texto")

            alerta.accept()

            popups_fechados += 1

            print(f"✅ Popup {i+1} fechado")

            time.sleep(1.5)

        except TimeoutException:
            print("✔ Nenhum popup encontrado")
            break

        except Exception as e:
            print(f"❌ Erro ao fechar popup: {e}")
            break

    print(f"✅ Total fechados: {popups_fechados}\n")

    return popups_fechados

def wait_and_switch_to_new_window(driver, timeout: int = 5) -> bool:
    """
    Aguarda surgir uma nova janela e alterna o foco para ela.
    Retorna True se trocou para a nova janela, False se não surgiu.
    """
    try:
        initial_handles = set(driver.window_handles)
        end_time = time.time() + timeout
        while time.time() < end_time:
            current_handles = set(driver.window_handles)
            new_handles = current_handles - initial_handles
            if new_handles:
                new_handle = list(new_handles)[0]
                driver.switch_to.window(new_handle)
                # Garante que estamos no conteúdo principal da nova janela
                try:
                    driver.switch_to.default_content()
                except Exception:
                    pass
                print("[INFO] Nova janela detectada e foco alternado.")
                return True
            time.sleep(0.5)
        print("[WARN] Nenhuma nova janela detectada dentro do timeout.")
        return False
    except Exception as e:
        print(f"[ERRO] Ao alternar para nova janela: {e}")
        return False

def obter_config_ie():

    # --- 1. CAMINHOS ---
    base_path = Path(__file__).resolve().parent.parent

    log_path = os.path.join(base_path, "iedriver.log")
    #print(str(base_path));

    ie_driver_path = str(base_path / "IEDriverServer.exe")

    # --- 2. OPÇÕES DO IE ---
    options = Options()

    options.ignore_protected_mode_settings = True
    options.ignore_zoom_level = True
    options.require_window_focus = False

    # --- 3. SERVICE ---
    service = Service(
        executable_path=ie_driver_path,
        log_output=log_path
    )

    return service, options

def close_new_windows_since(driver, handles_before: set):
    """
    Fecha todas as janelas abertas após a referência handles_before, mantendo o foco na mais antiga conhecida.
    """
    try:
        current = set(driver.window_handles)
        extra = list(current - handles_before)
        for h in extra:
            try:
                driver.switch_to.window(h)
                driver.close()
            except Exception:
                pass
        # retorna foco à janela conhecida mais antiga (MAIN_WINDOW_HANDLE se definido; caso contrário, uma de handles_before)
        target = None
        global MAIN_WINDOW_HANDLE
        if MAIN_WINDOW_HANDLE and MAIN_WINDOW_HANDLE in handles_before:
            target = MAIN_WINDOW_HANDLE
        else:
            target = list(handles_before)[0] if handles_before else (driver.window_handles[0] if driver.window_handles else None)
        if target:
            try:
                driver.switch_to.window(target)
                driver.switch_to.default_content()
            except Exception:
                pass
        print("[INFO] Janelas extras recentes fechadas.")
    except Exception as e:
        print(f"[WARN] Falha ao fechar janelas recentes: {e}")

def selecionar_numerica_e_visualizar(driver, wait_timeout: int = 20):
    """
    Seleciona a opção 'numerica' no select name=opcaoRel e clica no botão Visualizar.
    Aguarda o carregamento da nova página (ou nova janela) e salva o HTML.
    """
    try:
        # Garante foco no conteúdo principal primeiro
        try:
            driver.switch_to.default_content()
        except Exception:
            pass

        wait = WebDriverWait(driver, wait_timeout)

        # Entrar no frame correto: prioriza frame 'rotina'; se não existir, tenta encontrar o frame que contém 'opcaoRel'
        def switch_to_frame_with_element(by, value) -> bool:
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
            # 1) Tenta frame com nome 'rotina'
            try:
                driver.switch_to.frame("rotina")
                if driver.find_elements(by, value):
                    return True
            except Exception:
                try:
                    driver.switch_to.default_content()
                except Exception:
                    pass
            # 2) Tenta iterar todos os frames de primeiro nível e procurar o elemento
            try:
                frames = driver.find_elements(By.TAG_NAME, "frame")
            except Exception:
                frames = []
            for idx in range(len(frames)):
                try:
                    driver.switch_to.default_content()
                    driver.switch_to.frame(idx)
                    if driver.find_elements(by, value):
                        return True
                except Exception:
                    continue
            # 3) Não encontrou
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
            return False

        # Localiza o select
        # Garante que estamos no frame que possui o select
        encontrou_frame = switch_to_frame_with_element(By.NAME, "opcaoRel")
        if not encontrou_frame:
            raise Exception("Select 'opcaoRel' não encontrado em nenhum frame")
        select_el = wait.until(EC.presence_of_element_located((By.NAME, "opcaoRel")))

        # Primeiro tenta usar Select nativo
        selecionado = False
        try:
            sel = Select(select_el)
            for opt in sel.options:
                if (opt.text or "").strip().lower() == "numerica" or (opt.get_attribute("value") or "").strip().lower() == "numerica":
                    sel.select_by_visible_text(opt.text)
                    selecionado = True
                    break
        except Exception:
            selecionado = False

        # Se falhar (IE tem limitações), usa JS
        if not selecionado:
            driver.execute_script("""
                function _trimIE(s){ return (s||'').toString().replace(/^\\s+|\\s+$/g, ''); }
                var sel = document.getElementsByName('opcaoRel')[0];
                if (!sel) return;
                var alvo = null;
                for (var i=0; i<sel.options.length; i++){
                    var t = _trimIE(sel.options[i].text||'').toLowerCase();
                    var v = _trimIE(sel.options[i].value||'').toLowerCase();
                    if (t === 'numerica' || v === 'numerica'){ alvo = i; break; }
                }
                if (alvo !== null){
                    sel.selectedIndex = alvo;
                    if (typeof sel.onchange === 'function'){ sel.onchange(); }
                }
            """)

        # Primeiro: clique via JavaScript direto no botão com name/id 'BotVisualizar' (abordagem usada antes)
        clicou = False
        try:
            driver.execute_script("""
                (function(){
                    function _trimIE(s){ return (s||'').toString().replace(/^\\s+|\\s+$/g, ''); }
                    function _byNameCI(n){
                        var all=document.getElementsByTagName('*'), ln=(n||'').toLowerCase();
                        for(var i=0;i<all.length;i++){
                            var nm=(all[i].name||'').toLowerCase();
                            if(nm===ln){ return all[i]; }
                        }
                        return null;
                    }
                    var btn = document.getElementsByName('BotVisualizar')[0]
                              || document.getElementById('BotVisualizar')
                              || _byNameCI('BotVisualizar');
                    if (btn){
                        if (typeof btn.click === 'function'){ btn.click(); return true; }
                        if (typeof btn.onclick === 'function'){ btn.onclick(); return true; }
                        // Último recurso: submit do form
                        if (btn.form && typeof btn.form.submit === 'function'){ btn.form.submit(); return true; }
                    }
                    // Tentativa adicional: procurar por texto/valor 'Visualizar'
                    var inputs = document.getElementsByTagName('input');
                    for (var i=0;i<inputs.length;i++){
                        var v=_trimIE(inputs[i].value||'').toLowerCase();
                        if (v.indexOf('visualizar')>=0){ if(typeof inputs[i].click==='function'){ inputs[i].click(); return true; } }
                    }
                    var buttons = document.getElementsByTagName('button');
                    for (var j=0;j<buttons.length;j++){
                        var t=_trimIE(buttons[j].innerText||'').toLowerCase();
                        if (t.indexOf('visualizar')>=0){ if(typeof buttons[j].click==='function'){ buttons[j].click(); return true; } }
                    }
                    return false;
                })();
            """)
            clicou = True
        except Exception:
            clicou = False

        # Se não deu certo via JS direto, usa seletores tolerantes como fallback
        if not clicou:
            candidatos_xpath = [
                "//*[@name='BotVisualizar' or @id='BotVisualizar']",
                "//*[@id='visualizar' or @name='visualizar']",
                "//*[@id='cmdVisualizar' or @name='cmdVisualizar']",
                "//input[translate(@value,'VISUALIZAR','visualizar')='visualizar']",
                "//button[normalize-space(translate(text(),'VISUALIZAR','visualizar'))='visualizar']",
                "//input[contains(translate(@value,'VISUALIZAR','visualizar'),'visualizar')]",
                "//button[contains(translate(text(),'VISUALIZAR','visualizar'),'visualizar')]",
            ]

            botao = None
            for xp in candidatos_xpath:
                try:
                    botao = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                    if botao:
                        break
                except Exception:
                    botao = None

            if botao:
                try:
                    botao.click()
                    clicou = True
                except Exception:
                    try:
                        driver.execute_script("arguments[0].click && arguments[0].click();", botao)
                        clicou = True
                    except Exception:
                        try:
                            botao.send_keys(Keys.ENTER)
                            clicou = True
                        except Exception:
                            pass

        # Fallback final: submit do formulário do select, caso o botão não funcione
        if not clicou:
            try:
                driver.execute_script("""
                    (function(){
                        var sel = document.getElementsByName('opcaoRel')[0];
                        if (sel && sel.form && typeof sel.form.submit === 'function'){
                            sel.form.submit();
                            return true;
                        }
                        var f = document.forms && document.forms[0];
                        if (f && typeof f.submit === 'function'){ f.submit(); return true; }
                        return false;
                    })();
                """)
            except Exception:
                pass

        # Se ainda assim não houve navegação, tenta submeter o formulário do select como fallback
        try:
            driver.execute_script("""
                (function(){
                    var sel = document.getElementsByName('opcaoRel')[0];
                    if (sel && sel.form && typeof sel.form.submit === 'function'){
                        sel.form.submit();
                    }
                })();
            """)
        except Exception:
            pass

        # Após clicar, pode abrir nova janela OU recarregar a atual.
        # 1) Tenta nova janela
        if wait_and_switch_to_new_window(driver, timeout=wait_timeout):
            try:
                WebDriverWait(driver, wait_timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
            except Exception:
                pass
            
            return

        # 2) Se não abriu nova janela, aguarda carregamento e salva
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        try:
            WebDriverWait(driver, wait_timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        except Exception:
            pass
        
    except Exception as e:
        print(f"[ERRO] Ao selecionar 'numerica' e visualizar: {e}")


def click_gerexcel(driver, wait_timeout: int = 20) -> bool:
    """
    Clica no botão GerExecl na página atual (geralmente dentro do frame 'rotina').
    Retorna True se conseguiu acionar o clique.
    """
    try:
        print("[GEREXCEL] Iniciando tentativa de clique no GerExecl")
        driver.switch_to.default_content()
        driver.switch_to.frame("rotina")
        print("[GEREXCEL] Entrou no frame 'rotina'")

        try:
            el = driver.find_element(By.NAME, "GerExecl")
        except Exception:
            el = driver.find_element(By.ID, "GerExecl")

        print("[GEREXCEL] Encontrou elemento; clicando via Selenium .click()")
        el.click()
        driver.execute_script(
            "document.getElementById('GerExecl').click();"
        )
        print("[GEREXCEL] Sucesso: Selenium .click()")
        return True
    except Exception as e:
        print(f"[GEREXCEL] Falha no clique: {e}")
        return False

def realizar_automacao():

    try:
        print("🚀 Iniciando Internet Explorer...")

        service, options = obter_config_ie()

        driver = webdriver.Ie(service=service, options=options)

        driver.maximize_window()

        wait = WebDriverWait(driver, 10)
        # registra handle principal
        try:
            global MAIN_WINDOW_HANDLE
            MAIN_WINDOW_HANDLE = driver.current_window_handle
        except Exception:
            pass

        print("🌐 Acessando Revalle/Promax...")
        driver.get("https://revalle.promaxcloud.com.br/pw/")

        # LÓGICA DE LOGIN
        
        print("📥 Entrando no frame de login...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "frame")))

        print("🔑 Preenchendo login com JS...")

        # espera o campo existir
        wait.until(EC.presence_of_element_located((By.NAME, "Usuario")))

        # preencher usuário
        driver.execute_script(
            "document.getElementsByName('Usuario')[0].value = arguments[0];",
            login
        )

        # preencher senha
        driver.execute_script(
            "document.getElementsByName('Senha')[0].value = arguments[0];",
            senha
        )

        # clicar no botão
        driver.execute_script(
            "document.getElementById('BtnConfirm').click();"
        )

        print("✅ Login enviado!")
        driver.switch_to.default_content()

        # selecionar revenda
        print("Mudando para o frame top...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))

        botao_confirma = wait.until(
            EC.element_to_be_clickable((By.NAME, "cmdConfirma"))
        )
        botao_confirma.click()

        # fechar popups
        fechar_popups(driver, max_popups_to_check=4)

        driver.switch_to.default_content()

       # inserir rotina
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "top")))

        print("📂 Entrando no IframeMenu...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameMenu")))

        print(f"⌨️ Inserindo rotina: {rotina}")

        wait.until(EC.presence_of_element_located((By.ID, "atalho")))

        driver.execute_script("""
        var campo = document.getElementById('atalho');
        campo.value = arguments[0];
        """, rotina)

        driver.execute_script("""
        var container = document.getElementById('atal');
        var inputs = container.getElementsByTagName('input');
        inputs[1].click();
        """)

        # Após o clique, uma nova janela é aberta: aguarda e troca o foco para ela
        trocou = wait_and_switch_to_new_window(driver, timeout=25)
        if trocou:
            # Por segurança, aguarda o carregamento inicial de DOM na nova janela
            try:
                WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
            except Exception:
                pass
            
        

        # Na janela/dados abertos, selecionar 'numerica' e clicar em visualizar, depois salvar HTML
        selecionar_numerica_e_visualizar(driver, wait_timeout=8)

        # pequena espera para estabilizar a tela antes de exportar
        time.sleep(2)
        # Mantém foco na janela atual (onde o relatório está) para clicar em GerExecl.
        # Em seguida, se necessário, o click_gerexcel varre frames para encontrar o botão.

        # Agora estamos na página certa; clicar no botão GerExecl
        ok = click_gerexcel(driver, wait_timeout=8)
        if not ok:
            print("[WARN] Não consegui acionar o botão GerExecl.")

        time.sleep(5)
        driver.execute_script(
            "document.getElementById('GerExecl').focus();"
        )
        autoit.send("{F6}{TAB 2}{ENTER}")
        time.sleep(2)

        # Garante que a pasta de destino exista (se não existir, o Python cria)
        os.makedirs(DOWNLOAD_TARGET_DIR, exist_ok=True)

        # 2. Busca todos os arquivos que batem com o padrão do download
        padrao_busca = os.path.join(dir_downloads, "01.20.01.47_PW01076R_pizolitto_*.csv.inf")
        arquivos_encontrados = glob.glob(padrao_busca)

        # 3. Verifica se encontrou algum arquivo
        if arquivos_encontrados:
            
            # Pega o arquivo mais recente da lista
            arquivo_original = max(arquivos_encontrados, key=os.path.getctime)
            nome_antigo = os.path.basename(arquivo_original)
            
            # 4. Remove o ".inf" do final do nome (substitui por nada)
            novo_nome = nome_antigo.replace(".inf", "")
            
            # Monta o caminho final completo
            caminho_final = os.path.join(DOWNLOAD_TARGET_DIR, novo_nome)
            
            # Prevenção de erro: Se já existir um arquivo com esse nome exato no destino, ele apaga o antigo
            if os.path.exists(caminho_final):
                os.remove(caminho_final)
                
            # 5. Move e renomeia o arquivo simultaneamente
            shutil.move(arquivo_original, caminho_final)
            
            print(f"Sucesso! Arquivo processado:")
            print(f"Salvo em: {caminho_final}")

        print(f"✅ Rotina {rotina} finalizada!")
        driver.close() # Fecha a janela atual (o relatório)
        driver.switch_to.window(MAIN_WINDOW_HANDLE) # Volta para a janela do menu

    except Exception as e:
        print(f"❌ Erro: {e}")

    


if __name__ == "__main__":\
    realizar_automacao()
