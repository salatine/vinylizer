from dataclasses import dataclass
from functools import cached_property
from vinylizer.picture_handler import upload_pictures
from typing import Optional

@dataclass
class Product:
    artist: str
    album: str
    price: float
    gatefold_quantity: int
    lps_quantity: int
    genres: list[str]
    is_national: bool
    is_repeated: bool
    pictures: list[str]
    song_quantity: Optional[int]
    album_duration: Optional[float]
    release_year: Optional[int]
    label: Optional[str]
    observation: Optional[str]
    
    @cached_property
    def picture_urls(self):
        return upload_pictures(self.pictures)

    @property
    def description(self):
        gatefold_description = ""
        lps_description = ""
        observation_description = self.observation if self.observation else ""

        if self.gatefold_quantity >= 2:
            gatefold_description = f"COM ENCARTES."
        elif self.gatefold_quantity == 1:
            gatefold_description = "COM ENCARTE."

        if self.lps_quantity == 2:
            lps_description = f"DISCO DUPLO."

        return f"PRODUTO USADO EM BOM ESTADO.\n{gatefold_description} {lps_description}\n{observation_description}"

    @property
    def nationality_text(self):
        nationalityText = "brasil"
        if not self.is_national:
            nationalityText = "internacional"
        
        return nationalityText.title()

    @property
    def title(self):
        title = f"Lp Vinil {self.artist} {self.album}"
        if self.is_repeated:
            title = f"Disco Vinil {self.album} {self.artist}"

        if self.lps_quantity == 2:
            title += " Duplo"
        
        if self.gatefold_quantity >= 2:
            title += " Com Encartes"
        elif self.gatefold_quantity == 1:
            title += " Com Encarte"
        
        if self.is_repeated:
            title += " A"

        if self.observation:
            title += f", Leia"

        # remove double spaces if any
        title = " ".join(title.split())
        return title
