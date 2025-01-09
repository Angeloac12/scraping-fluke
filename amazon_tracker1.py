from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import datetime

# Configuración de Selenium
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Quitar para ver el navegador en acción
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

# Establecer el código postal en Amazon
def set_postcode(driver, postcode="33101"):
    try:
        driver.get("https://www.amazon.com")
        wait = WebDriverWait(driver, 10)
        
        # Hacer clic en el botón de ubicación
        location_button = wait.until(EC.element_to_be_clickable((By.ID, "nav-global-location-popover-link")))
        location_button.click()

        # Ingresar el código postal
        postcode_input = wait.until(EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput")))
        postcode_input.clear()
        postcode_input.send_keys(postcode)

        # Confirmar el código postal
        apply_button = driver.find_element(By.ID, "GLUXZipUpdate")
        apply_button.click()

        # Cerrar el modal si aparece
        try:
            close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close']")))
            close_button.click()
        except:
            pass  # Si no aparece el modal, continuar

        print(f"Código postal establecido en: {postcode}")
    except Exception as e:
        print(f"Error al establecer el código postal: {e}")

# Extraer datos de cada producto
def fetch_product_data(url, driver):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Extraer datos del producto
        name = fetch_element_text(driver, wait, By.ID, "productTitle", "Producto no encontrado")
        price = fetch_element_text(driver, wait, By.CLASS_NAME, "a-price-whole", "Precio no disponible")
        availability = fetch_element_text(driver, wait, By.ID, "availability", "Disponibilidad no encontrada")

        return {
            'Product Name': name,
            'Price': price,
            'Availability': availability,
            'URL': url,
            'Timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Error al procesar {url}: {e}")
        return {
            'Product Name': "Error",
            'Price': "Error",
            'Availability': "Error",
            'URL': url,
            'Timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# Función auxiliar para obtener texto de un elemento
def fetch_element_text(driver, wait, by, value, default=""):
    try:
        element = wait.until(EC.presence_of_element_located((by, value)))
        return element.text.strip()
    except:
        return default

# Guardar datos en CSV
def save_to_csv(data, output_file='product_data.csv'):
    df = pd.DataFrame(data)
    df.to_csv(output_file, mode='a', header=not pd.io.common.file_exists(output_file), index=False)

# Leer URLs desde el archivo
def read_urls(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Archivo no encontrado: {file_path}")
        return []

# Función principal
def track_products():
    driver = init_driver()
    try:
        set_postcode(driver, postcode="33101")

        # Leer las URLs
        urls = read_urls('urls_utf8.txt')
        if not urls:
            print("No se encontraron URLs para procesar.")
            return

        data = []
        for url in urls:
            print(f"Procesando: {url}")
            product_data = fetch_product_data(url, driver)
            data.append(product_data)

        save_to_csv(data)
        print("Datos guardados exitosamente en 'product_data.csv'.")
    finally:
        driver.quit()

if __name__ == "__main__":
    track_products()
