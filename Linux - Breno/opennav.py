import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# --- 1. AJUSTE DE IMPORTAÇÃO ---
# Agora importamos a função correta do seu configlinux.py
from configlinux import obter_config_ie
from fecharPopups import fechar_popups

login = "pizolitto"
senha = "Nerd12lol"
rotina = "01.20.01.47"

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
        botao_ok = driver.find_element(By.XPATH, '//*[@id="atal"]/div[1]/table/