from pathlib import Path
import discogs_client
import tomli
from typing import Callable, List, Optional, TypeVar
from PySide6 import QtWidgets
import platform
from vinylizer.Product import Product
from vinylizer.product_suggestion import ProductSuggestion, NULL_SUGGESTION
from vinylizer.shopify_exporter import export_to_shopify_spreadsheet
from vinylizer.ml_exporter import export_to_ml_spreadsheet
from datetime import timedelta, datetime
from vinylizer.emailer import send_email
import json
from vinylizer.resume_sheet import create_resume_sheet

with open('./config.toml', 'rb') as file:
    CONFIG = tomli.load(file)

def main():
    QtWidgets.QApplication([])
    client = get_client(get_token())
    
    json_products = get_json_products()

    products = get_products(client, json_products)
    export_to_ml_spreadsheet(get_ml_spreadsheet(), products) 
    export_to_shopify_spreadsheet(get_shopify_spreadsheet(), products)

    # backup não é mais necessário uma vez que é concluído o processo de exportação
    delete_json_products()

    create_resume_sheet(products, get_resume_sheet_path())

    data = datetime.now().strftime("%d/%m/%Y")
    if input(f"\ndeseja enviar um e-mail com a relação para {CONFIG['receivers']}? [S/n]: ").lower() != 'n':
        send_email(
            subject=f"Relação {data}",
            body=CONFIG['message'],
            sender=CONFIG['sender'],
            receivers=CONFIG['receivers'],
            app_password=CONFIG['app_password'],
            resume_attachment_path=get_resume_sheet_path(),
        )

        print('e-mail enviado com sucesso!')

def get_json_products() -> List[Product]:    
    json_products = []
    if Path('./products.json').exists() and input('foi detectado um backup dos produtos, deseja carregá-lo? [S/n]: ').lower() != 'n':
        json_products = load_json_products()
        print(f'{len(json_products)} produtos carregados do arquivo de backup')

    return json_products

def load_json_products() -> List[Product]:
    products = []
    with open('./products.json', 'r') as file:
        json_products = json.load(file)
        for json_product in json_products:
            product = Product(
                artist = json_product['artist'],
                album = json_product['album'],
                price = json_product['price'],
                gatefold_quantity = json_product['gatefold_quantity'],
                lps_quantity = json_product['lps_quantity'],
                genres = json_product['genres'],
                is_national = json_product['is_national'],
                is_repeated = json_product['is_repeated'],
                is_double_covered = json_product['is_double_covered'],
                pictures = json_product['pictures'],
                song_quantity = json_product['song_quantity'],
                album_duration = json_product['album_duration'],
                release_year = json_product['release_year'],
                label = json_product['label'],
                observation = json_product['observation'],
            )
            products.append(product)

    return products

def get_products(client: discogs_client.Client, json_products: List[Product]) -> List[Product]:
    products = json_products
    if len(products) > 1 and input('\ndeseja cadastrar mais produtos? [S/n]: ').lower() == 'n':
        return products

    while True:
        suggestion = get_product_suggestion_with_discogs(client)
        if suggestion == None:
            break
        if suggestion is None:
            if input('nenhuma sugestão encontrada, deseja continuar? [s]: ').lower() == 'n':
                break
            else:
                continue

        product = Product(
            artist = get_artist_name(suggestion.artist),
            album = get_album_name(suggestion.album),
            price = get_price(),
            gatefold_quantity = get_gatefold_quantity(),
            lps_quantity = get_lps_quantity(suggestion.lps_quantity),
            genres = get_genres(suggestion.genres),
            observation = get_observation(),
            is_national = is_national(suggestion.is_national),
            is_repeated = is_repeated(suggestion.is_repeated),
            is_double_covered = get_is_double_covered(suggestion.is_double_covered),
            pictures = get_pictures(),
            # campos opcionais
            song_quantity = suggestion.song_quantity or 1,
            album_duration = suggestion.album_duration or 0,
            release_year = suggestion.release_year or None,
            label = suggestion.label or None,
        )
        print('\nproduto cadastrado: ')
        display_product_information(product)
        
        if input('\ndeseja alterar algum valor? [s/N]: ').lower() == 's':
            product = change_product_values(product, suggestion)

        products.append(product)

        # atualiza arquivo products.json a cada produto cadastrado, a fim de não perder os dados
        save_json_products(products)

        if input('\ndeseja cadastrar mais produtos? [S/n]: ').lower() == 'n':
            break
    
    return products

def save_json_products(products: List[Product]):
    with open('./products.json', 'w') as file:
        json_products = []
        for product in products:
            json_product = {
                'artist': product.artist,
                'album': product.album,
                'price': product.price,
                'gatefold_quantity': product.gatefold_quantity,
                'lps_quantity': product.lps_quantity,
                'genres': product.genres,
                'is_national': product.is_national,
                'is_repeated': product.is_repeated,
                'is_double_covered': product.is_double_covered,
                'pictures': product.pictures,
                'song_quantity': product.song_quantity,
                'album_duration': product.album_duration,
                'release_year': product.release_year,
                'label': product.label,
                'observation': product.observation,
            }
            json_products.append(json_product)

        json.dump(json_products, file)
        
