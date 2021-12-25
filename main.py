import requests
from dotenv import load_dotenv
import os
import urllib
from pprint import pprint


def get_comic(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['img'], response.json()['alt']


def get_image_extension(url):
    parsed_url = urllib.parse.urlsplit(url, scheme='', allow_fragments=True)
    filepath = urllib.parse.unquote(parsed_url[2],
                                    encoding='utf-8', errors='replace')
    path, extension = os.path.splitext(filepath)
    return extension


def download_image(url, path, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    load_dotenv()
    comic_url = 'https://xkcd.com/614/info.0.json'
    image_url, comment = get_comic(comic_url)
    print(image_url, comment)
    image_folder = 'images'
    filename = 'comic'
    image_extension = get_image_extension(image_url)
    comic_path = os.path.join(image_folder,
                              f'{filename}{image_extension}')
    os.makedirs(image_folder, exist_ok=True)
    download_image(image_url, comic_path)
