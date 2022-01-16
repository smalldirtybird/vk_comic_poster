import argparse
import requests
from dotenv import load_dotenv
import os
import urllib
import random


class VkApiError(Exception):
    pass


def check_vk_api_error(response):
    if 'error' in response:
        error = response['error']
        raise VkApiError(f'''
            Error code: {error['error_code']}.
            Error message: {error['error_msg']}.
            Check VK API documentation: https://dev.vk.com/reference/errors.
            ''')


def get_random_comic_number():
    current_comic_url = 'https://xkcd.com/info.0.json'
    response = requests.get(current_comic_url)
    response.raise_for_status()
    current_comic_number = response.json()['num']
    return random.randint(1, current_comic_number)


def get_comic_with_comment(number):
    url = f'https://xkcd.com/{number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic = response.json()
    return comic['img'], comic['alt']


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


def download_comic(url, folder):
    image_url, comment = get_comic_with_comment(url)
    filename = 'comic'
    image_extension = get_image_extension(image_url)
    path = os.path.join(folder,
                        f'{filename}{image_extension}')
    os.makedirs(folder, exist_ok=True)
    download_image(image_url, path)
    return path, comment


def get_photo_upload_url(access_token, api_version, group_id):
    host = 'https://api.vk.com/method/'
    method = 'photos.getWallUploadServer'
    url = os.path.join(host, method)
    params = {
        'access_token': access_token,
        'v': api_version,
        'group_id': group_id
        }
    response = requests.get(url, params=params)
    parameters_for_upload = response.json()
    check_vk_api_error(parameters_for_upload)
    response.raise_for_status()
    return parameters_for_upload['response']['upload_url']


def upload_photo_to_server(url, filepath):
    with open(filepath, 'rb') as file:
        image = {
            'photo': file
            }
        response = requests.post(url, files=image)
    response.raise_for_status()
    uploaded_photo_parameters = response.json()
    return uploaded_photo_parameters['hash'],\
        uploaded_photo_parameters['photo'],\
        uploaded_photo_parameters['server']


def save_wall_photo(access_token, api_version, group_id,
                    photo_hash, photo, photo_server):
    host = 'https://api.vk.com/method/'
    method = 'photos.saveWallPhoto'
    url = os.path.join(host, method)
    params = {
        'access_token': access_token,
        'v': api_version,
        'group_id': group_id,
        'hash': photo_hash,
        'photo': photo,
        'server': photo_server
        }
    response = requests.get(url, params=params)
    response.raise_for_status()
    saved_photo_parameters = response.json()
    check_vk_api_error(saved_photo_parameters)
    return saved_photo_parameters['response'][0]['owner_id'],\
        saved_photo_parameters['response'][0]['id']


def wall_post_comics(access_token, api_version, group_id,
                     media_owner_id, post_media_id, comment):
    host = 'https://api.vk.com/method/'
    method = 'wall.post'
    url = os.path.join(host, method)
    post_owner_id = f'-{group_id}'
    post_from_group_checkbox = '1'
    post_attachment = f'photo{media_owner_id}_{post_media_id}'
    params = {
        'access_token': access_token,
        'v': api_version,
        'group_id': group_id,
        'owner_id': post_owner_id,
        'from_group': post_from_group_checkbox,
        'attachments': post_attachment,
        'message': comment
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    check_vk_api_error(response.json())


def get_arguments():
    parser = argparse.ArgumentParser(
        description='Загрузка комиксов xkcd на страницу Вконтакте')
    parser.add_argument(
        '-dir', '--directory', default='images',
        help='Путь к папке для скачанных картинок')
    args = parser.parse_args()
    return args.directory


if __name__ == '__main__':
    load_dotenv()
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_api_version = '5.131'
    vk_group_id = os.environ['VK_GROUP_ID']
    try:
        comic_folder = get_arguments()
        comic_number = get_random_comic_number()
        comic_path, comic_comment = download_comic(
            comic_number, comic_folder)
        photo_upload_url = get_photo_upload_url(
            vk_access_token, vk_api_version, vk_group_id)
        uploaded_photo_hash, uploaded_photo, uploaded_photo_server = \
            upload_photo_to_server(photo_upload_url, comic_path)
        owner_id, media_id = save_wall_photo(vk_access_token, vk_api_version,
                                             vk_group_id, uploaded_photo_hash,
                                             uploaded_photo,
                                             uploaded_photo_server)
        wall_post_comics(vk_access_token, vk_api_version, vk_group_id,
                         owner_id, media_id, comic_comment)
    except VkApiError as vk_error:
        print(vk_error)
    finally:
        os.remove(comic_path)
