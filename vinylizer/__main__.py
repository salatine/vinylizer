from pathlib import Path
import discogs_client
import tomli
from typing import List
from PySide6 import QtWidgets
import platform
from vinylizer.Product import Product
from vinylizer.shopify_exporter import export_to_shopify_spreadsheet
from vinylizer.ml_exporter import export_to_ml_spreadsheet
from datetime import timedelta

with open('./config.toml', 'rb') as file:
    CONFIG = tomli.load(file)

def main():
    QtWidgets.QApplication([])
    client = get_client(get_token())
    products = []

    while True:
        vinyl = get_vinyl(client)
        if vinyl is None:
            if input('nenhum vinil encontrado, deseja continuar? [s]: ').lower() == 'n':
                break
            else:
                continue

        product = Product(
            artist = get_artist_name(vinyl),
            album = get_album_name(vinyl),
            price = get_price(),
            gatefold_quantity = get_gatefold_quantity(),
            lps_quantity = get_lps_quantity(vinyl),
            genres = get_genres(vinyl),
            is_national = is_national(vinyl),
            pictures = get_pictures(),
            song_quantity = len(vinyl.tracklist), # pyright: ignore
            album_duration = get_album_duration(vinyl), # pyright: ignore
            release_year = vinyl.year,
            label = vinyl.labels[0].name, # pyright: ignore
        )
        products.append(product)

        if input('deseja continuar? [s]: ').lower() == 'n':
            break

    export_to_shopify_spreadsheet(get_shopify_spreadsheet(), products) 
    export_to_ml_spreadsheet(get_ml_spreadsheet(), products) 

def get_vinyl(client: discogs_client.Client) -> discogs_client.Release | None:
    vinyls = client.search(get_vinyl_code(), type='release')
    while len(vinyls) < 1:
        print('nenhum álbum encontrado, digite novamente\n')
        vinyls = client.search(get_vinyl_code(), type='release')

    if len(vinyls) > 5:
        vinyls = vinyls[:5]
    for i in range(vinyls):
        print(f'{i}: {vinyls[i].title}')
    print('n: nenhum dos anteriores, não obter sugestões do discogs\n')

    choice = input('escolha um álbum: ')
    if choice.lower() == 'n':
        return None
    return vinyls[int(choice)]

def get_token() -> str:
    return CONFIG['token']

def get_client(token: str) -> discogs_client.Client:
    return discogs_client.Client('vinylizer/0.1', user_token=token)

def get_album_name(vinyl) -> str:
    return input(f'nome do álbum [{vinyl.title}]: ') or vinyl.title

def get_artist_name(vinyl) -> str:
    return input(f'nome do artista [{vinyl.artists[0].name}]: ') or vinyl.artists[0].name

def get_vinyl_code() -> str:
    return input('vinyl code: ')

def is_national(vinyl: discogs_client.Release) -> bool:
    return 'brazil' in vinyl.artists[0].profile.lower()

def get_pictures() -> List[str]:
    if platform.system() == 'Linux':
        return get_pictures_binux()
    return get_pictures_windows()

def get_pictures_binux() -> List[str]:
    return input('drag n\' drop: ').strip(' ').split(' ')

def get_pictures_windows() -> List[str]:
    return QtWidgets.QFileDialog.getOpenFileNames(None, "selecionar fotos", CONFIG["pictures_path"], "image files (*.png *.jpg)")[0]

def get_price() -> float:
    price = input('preço [30]: ') or "30"
    return float(price)

def get_gatefold_quantity() -> int:
    quantity = input('quantidade de encartes [0]: ')
    if not quantity:
        return 0
    return int(quantity)

def get_lps_quantity(vinyl) -> int:
    lps_quantity = vinyl.formats[0]['qty']
    quantity = input(f'quantidade de discos [{lps_quantity}]: ')

    if not quantity:
        return lps_quantity
    return int(quantity)

def get_ml_spreadsheet() -> str:
    return QtWidgets.QFileDialog.getOpenFileName(None, "Selecione a planilha do ML", CONFIG["spreadsheet_directory_path"], "ml spreadsheet (*.xlsx)")[0]

def get_shopify_spreadsheet() -> str:
    return str(Path(CONFIG["spreadsheet_directory_path"]) / 'shopify.csv')

def get_genres(vinyl: discogs_client.Release) -> List[str]:
    genres = []
    possible_genres: List[str] = vinyl.genres # pyright: ignore
    print("selecione alguns dos gêneros encontrados e/ou digite novos, separando por vírgula: ")
    for i, possible_genre in enumerate(possible_genres):
        print(f"\t{i}: {possible_genre}")
    
    # pode escolher os gêneros padrões e/ou digitar um novo, caso contrário pega o primeiro gênero padrão
    choices = input(f'\ngênero [{possible_genres[0]}]: ') or "0"

    for choice in choices.split(','):
        choice = choice.strip(' ')
        if choice.isdigit():
            while int(choice) >= len(possible_genres):
                print(f"número {choice} é inválido, selecione um número entre 0 e {len(possible_genres) - 1}")
                choice = input('\ngênero: ')
            genres.append(possible_genres[int(choice)])
        else:
            genres.append(choice)

    return genres

def get_song_duration(song: discogs_client.Track) -> timedelta:
    minutes, seconds = song.duration.split(':')
    return timedelta(minutes=int(minutes), seconds=int(seconds))

def get_album_duration(vinyl: discogs_client.Release) -> float:
    total_duration = 0
    for song in vinyl.tracklist:
        duration = get_song_duration(song)
        total_duration += duration.total_seconds() / 60

    return total_duration
if __name__ == "__main__":
    main()

