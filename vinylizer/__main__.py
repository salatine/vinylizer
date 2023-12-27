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
from datetime import timedelta

with open('./config.toml', 'rb') as file:
    CONFIG = tomli.load(file)

def main():
    QtWidgets.QApplication([])
    client = get_client(get_token())
    products = []

    while True:
        suggestion = get_product_suggestion_with_discogs(client)
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
            is_national = is_national(suggestion.is_national),
            pictures = get_pictures(),

            # campos opcionais
            song_quantity = suggestion.song_quantity or 1,
            album_duration = suggestion.album_duration or 0,
            release_year = suggestion.release_year or None,
            label = suggestion.label or None,
        )
        products.append(product)
        if input('deseja continuar? [S/n]: ').lower() == 'n':
            break

    export_to_shopify_spreadsheet(get_shopify_spreadsheet(), products) 
    export_to_ml_spreadsheet(get_ml_spreadsheet(), products) 

def get_product_suggestion_with_discogs(client: discogs_client.Client) -> ProductSuggestion:
    code = get_vinyl_code()
    vinyls = client.search(code, type='release')
    while len(vinyls) < 1:
        if input('nenhum álbum encontrado, deseja tentar procurar novamente? ' + \
            'caso contrário, iremos prosseguir sem as sugestões do discogs [s]: ').lower() == 'n':
            return NULL_SUGGESTION
        
        vinyls = client.search(code, type='release')
    
    n = min(len(vinyls), 5)
    for i in range(n):
        print(f'{i}: {vinyls[i].title}. Ano de lançamento: {vinyls[i].year}. Format: {vinyls[i].formats}\n')
    print('n: nenhum dos anteriores, não obter sugestões do discogs\n')

    choice = input('escolha um álbum [0]: ') or "0"
    if choice.lower() == 'n':
        return NULL_SUGGESTION

    vinyl_to_suggest = vinyls[int(choice)]
    suggestion_artist = ""
    suggestion_is_national = False

    # se o artista for "Various", não terá nome nem nacionalidade, por não ter perfil no discogs
    if vinyl_to_suggest.artists[0].name != "Various":
        suggestion_artist = vinyl_to_suggest.artists[0].name
        suggestion_is_national = 'brazil' in vinyl_to_suggest.artists[0].profile.lower()

    return ProductSuggestion(
       artist = suggestion_artist,
       album = vinyl_to_suggest.title,
       lps_quantity = vinyl_to_suggest.formats[0]['qty'],
       genres = vinyl_to_suggest.genres,
       is_national = suggestion_is_national,
       song_quantity = len(vinyl_to_suggest.tracklist),
       album_duration = get_album_duration(vinyl_to_suggest),
       release_year = vinyl_to_suggest.year,
       label = vinyl_to_suggest.labels[0].name,
    )

def get_token() -> str:
    return CONFIG['token']

def get_client(token: str) -> discogs_client.Client:
    return discogs_client.Client('vinylizer/0.1', user_token=token)

def get_album_name(suggestion: Optional[str]) -> str:
    return get_field_with_suggestion('nome do álbum', suggestion=suggestion)

def get_artist_name(suggestion: Optional[str]) -> str:
    return get_field_with_suggestion('nome do artista', suggestion=suggestion)

def get_vinyl_code() -> str:
    return input('vinyl code: ')

def tobool(value: str) -> bool:
    if value.lower() == 's':
        return True
    elif value.lower() == 'n':
        return False

    raise ValueError('valor inválido!')

def is_national(suggestion: Optional[bool]) -> bool:
    return get_field_with_suggestion('nacional (S/n)', cast_function=tobool, suggestion=suggestion is not None and suggestion or True)

def get_pictures() -> List[str]:
    if platform.system() == 'Linux':
       return get_pictures_binux()
    return get_pictures_bindows()

def get_pictures_binux() -> List[str]:
    return input('drag n\' drop: ').strip(' ').split(' ')

def get_pictures_bindows() -> List[str]:
    return QtWidgets.QFileDialog.getOpenFileNames(None, "selecionar fotos", CONFIG["pictures_path"], "image files (*.png *.jpg)")[0]

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

if __name__ == "__main__":
    main()

