import io
import requests
from PIL import Image, ImageOps
from typing import List

def compress_picture(picture: str) -> io.BytesIO:
    remove_exif(picture)
    compressed_picture = io.BytesIO()
    Image.open(picture).save(compressed_picture, optimize=True, quality=80, format='WEBP')
    compressed_picture.seek(0)
    return compressed_picture

def upload_picture(picture: str) -> str:
    compressed_picture = compress_picture(picture)
    response = requests.post(
        'https://litterbox.catbox.moe/resources/internals/api.php', 
        files={'fileToUpload': ('photo.webp', compressed_picture, 'image/webp')}, 
        data={'reqtype': 'fileupload', 'time': '12h'},
    )
    response.raise_for_status()

    return response.text
    

def remove_exif(picture: str) -> None:
    image = Image.open(picture)
    image = ImageOps.exif_transpose(image)
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)
    image_without_exif.save(picture)
