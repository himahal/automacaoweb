from selenium import webdriver
from configs import obter_config_ie

service, options = obter_config_ie()

print("🌐 Abrindo navegador Internet Explorer...")
driver = webdriver.Ie(service=service, options=options)
driver.maximize_window()

print("📥 Acessando a URL do sistema...")
driver.get("https://app.powerbi.com/groups/me/apps/a44ca4f3-ad02-4e6d-b2f9-523d74c0a272/reports/67b52c11-a1cb-433f-adee-e18e506d552a/ReportSection?ctid=cef04b19-7776-4a94-b89b-375c77a8f936&experience=power-bi")
