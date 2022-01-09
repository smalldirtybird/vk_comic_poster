import argparse
import requests
from dotenv import load_dotenv
import os
import urllib
import random
import shutil
from pprint import pprint


def get_random_comic_url():
    current_comic_url = 'https://xkcd.com/info.0.json'
    response = requests.get(current_comic_url)
    response.raise_for_status()
    current_comic_number = response.json()['num']
    random_comic_number = random.choice(range(1, current_comic_number + 1))
    return f'https://xkcd.com/{random_comic_number}/info.0.json'


def get_comic_with_comment(url):
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


def download_comic(url, folder):
    image_url, comment = get_comic_with_comment(url)
    filename = 'comic'
    image_extension = get_image_extension(image_url)
    path = os.path.join(folder,
                        f'{filename}{image_extension}')
    os.makedirs(folder, exist_ok=True)
    download_image(image_url, path)
    return path, comment


def get_photo_upload_url(params):
    host = 'https://api.vk.com/method/'
    method = 'photos.getWallUploadServer'
    url = os.path.join(host, method)
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def upload_photo_to_server(url, filepath):
    with open(filepath, 'rb') as file:
        image = {
            'photo': file
            }
        response = requests.post(url, files=image)
        response.raise_for_status()
        return response.json()


def save_wall_photo(params, photo_parameters):
    host = 'https://api.vk.com/method/'
    method = 'photos.saveWallPhoto'
    url = os.path.join(host, method)
    parameters.update(photo_parameters)
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['response'][0]['owner_id'],\
        response.json()['response'][0]['id']


def wall_post_comics(params, media_owner_id, post_media_id, comment):
    host = 'https://api.vk.com/method/'
    method = 'wall.post'
    url = os.path.join(host, method)
    post_owner_id = f'-{params.pop("group_id")}'
    post_from_group_checkbox = '1'
    post_attachment = f'photo{media_owner_id}_{post_media_id}'
    params['owner_id'] = post_owner_id
    params['from_group'] = post_from_group_checkbox
    params['attachments'] = post_attachment
    params['message'] = comment
    response = requests.post(url, params=params)
    response.raise_for_status()
    if 'error' in response.json():
        error_code = response.json()['error']['error_code']
        error_message = response.json()['error']['error_msg']
        return f'''
            Error code: {error_code}.
            Error message: {error_message}.
            Check VK API documentation: https://dev.vk.com/reference/errors.
            '''
    else:
        return 'Comic successfully published!'


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
    parameters = {
        'access_token': vk_access_token,
        'v': vk_api_version,
        'group_id': vk_group_id
        }
    comic_folder = get_arguments()
    comic_url = get_random_comic_url()
    comic_path, comic_comment = download_comic(
        comic_url, comic_folder)
    photo_upload_url = get_photo_upload_url(parameters)
    uploaded_photo_parameters = upload_photo_to_server(
        photo_upload_url, comic_path)
    owner_id, media_id = save_wall_photo(parameters, uploaded_photo_parameters)
    comic_post_result = wall_post_comics(parameters, owner_id, media_id, comic_comment)
    print(comic_post_result)
    shutil.rmtree(comic_folder)