def delete_json_products():
    Path('./products.json').unlink()

def change_product_values(product: Product, suggestion: ProductSuggestion):
    while True:
        print('\nqual valor deseja alterar?')
        print('\tq: sair')
        print('\t0: nome do artista')
        print('\t1: nome do álbum')
        print('\t2: preço')
        print('\t3: quantidade de encartes')
        print('\t4: quantidade de discos')
        print('\t5: gênero(s)')
        print('\t6: nacional')
        print('\t7: repetido')
        choice = input('\nqual valor deseja alterar? [0]: ') or '0'
        match(choice):
            case 'q':
                break
            case '0':
                product.artist = get_artist_name(suggestion.artist)
            case '1':
                product.album = get_album_name(suggestion.album)
            case '2':
                product.price = get_price()
            case '3':
                product.gatefold_quantity = get_gatefold_quantity()
            case '4':
                product.lps_quantity = get_lps_quantity(suggestion.lps_quantity)
            case '5':
                product.genres = get_genres(suggestion.genres)
            case '6':
                product.is_national = is_national(suggestion.is_national)
            case '7':
                product.is_repeated = is_repeated(suggestion.is_repeated)
            case _:
                print('valor inválido, tente novamente!')
                continue

        print('\nproduto cadastrado: ')
        display_product_information(product)

        if input('\ndeseja alterar mais algum valor? [S/n]: ').lower() == 'n':
            break

    return product

def get_product_suggestion_with_discogs(client: discogs_client.Client) -> ProductSuggestion | None:
    vinyls = client.search(get_vinyl_code(), type='release')
    choice = None
    while True: 
        n = min(len(vinyls), 5)
        default = '0' if n > 0 else 'r'
        if n < 1:
            print("nenhum álbum com essa pesquisa foi encontrado")
        for i in range(n):
            print(f'{i}: {vinyls[i].title}. Ano de lançamento: {vinyls[i].year}. Format: {vinyls[i].formats[0]}. ' + \
                  f'País: {vinyls[i].country}. Código: {vinyls[i].labels[0].catno}')
        print('\nn: nenhum dos anteriores, não obter sugestões do discogs')
        print('r: pesquisar novamente')
        print('q: sair\n')
        choice = input(f'escolha uma das opções [{default}]: ') or default
        match(choice):
            case 'n':
                return NULL_SUGGESTION
            case 'r':
                vinyls = client.search(get_vinyl_code(), type='release')
                continue
            case 'q':
                return None
            case _:
                break

    vinyl_to_suggest = vinyls[int(choice)]
    suggestion_artist = ""
    suggestion_is_national = False

    # se o artista for "Various", não terá nome nem nacionalidade, por não ter perfil no discogs
    if vinyl_to_suggest.artists[0].name not in ["Various", "No Artist", "Unknown Artist" ]: 
        suggestion_artist = vinyl_to_suggest.artists[0].name
        suggestion_is_national = 'brazil' in vinyl_to_suggest.artists[0].profile.lower()

    return ProductSuggestion(
       artist = suggestion_artist,
       album = vinyl_to_suggest.title,
       lps_quantity = vinyl_to_suggest.formats[0]['qty'],
       genres = vinyl_to_suggest.genres,
       is_national = suggestion_is_national,
       is_repeated = False,
       is_double_covered = False,
       song_quantity = len(vinyl_to_suggest.tracklist),
       album_duration = get_album_duration(vinyl_to_suggest),
       release_year = vinyl_to_suggest.year if vinyl_to_suggest.year != "0" and vinyl_to_suggest else None,
       label = vinyl_to_suggest.labels[0].name,
       observation = None,
    )

def get_token() -> str:
    return CONFIG['token']

def get_client(token: str) -> discogs_client.Client:
    return discogs_client.Client('vinylizer/0.1', user_token=token)

def get_album_name(suggestion: Optional[str]) -> str:
    return get_field_with_suggestion('nome do álbum', suggestion=suggestion)

def get_artist_name(suggestion: Optional[str]) -> str:
    return get_field_with_suggestion('nome do artista', suggestion=suggestion)

def get_is_double_covered(suggestion: Optional[bool]) -> bool:
    return get_field_with_suggestion('capa dupla (S/n)', cast_function=tobool, suggestion=suggestion)

def get_vinyl_code() -> str:
    return input('pesquisa do vinil: ')

def tobool(value: str) -> bool:
    if value.lower() == 's':
        return True
    elif value.lower() == 'n':
        return False

    raise ValueError('valor inválido!')

