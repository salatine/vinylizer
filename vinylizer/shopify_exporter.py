from typing import List
from vinylizer.Product import Product
import csv
import io
from slugify import slugify
from uuid import uuid4

VINYL_TAG_RELATIONS = {
    'all': 'LPs',
    'novo': 'LPs - Novos / Lacrados',
    'nacional': 'LPs - Nacional',
    'internacional': 'LPs - Internacional',
    'compactos': 'LPs - Compactos',
    'compactos-nacional': 'LPs - Compactos Nacional',
    'compactos-internacional': 'LPs - Compactos Internacional',
    'mpb': 'LPs - MPB',
    'dance': 'LPs - Dance Music',
    'electronic': 'LPs - Dance Music',
    'soul': 'LPs - Soul / Funk / Black',
    'funk': 'LPs - Soul / Funk / Black',
    'black': 'LPs - Soul / Funk / Black',
    'blues': 'LPs - Blues & Jazz',
    'jazz': 'LPs - Blues & Jazz',
    'trilhas': 'LPs - Trilhas Sonoras',
    'trilhas-nacional': 'LPs - Trilhas Sonoras Nacional',
    'trilhas-internacional': 'LPs - Trilhas Sonoras Internacional',
    'rock-nacional': 'LPs - Rock/POP Nacional',
    'pop-nacional': 'LPs - Rock/POP Nacional',
    'rock-internacional': 'LPs - Rock/POP Internacional',
    'pop-internacional': 'LPs - Rock/POP Internacional',
    'samba': 'LPs - Samba & Pagode',
    'pagode': 'LPs - Samba & Pagode',
    'sertanejo': 'LPs - Sertanejo',
    'classica': 'LPs - Clássicas e Orquestras',
    'orquestra': 'LPs - Clássicas e Orquestras',
    'latin': 'LPs - Latinas e Europeias',
    'outros': 'LPs - Outros',
    'outros-nacional': 'LPs - Outros Nacional',
    'outros-internacional': 'LPs - Outros Internacional',
}

TAG_RELATIONS = {
    'Lp Vinil': VINYL_TAG_RELATIONS,
    'Compacto Vinil': VINYL_TAG_RELATIONS,
    'CD': {
        'all': 'CDs',
        'mpb': 'CDs - MPB',
        'blues': 'CDs - Blues & Jazz',
        'jazz': 'CDs - Blues & Jazz',
        'dance': 'CDs - Dance Music',
        'trilhas': 'CDs - Trilhas Sonoras',
        'rock-nacional': 'CDs - Rock/POP Nacional',
        'pop-nacional': 'CDs - Rock/POP Nacional',
        'rock-internacional': 'CDs - Rock/POP Internacional',
        'pop-internacional': 'CDs - Rock/POP Internacional',
        'samba': 'CDs - Samba & Pagode',
        'pagode': 'CDs - Samba & Pagode',
        'sertanejo': 'CDs - Sertanejo',
        'forró': 'CDs - Forró',
        'outros': 'CDs - Outros',
    },

    'DVD': {
        'all': 'DVDs - Música',
        'rock-nacional': 'DVDs Música - Rock/POP Nacional',
        'pop-nacional': 'DVDs Música - Rock/POP Nacional',
        'rock-internacional': 'DVDs Música - Rock/POP Internacional',
        'pop-internacional': 'DVDs Música - Rock/POP Internacional',
        'mpb': 'DVDs Música - MPB',
        'samba': 'DVDs Música - Samba & Pagode',
        'pagode': 'DVDs Música - Samba & Pagode',
        'sertanejo': 'DVDs Música - Sertanejo',
        'ópera': 'DVDs Música - Ópera',
        'forró': 'DVDs Música - Forró & Música Nordestina',
        'outros': 'DVDs Música - Outros',
    },

    'Fita K7 Cassete': {
        'all': 'K7',
    },

    'LD LaserDisc': {
        'all': 'Outros',
        'nacional': 'Outros - LD LaserDisc',
        'internacional': 'Outros - LD LaserDisc',
    },
}

