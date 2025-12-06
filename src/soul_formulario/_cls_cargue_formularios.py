"""
Created By Emerson Aguilar Cruz
"""
import os
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from web_scraping._cls_webscraping import WebScraping_Chrome
import json

class FormulariosSoul():

    def __init__(self, usuario=None, contrasena=None, archivo_excel=None):

        self.current_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(self.current_folder)

        self.project_root = os.path.dirname(self.current_folder)
        print(self.project_root)

        self.path_home = str(Path.home())
        self.driver_path = os.path.join(
            self.path_home,
            'Documents',
            'chromedriver.exe'
        )
        
        # Crear carpeta para perfil de Chrome persistente
        self.chrome_profile_path = os.path.join(self.project_root, 'data', 'chrome_profile_soul')
        os.makedirs(self.chrome_profile_path, exist_ok=True)

        self.config_json_path = os.path.join(self.project_root, 'config', 'config_formulario_soul.json')
        with open(self.config_json_path, 'r', encoding='utf-8') as f:
            self.config_soul = json.load(f)

        self.campanas_disponibles = [key for key in self.config_soul.keys()]
        print("Campañas Disponibles:")

        for i, campana in enumerate(self.campanas_disponibles, start=1):
            print(f"{i}. {campana}")

        while True:
            try:
                seleccion = int(input("Ingrese el numero de la campaña que desea ejecutar: "))
                if 1 <= seleccion <= len(self.campanas_disponibles):
                    self.campana_seleccionada = self.campanas_disponibles[seleccion - 1]
                    break
                else: 
                    print("Numero no valido, intente nuevamente")
            except ValueError:
                print("Entrada no valida. Ingrese un numero")

        self.campana_config = self.config_soul[self.campana_seleccionada]
        
        self.url = 'https://www.mysoul.software/login'
        
        self.usuario = usuario
        self.contrasena = contrasena
        
        self.crm = self.campana_config['crm']
        self.nombre_formulario = self.campana_config['nombre_formulario']
        
        self.ruta_formulario = os.path.join(self.project_root, 'data', 'upload_soul', self.campana_seleccionada)
        os.makedirs(self.ruta_formulario, exist_ok=True)

        for archivo in os.listdir(self.ruta_formulario):
            if archivo.lower().endswith(('.xlsx', '.xls')):
                self.archivo_excel = os.path.join(self.ruta_formulario, archivo )
                break

        else: 
            self.archivo_excel = None

    def buscar_formulario(self):

        try:
            # Usar EXACTAMENTE la misma configuración que el setup
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            
            options = webdriver.ChromeOptions()
            options.add_argument(f"--user-data-dir={self.chrome_profile_path}")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-blink-features=AutomationControlled")
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0
            }
            options.add_experimental_option("prefs", prefs)
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            service = Service(executable_path=self.driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            driver.maximize_window()
            
            driver.get(self.url)
            time.sleep(3)
            
            WebScraping_Chrome.WebScraping_WaitCSS(driver, 150, 'input[formcontrolname="user"]')
            WebScraping_Chrome.WebScraping_SendKeysCSS(driver, 'input[formcontrolname="user"]', self.usuario) 

            WebScraping_Chrome.WebScraping_WaitCSS(driver, 150, 'input[formcontrolname="password"]')
            WebScraping_Chrome.WebScraping_SendKeysCSS(driver, 'input[formcontrolname="password"]', self.contrasena) 
            time.sleep(1)

            WebScraping_Chrome.WebScraping_WaitCSS(driver, 150, 'button[type="submit"][color="primary"]')
            WebScraping_Chrome.WebScraping_ClickCSS(driver, 'button[type="submit"][color="primary"]')

            WebScraping_Chrome.WebScraping_WaitTextCSS(driver, 150, 'a.mat-list-item.mat-menu-trigger', 'Menú')
            WebScraping_Chrome.WebScraping_ClickByTextCSS(driver, 'a.mat-list-item.mat-menu-trigger', 'Menú')
            time.sleep(1)

            WebScraping_Chrome.WebScraping_WaitTextCSS(driver, 150, 'button.mat-focus-indicator[mat-menu-item]', 'Aplicaciones')
            WebScraping_Chrome.WebScraping_ClickByTextCSS(driver, 'button.mat-focus-indicator[mat-menu-item]', 'Aplicaciones')
            time.sleep(1)

            WebScraping_Chrome.WebScraping_WaitTextCSS(driver, 150, 'button.mat-focus-indicator[mat-menu-item]', self.crm)
            WebScraping_Chrome.WebScraping_ClickByTextCSS(driver, 'button.mat-focus-indicator[mat-menu-item]', self.crm)
            time.sleep(2)
            
            # Cerrar el popup de notificaciones si aparece
            try:
                # Buscar el botón OK del popup de notificaciones
                ok_button = driver.find_element(By.XPATH, "//button[contains(text(), 'OK')]")
                ok_button.click()
                print("✅ Popup de notificaciones cerrado")
                time.sleep(2)
            except:
                print("ℹ️ No apareció popup de notificaciones")
                time.sleep(1)

            # Esperar a que desaparezca el overlay si existe
            try:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.overlay'))
                )
                print("✅ Overlay desaparecido")
                time.sleep(2)
            except:
                time.sleep(2)  # Si no hay overlay, solo esperar
            
            # Ahora sí hacer click en Formularios
            WebScraping_Chrome.WebScraping_WaitClickableCSS(driver, 150, 'a.mat-list-item.mat-focus-indicator')
            WebScraping_Chrome.WebScraping_ClickByTextCSS(driver, 'a.mat-list-item.mat-focus-indicator', 'Formularios')
            print("✅ Click en Formularios")
            time.sleep(5)  # Esperar más tiempo a que cargue la página
            
            # Esperar a que la página de formularios cargue completamente
            try:
                WebScraping_Chrome.WebScraping_WaitCSS(driver, 30, 'mat-select')
                print("✅ Página de formularios cargada")
            except Exception as e:
                print(f"❌ No se encontró mat-select: {e}")
                print(f"📍 URL actual: {driver.current_url}")
                # Tomar screenshot para debug
                driver.save_screenshot(os.path.join(self.project_root, 'data', 'debug_formularios.png'))
                raise

            WebScraping_Chrome.WebScraping_ScrollIntoViewCSS(driver, 'mat-select')
            WebScraping_Chrome.WebScraping_WaitClickableCSS(driver, 10, 'mat-select')
            WebScraping_Chrome.WebScraping_ClickCSS(driver, 'mat-select')
            time.sleep(1)

            WebScraping_Chrome.WebScraping_WaitClickableCSS(driver, 10, 'mat-option .mat-option-text')
            WebScraping_Chrome.WebScraping_ClickByTextCSS(driver, 'mat-option .mat-option-text', '100')
            time.sleep(1)

            WebScraping_Chrome.WebScraping_WaitCSS(driver, 150, 'input[formcontrolname="search"]')
            WebScraping_Chrome.WebScraping_SendKeysCSS(driver, 'input[formcontrolname="search"]', self.nombre_formulario)
            time.sleep(1)

        except Exception as e:
             print(f"Error: Error al buscar el formulario debido a {e}")
        
        self.driver = driver
        return self.driver
    
    def cargar_formulario(self):

        try:
            WebScraping_Chrome.WebScraping_WaitClickableCSS(self.driver, 150, 'button[aria-label="Toggle menu"]')
            WebScraping_Chrome.WebScraping_ClickCSS(self.driver, 'button[aria-label="Toggle menu"]')
            print("✅ Click en Toggle menu")
            time.sleep(1)
        
            WebScraping_Chrome.WebScraping_WaitClickableCSS(self.driver, 150, 'button.mat-menu-item')
            WebScraping_Chrome.WebScraping_ClickByTextCSS(self.driver, 'button.mat-menu-item', 'Crear base de datos')
            print("✅ Click en Crear base de datos")
            time.sleep(3)
            
            # Buscar el input de archivo por ID (está oculto, por eso no lo encuentra el wait)
            try:
                file_input = self.driver.find_element(By.ID, 'file')
                print("✅ Input de archivo encontrado por ID")
            except:
                # Si no existe por ID, buscar por type
                file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                print("✅ Input de archivo encontrado por type")
            
            # Hacer visible el input y cargar archivo
            self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
            self.driver.execute_script("arguments[0].style.visibility = 'visible';", file_input)
            self.driver.execute_script("arguments[0].style.opacity = '1';", file_input)
            file_input.send_keys(self.archivo_excel)
            print(f"✅ Archivo cargado: {os.path.basename(self.archivo_excel)}")
            time.sleep(2)
        
        except Exception as e:
            print(f"Error: Error al cargar el formulario debido a {e}")
        
        WebScraping_Chrome.WebScraping_WaitClickableCSS(self.driver, 150, 'div.row.col-8')
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'div.row.col-8')

        for row in rows:
            label_text = None
            try:
                label_elem = row.find_element(By.CSS_SELECTOR, '.col-4 .box__white')
                label_text = label_elem.text.strip()

                if label_text in self.campana_config['mapping']:
                    try:
                        select_elem = row.find_element(By.CSS_SELECTOR, 'mat-select')
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", select_elem)
                        select_elem.click()
                        time.sleep(0.1)

                        option_text = self.campana_config['mapping'][label_text]
                        option_elem = self.driver.find_element(
                            By.XPATH,
                            f"//mat-option//span[normalize-space(text())='{option_text}']"
                        )
                        option_elem.click()
                        time.sleep(1)

                    except Exception as e:
                        print(f"Error: No se pudo seleccionar opción para '{label_text}': {e}")

                else:
                    print(f"Etiqueta '{label_text}' no está en el mapping, se omite.")

            except Exception as e:
                print(f"Error: Error procesando fila (etiqueta: {label_text}): {e}")
  
        
        WebScraping_Chrome.WebScraping_WaitCSS(self.driver, 150, 'button[type="submit"][color="primary"]')
        WebScraping_Chrome.WebScraping_ClickCSS(self.driver, 'button[type="submit"][color="primary"]')
        time.sleep(1)

        WebScraping_Chrome.WebScraping_WaitCSS(self.driver, 150, 'mat-radio-button[value="0"]')
        WebScraping_Chrome.WebScraping_ClickCSS(self.driver, 'mat-radio-button[value="0"]')

        time.sleep(1)

        WebScraping_Chrome.WebScraping_WaitCSS(self.driver, 10, 'button[type="submit"][color="primary"].continue-button')
        WebScraping_Chrome.WebScraping_ClickCSS(self.driver, 'button[type="submit"][color="primary"].continue-button')
        time.sleep(1)

        WebScraping_Chrome.WebScraping_WaitTextCSS(self.driver, 150, 'mat-radio-button .mat-radio-label-content', 'Reemplazar y actualizar')
        WebScraping_Chrome.WebScraping_ClickByTextCSS(self.driver, 'mat-radio-button .mat-radio-label-content', 'Reemplazar y actualizar')
        time.sleep(1)

        WebScraping_Chrome.WebScraping_WaitCSS(self.driver, 150, 'button[type="button"][color="primary"].continue-button')
        WebScraping_Chrome.WebScraping_ClickCSS(self.driver, 'button[type="button"][color="primary"].continue-button')
        time.sleep(1)

        WebScraping_Chrome.WebScraping_WaitTextCSS(self.driver, 150, 'button.swal2-confirm.swal2-styled', 'Aceptar')
        WebScraping_Chrome.WebScraping_ClickByTextCSS(self.driver, 'button.swal2-confirm.swal2-styled', 'Aceptar')
        time.sleep(1)

        WebScraping_Chrome.WebScraping_WaitTextCSS(self.driver, 1000, 'button.swal2-confirm.swal2-styled', 'Aceptar')
        time.sleep(10)
        WebScraping_Chrome.WebScraping_ClickByTextCSS(self.driver, 'button.swal2-confirm.swal2-styled', 'Aceptar')
        
        print("Proceso SOUL Terminado")