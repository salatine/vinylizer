from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductSuggestion:
    artist: Optional[str]
    album: Optional[str]
    lps_quantity: Optional[int]
    genres: list[str]
    is_national: Optional[bool]
    is_repeated: Optional[bool]
    song_quantity: Optional[int]
    album_duration: Optional[float]
    release_year: Optional[int]
    label: Optional[str]
    observation: Optional[str]

NULL_SUGGESTION = ProductSuggestion(None, None, None, [], None, None, None, None, None, None, None)

