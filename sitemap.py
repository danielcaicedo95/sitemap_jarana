import requests
import xml.etree.ElementTree as ET
import csv

# URL del sitemap original
sitemap_url = "https://jarana-b2c.myshopify.com/sitemap.xml"

def fetch_sitemap(url):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return ET.fromstring(response.content)
        except ET.ParseError as e:
            print(f"Error al analizar el XML: {e} - Contenido recibido: {response.content.decode('utf-8')}")
            return None
    else:
        print(f"Error al obtener el sitemap: {response.status_code} - Contenido recibido: {response.text}")
        return None

def extract_links(sitemap):
    collections = []
    pages = []
    products = []

    # Extraer URLs de los sitemaps principales
    for url in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        if "/collections/" in loc:
            collections.append(loc)
        elif "/pages/" in loc:
            pages.append(loc)
        elif "/products/" in loc:
            products.append(loc)

    # Extraer URLs de los sitemaps secundarios
    for sitemap in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
        loc = sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        if loc:
            nested_sitemap = fetch_sitemap(loc)
            if nested_sitemap is not None:
                nested_links = extract_links(nested_sitemap)
                collections.extend(nested_links[0])
                pages.extend(nested_links[1])
                products.extend(nested_links[2])

    return collections, pages, products

def get_all_urls(sitemap_url):
    all_collections = []
    all_pages = []
    all_products = []
    to_visit = [sitemap_url]

    while to_visit:
        current_url = to_visit.pop()
        sitemap = fetch_sitemap(current_url)
        if sitemap is not None:
            collections, pages, products = extract_links(sitemap)
            all_collections.extend(collections)
            all_pages.extend(pages)
            all_products.extend(products)
            # Agregar los sitemaps secundarios a la lista para visitar
            to_visit.extend([link for link in collections + pages + products if 'sitemap' in link])

    return all_collections, all_pages, all_products

# Obtener todas las URLs
collections, pages, products = get_all_urls(sitemap_url)

# Guardar en un archivo CSV
with open('sitemap_urls.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Escribir encabezados
    writer.writerow(["Colecciones", "Páginas", "Productos"])

    # Encontrar el número máximo de filas
    max_rows = max(len(collections), len(pages), len(products))

    # Agregar URLs al CSV
    for i in range(max_rows):
        writer.writerow([
            collections[i] if i < len(collections) else "",
            pages[i] if i < len(pages) else "",
            products[i] if i < len(products) else ""
        ])

print("Archivo CSV generado con éxito: sitemap_urls.csv")
