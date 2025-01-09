import pandas as pd

def preparar_archivo_actualizacion(amazon_csv, shopify_csv, mapeo_csv, output_csv):
    # Leer los datos de Amazon, Shopify y el mapeo
    amazon_data = pd.read_csv(amazon_csv)
    shopify_data = pd.read_csv(shopify_csv)
    mapeo = pd.read_csv(mapeo_csv)

    # Unir el mapeo con los datos de Amazon
    amazon_data = amazon_data.merge(mapeo, left_on="Product Name", right_on="Amazon Product Name", how="inner")

    # Unir los datos de Shopify usando el Handle del mapeo
    products_to_update = amazon_data.merge(shopify_data, left_on="Shopify Handle", right_on="Handle", how="inner")

    # Seleccionar solo las columnas necesarias
    products_to_update = products_to_update[["Handle", "Price"]]
    products_to_update.rename(columns={"Price": "Price USD"}, inplace=True)

    # Eliminar duplicados basados en el Handle
    products_to_update = products_to_update.drop_duplicates(subset=["Handle"])

    # Guardar el archivo final
    products_to_update.to_csv(output_csv, index=False)
    print(f"Archivo generado: {output_csv}")

# Ejecución del script
if __name__ == "__main__":
    preparar_archivo_actualizacion(
        amazon_csv="product_data.csv",
        shopify_csv="products_export_1.csv",
        mapeo_csv="mapeo_amazon_shopify.csv",
        output_csv="products_to_update.csv"
    )
