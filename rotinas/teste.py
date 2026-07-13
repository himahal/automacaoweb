from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

opcoes = Options()

opcoes.add_argument(
    r"--user-data-dir=C:\Users\usuario\AppData\Local\Google\Chrome\User Data"
)

opcoes.add_argument(
    "--profile-directory=Profile 2"
)

opcoes.add_argument(
    "--remote-debugging-port=0"
)

opcoes.add_argument(
    "--disable-extensions"
)

opcoes.add_argument(
    "--no-first-run"
)

opcoes.add_argument(
    "--no-default-browser-check"
)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opcoes
)

print("SESSÃO CRIADA")

input("Pressione ENTER para fechar...")

driver.quit()