def is_national(suggestion: Optional[bool]) -> bool:
    return get_field_with_suggestion('nacional (S/n)', cast_function=tobool, suggestion=suggestion is not None and suggestion or False)

def is_repeated(suggestion: Optional[bool]) -> bool:
    return get_field_with_suggestion('repetido (S/n)', cast_function=tobool, suggestion=suggestion is not None and suggestion or False)

def get_pictures() -> List[str]:
    products = []
    if platform.system() == 'Linux':
       products = get_pictures_binux()
    else:
        products = get_pictures_bindows()

    # this is done because normally the main photo is the last one in the list
    products = products[-1:] + products[:-1]

    return products

def get_pictures_binux() -> List[str]:
    return input('drag n\' drop: ').strip(' ').split(' ')

def get_pictures_bindows() -> List[str]:
    return QtWidgets.QFileDialog.getOpenFileNames(None, "selecionar fotos", CONFIG["pictures_path"], "image files (*.png *.jpg)")[0]

def get_observation() -> str:
    return get_field_with_suggestion('observação', cast_function=str, suggestion='')

def get_price() -> float:
    return get_field_with_suggestion('preço', cast_function=float, suggestion=30)

def get_gatefold_quantity() -> int:
    return get_field_with_suggestion('quantidade de encartes', cast_function=int, suggestion=0)

def get_lps_quantity(suggestion: Optional[int]) -> int:
    return get_field_with_suggestion('quantidade de discos', cast_function=int, suggestion=suggestion or 1)

def get_ml_spreadsheet() -> str:
    return QtWidgets.QFileDialog.getOpenFileName(None, "Selecione a planilha do ML", CONFIG["spreadsheet_directory_path"], "ml spreadsheet (*.xlsx)")[0]

def get_shopify_spreadsheet() -> str:
    return str(Path(CONFIG["spreadsheet_directory_path"]) / 'shopify.csv')

def get_genres(suggested_genres: List[str]) -> List[str]:
    print("selecione alguns dos gêneros encontrados e/ou digite novos, separando por vírgula: ")
    for i, possible_genre in enumerate(suggested_genres):
        print(f"\t{i}: {possible_genre}")
    
    # pode escolher os gêneros padrões e/ou digitar um novo, caso contrário pega o primeiro gênero padrão
    if len(suggested_genres) > 0:
        choices = input(f'\ngênero [{suggested_genres[0]}]: ') or "0"
    else:
        choices = input(f'\ngênero: ')
    
    genres = []
    for choice in choices.split(','):
        choice = choice.strip(' ')
        if choice.isdigit():
            while int(choice) >= len(suggested_genres):
                print(f"número {choice} é inválido, selecione um número entre 0 e {len(suggested_genres) - 1}")
                choice = input('\ngênero: ')
            genres.append(suggested_genres[int(choice)])
        else:
            genres.append(choice)

    return genres

def get_song_duration(song: discogs_client.Track) -> timedelta:
    minutes, seconds = song.duration.split(':')
    return timedelta(minutes=int(minutes), seconds=int(seconds))

def get_album_duration(vinyl: discogs_client.Release) -> float:
    total_duration = 0
    for song in vinyl.tracklist:
        if not song.duration:
            continue
        duration = get_song_duration(song)
        total_duration += duration.total_seconds() / 60

    return total_duration

T = TypeVar('T')
def get_field_with_suggestion(
    field_description: str,
    cast_function: Callable[[str], T] = str,
    suggestion: Optional[T] = None
) -> T:
    prompt_text = f'{field_description}'
    if suggestion is not None:
        prompt_text += f' [{suggestion}]'
    prompt_text += ': '

    while True:
        input_value = input(prompt_text)
        if input_value == '':
            if suggestion is not None:
                return suggestion

            print('valor é obrigatório, tente novamente!')
            continue

        # Tentaremos converter o valor digitado pro tipo que é desejado por quem chamou
        # a função, e se falharmos o usuário irá ter que digitar de novo 
        try:
            return cast_function(input_value)
        except:
            print('valor inválido, tente novamente!')
            continue

def display_product_information(product: Product):
    print(f'\tnome do artista: {product.artist}')
    print(f'\tnome do álbum: {product.album}')
    print(f'\tpreço: R${product.price}')
    print(f'\tquantidade de encartes: {product.gatefold_quantity}')
    print(f'\tquantidade de discos: {product.lps_quantity}')
    print(f'\tgênero(s): {product.genres}')
    print(f'\tnacional: {product.is_national}')
    print(f'\trepetido: {product.is_repeated}')

def get_resume_sheet_path() -> str:
    data = datetime.now().strftime("%d.%m.%Y")
    return str(Path(CONFIG["resume_directory_path"]) / f'Relação {data}.xlsx')


if __name__ == "__main__":
    main()

