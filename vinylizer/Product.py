from dataclasses import dataclass
from functools import cached_property
from vinylizer.picture_handler import upload_pictures

@dataclass
class Product:
    artist: str
    album: str
    price: float
    gatefold_quantity: int
    lps_quantity: int
    genres: list[str]
    is_national: bool
    pictures: list[str]
    song_quantity: int
    album_duration: float
    release_year: int
    label: str
    
    @cached_property
    def picture_urls(self):
        return upload_pictures(self.pictures)

    @property
    def description(self):
        gatefold_description = ""
        lps_description = ""

        if self.gatefold_quantity >= 2:
            gatefold_description = f"COM ENCARTES."
        elif self.gatefold_quantity == 1:
            gatefold_description = "COM ENCARTE."

        if self.lps_quantity == 2:
            lps_description = f"DISCO DUPLO."

        return f"PRODUTO USADO EM BOM ESTADO.\n{gatefold_description} {lps_description}\n"

    @property
    def nationality_text(self):
        nationalityText = "brasil"
        if not self.is_national:
            nationalityText = "internacional"
        
        return nationalityText.title()

    @property
    def title(self):
        title = f"Lp Vinil {self.artist} {self.album}"
        if self.lps_quantity == 2:
            title += " Duplo"
        
        if self.gatefold_quantity >= 2:
            title += " Com Encartes"
        elif self.gatefold_quantity == 1:
            title += " Com Encarte"

        return title
