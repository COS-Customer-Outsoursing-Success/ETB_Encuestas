"""
Script de configuración inicial para Soul
Ejecuta esto UNA VEZ para configurar el perfil de Chrome y bloquear notificaciones
"""
import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

print("="*45)
print("CONFIGURACIÓN INICIAL DE SOUL")
print("="*45)
print("\n📌 INSTRUCCIONES:")
print("1. Se abrirá Chrome con Soul")
print("2. Cuando aparezca el popup de notificaciones, presiona 'OK'")
print("3. Luego cierra el navegador manualmente")
print("4. La próxima vez NO aparecerá el popup")
print("\n" + "="*45)
input("\nPresiona ENTER para continuar...")

# Obtener rutas
path_home = str(Path.home())
driver_path = os.path.join(path_home, 'Documents', 'chromedriver.exe')

# Detectar ruta del proyecto
current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)

# Crear perfil persistente
chrome_profile_path = os.path.join(project_root, 'data', 'chrome_profile_soul')
os.makedirs(chrome_profile_path, exist_ok=True)

print(f"\n✅ Perfil de Chrome creado en: {chrome_profile_path}")

# Configurar Chrome
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={chrome_profile_path}")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-blink-features=AutomationControlled")

prefs = {
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_settings.popups": 0
}
options.add_experimental_option("prefs", prefs)
options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()

# Abrir Soul
url = 'https://www.mysoul.software/login'
driver.get(url)

print("\n✅ Chrome abierto con Soul")
print("📌 Si aparece el popup, presiona 'OK'")
print("📌 Luego CIERRA el navegador manualmente (no lo hagas desde aquí)")
print("\nEsperando 45 segundos...")

time.sleep(45)

print("\n✅ Configuración completada!")
print("🚀 Ahora ejecuta tu script normal y NO aparecerá el popup")
