from dataclasses import dataclass
from functools import cached_property
from vinylizer.picture_handler import upload_picture
from typing import Optional
from vinylizer.edit_title import edit_title
import requests

ML_CHARACTER_LIMIT = 60
QUANTITY_TRANSLATION = {
    2: "Duplo",
    3: "Triplo",
    4: "Quádruplo",
    5: "Quíntuplo",
    6: "Sêxtuplo",
    7: "Sétuplo",
    8: "Óctuplo",
    9: "Nônuplo",
}

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
    is_double_covered: bool
    pictures: list[str]
    song_quantity: Optional[int]
    album_duration: Optional[float]
    release_year: Optional[int]
    label: Optional[str]
    observation: Optional[str]
    
    @cached_property
    def picture_urls(self):
        uploaded_pictures = []
        for picture in self.pictures:
            status = 0
            uploaded_picture = upload_picture(picture)
            while status != 200:
                response = requests.get(uploaded_picture)
                status = response.status_code
            uploaded_pictures.append(uploaded_picture)

        return uploaded_pictures

    @property
    def description(self):
        gatefold_description = ""
        lps_description = ""
        observation_description = self.observation if self.observation else ""

        if self.gatefold_quantity >= 2:
            gatefold_description = "COM ENCARTES. "
        elif self.gatefold_quantity == 1:
            gatefold_description = "COM ENCARTE. "

        if self.lps_quantity == 2:
            lps_description = "DISCO DUPLO. "

        if self.is_double_covered:
            lps_description += "CAPA DUPLA."

        return f"PRODUTO USADO EM BOM ESTADO.\n{gatefold_description} {lps_description}\n{observation_description}"

    @property
    def nationality_text(self):
        nationalityText = "brasil"
        if not self.is_national:
            nationalityText = "internacional"
        
        return nationalityText.title()

    @cached_property
    def title(self):
        album = self.album
        if album == self.artist:
            album = self.release_year or None
        title = f"Lp Vinil {self.artist} {album}"
        if self.is_repeated:
            title = f"Disco Vinil {album} {self.artist}"
        double = ""

        if self.is_double_covered:
            double = "Capa Dupla"
        if self.lps_quantity > 1 and self.lps_quantity < 10:
            double = QUANTITY_TRANSLATION[self.lps_quantity]

        title += f" {double}"
        
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

        if len(title) > ML_CHARACTER_LIMIT:
            title = edit_title(title)

        return title
