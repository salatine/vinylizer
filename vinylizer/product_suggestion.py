from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductSuggestion:
    artist: Optional[str]
    album: Optional[str]
    lps_quantity: Optional[int]
    genres: list[str]
    is_national: Optional[bool]
    song_quantity: Optional[int]
    album_duration: Optional[float]
    release_year: Optional[int]
    label: Optional[str]

    NULL_SUGGESTION = ProductSuggestion(
        artist = None,
        album = None,
        lps_quantity = None,
        genres = [],
        is_national = None,
        song_quantity = None,
        album_duration = None,
        release_year = None,
        label = None,
    )
