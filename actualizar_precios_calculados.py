import pandas as pd
import requests

# Configuración de Shopify
API_TOKEN = "REDACTED"  # Admin API Access Token
SHOP_NAME = "28b3fe-e1.myshopify.com"  # Subdominio correcto de tu tienda
API_VERSION = "2025-01"  # Versión de la API

# Tasa fija de conversión USD a COP
USD_TO_COP_RATE = 4000  # Cambia esta tasa según el tipo de cambio actual

# Función para calcular el precio ajustado
def calcular_precio(base_price_usd, tax_rate=0.10, shipping_cost=100000, profit_margin=0.35):
    """
    Calcula el precio final ajustado en COP.
    """
    base_price_cop = base_price_usd * USD_TO_COP_RATE  # Convertir de USD a COP
    price_with_taxes = base_price_cop * (1 + tax_rate)  # Agregar impuestos
    final_price = price_with_taxes + shipping_cost  # Agregar costo de envío
    return round(final_price * (1 + profit_margin), 2)  # Aplicar ganancia

# Función para actualizar precios en Shopify
def actualizar_precios(csv_file):
    # Leer el archivo CSV con los Handles y precios en USD
    data = pd.read_csv(csv_file)

    # Validar que el archivo tenga las columnas necesarias
    if not {'Handle', 'Price USD'}.issubset(data.columns):
        print("El archivo CSV debe contener las columnas 'Handle' y 'Price USD'.")
        return

    # Iterar sobre cada producto
    for index, row in data.iterrows():
        handle = row['Handle']
        base_price_usd = row['Price USD']

        # Validar que el precio base sea numérico
        try:
            base_price_usd = float(base_price_usd)
        except ValueError:
            print(f"Precio inválido para el Handle {handle}.")
            continue

        # Calcular el precio ajustado
        adjusted_price = calcular_precio(base_price_usd)

        # Buscar y actualizar el producto en Shopify
        url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/products.json?handle={handle}"
        headers = {"X-Shopify-Access-Token": API_TOKEN}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            products = response.json().get("products", [])
            if products:
                product = products[0]
                product_id = product["id"]
                variant_id = product["variants"][0]["id"]

                # Actualizar el precio del producto
                update_url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/variants/{variant_id}.json"
                update_data = {"variant": {"id": variant_id, "price": adjusted_price}}
                update_response = requests.put(update_url, headers=headers, json=update_data)

                if update_response.status_code == 200:
                    print(f"Precio del producto '{handle}' actualizado a {adjusted_price} COP.")
                else:
                    print(f"No se pudo actualizar el precio del producto '{handle}'.")
                    print("Detalles:", update_response.text)
            else:
                print(f"Producto con Handle '{handle}' no encontrado en Shopify.")
        else:
            print(f"Error al buscar el producto '{handle}': {response.status_code}")
            print("Detalles:", response.text)

# Ejecutar la función principal
if __name__ == "__main__":
    csv_file = "products_to_update.csv"  # Archivo con Handles y precios en USD
    actualizar_precios(csv_file)
