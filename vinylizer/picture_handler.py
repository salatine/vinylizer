import io
import requests
from PIL import Image, ImageOps
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

def compress_picture(picture: str) -> io.BytesIO:
    remove_exif(picture)
    compressed_picture = io.BytesIO()
    Image.open(picture).save(compressed_picture, optimize=True, quality=80, format='WEBP')
    compressed_picture.seek(0)
    return compressed_picture

def upload_picture(picture: str) -> str:
    compress_picture(picture)
    formatDate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file = drive.CreateFile(metadata={"title": "{0}.webp".format(formatDate), 'mimeType': 'image/webp'})
    file.SetContentFile(picture)  # Set content of the file from given string.
    file.Upload(param={'supportsTeamDrives': True})

    access_token = gauth.credentials.access_token # gauth is from drive = GoogleDrive(gauth) Please modify this for your actual script.
    file_id = file['id']
    url = 'https://www.googleapis.com/drive/v3/files/' + file_id + '/permissions?supportsAllDrives=true'
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    payload = {'type': 'anyone', 'value': 'anyone', 'role': 'reader'}
    res = requests.post(url, data=json.dumps(payload), headers=headers)
    link = file['alternateLink']

    # change to a downloadable link
    link = link.replace("drive.google.com", "drive.usercontent.google.com").replace("file/d/", "download?id=")
    link = link[:link.rfind('/')]

    return link

def remove_exif(picture: str) -> None:
    image = Image.open(picture)
    image = ImageOps.exif_transpose(image)
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)
    image_without_exif.save(picture)
