import io
import requests
from PIL import Image
from typing import List

def compress_picture(picture: str) -> io.BytesIO:
    compressed_picture = io.BytesIO()
    Image.open(picture).save(compressed_picture, optimize=True, quality=85, format='WEBP')
    compressed_picture.seek(0)
    return compressed_picture

def upload_pictures(pictures: List[str]) -> List[str]:
    picture_links = []
    for picture in pictures:
        compressed_picture = compress_picture(picture)
        response = requests.post(
            'https://litterbox.catbox.moe/resources/internals/api.php', 
            files={'fileToUpload': ('photo.webp', compressed_picture, 'image/webp')}, 
            data={'reqtype': 'fileupload', 'time': '12h'},
        )
        response.raise_for_status()
        picture_links.append(response.text)

    return picture_links
    