PRODUCT_CATEGORY_RELATIONS = {
    'Lp Vinil': 'Mídia > Gravações de músicas > Discos e LPs',
    'Compacto Vinil': 'Mídia > Gravações de músicas > Vinil',
    'CD': 'Mídia > Gravações de músicas > CDs de música',
    'DVD': 'Mídia > Vídeos > DVDs',
    'Fita K7 Cassete': 'Mídia > Gravações de músicas > Fitas cassete de música',
    'LD LaserDisc': 'Mídia > Gravações de músicas > Discos e LPs',
}

PRODUCT_GRAMS_RELATIONS = {
    'Lp Vinil': '100000.0',
    'LD LaserDisc': '100000.0',
    'Compacto Vinil': '10000.0',
    'Fita K7 Cassete': '1000.0',
    'CD': '100.0',
    'DVD': '100.0',
}

COLUMNS = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category', 'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Included / Brazil', 'Price / Brazil', 'Compare At Price / Brazil', 'Included / International', 'Price / International', 'Compare At Price / International', 'Status']

def export_to_shopify_spreadsheet(output_path: str, products: List[Product]) -> None:
    with io.open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator='\r', quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for i, product in enumerate(products):
            handle = get_product_handle(product)

            # Temos que escrever várias linhas na planilha para descrever o produto, pois o Shopify só permite
            # uma imagem do produto por linha.
            # Para contornar isso, preenchemos a primeira linha com todas as informações do produto e a URL
            # da primeira imagem; e geramos linhas adicionais contendo apenas o `handle` (um identificador do produto)
            # e a URL das imagens que restaram.
            first_row = {
                'Handle': handle,
                'Title': product.title,
                'Body (HTML)': product.description,
                'Product Category': PRODUCT_CATEGORY_RELATIONS[product.format],
                'Vendor': 'Searom Discos',
                'Tags': ', '.join(get_product_tags(product)),
                'Published': 'true',
                'Variant Grams': PRODUCT_GRAMS_RELATIONS[product.format],
                'Variant Inventory Tracker': 'shopify',
                'Variant Inventory Qty': str(product.stock),
                'Variant Inventory Policy': 'deny',
                'Variant Fulfillment Service': 'manual',
                'Variant Price': product.price,
                'Variant Requires Shipping': 'true',
                'Variant Taxable': 'false',
                'Image Src': product.picture_urls[0],
                'Image Position': 1,
                'Status': 'active',
            }

            additional_rows = [
                { 'Handle': handle, 'Image Src': photo_url, 'Image Position': index + 1 }
                for index, photo_url in enumerate(product.picture_urls[1:], start=1)
            ]
            rows = [first_row] + additional_rows

            writer.writerows(rows)

def get_product_handle(product: Product) -> str:
    # generate random uuid for handle, avoiding possible shopify conflicts
    uuid = str(uuid4())
    return slugify(product.title + f' {uuid}')

def get_product_tags(product: Product) -> List[str]:
    nationality = 'nacional' if product.is_national else 'internacional'
    genres = [genre.lower() for genre in product.genres]

    tags = []
    tags.append(TAG_RELATIONS[product.format]['all'])
    if nationality in TAG_RELATIONS[product.format].keys():
        tags.append(TAG_RELATIONS[product.format][nationality])

    if product.format == 'Lp Vinil' and product.is_new == True:
        tags.append(TAG_RELATIONS[product.format]['novo'])

    for genre in genres:
        genre_nationality = f'{genre}-{nationality}'
        if genre in TAG_RELATIONS[product.format].keys():
            tags.append(TAG_RELATIONS[product.format][genre])

        if genre_nationality in TAG_RELATIONS[product.format].keys():
            tags.append(TAG_RELATIONS[product.format][genre_nationality])

    return tags
