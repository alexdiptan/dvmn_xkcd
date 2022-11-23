import os
import pathlib
import random

import requests
from dotenv import load_dotenv


def fetch_comics(img_url, image_filepath) -> None:
    response = requests.get(img_url)
    response.raise_for_status()
    with open(image_filepath, 'wb') as file:
        file.write(response.content)


def get_comics(comics_id):
    comics_url = f'https://xkcd.com/{comics_id}/info.0.json'
    response = requests.get(comics_url)
    response.raise_for_status()

    comics = response.json()

    return comics['img'], comics['alt']


def get_wall_upload_server(vk_token, group_id):
    url_params = {
        'group_id': group_id,
        'access_token': vk_token,
        'v': '5.131',
    }
    upload_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(upload_url, params=url_params)
    response.raise_for_status()

    return response.json()


def upload_image_to_vk(image, upload_url):
    with open(image, 'rb') as file:
        file_to_upload = {'photo': file}
        response = requests.post(upload_url, files=file_to_upload)
    response.raise_for_status()

    vk_response = response.json()

    return vk_response['server'], vk_response['photo'], vk_response['hash']


def save_wall_photo(group_id, photo, server, photo_hash, vk_token):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': photo_hash,
        'access_token': vk_token,
        'v': '5.131',
    }
    response = requests.post(url, params=params)
    response.raise_for_status()

    vk_response = response.json()

    return vk_response['response'][0]['owner_id'], vk_response['response'][0]['id']


def publish_photo_on_the_wall(media_id, owner_id, vk_group_id, message, vk_token):
    url = 'https://api.vk.com/method/wall.post'
    vk_attachments = f'photo{owner_id}_{media_id}'
    params = {
        'owner_id': f'-{vk_group_id}',
        'message': message,
        'from_group': '1',
        'attachments': vk_attachments,
        'access_token': vk_token,
        'v': '5.131',
    }
    response = requests.post(url, data=params)
    response.raise_for_status()

    return response.json()


def main():
    load_dotenv()
    vk_token = os.environ['VK_ACCESS_TOKEN']
    vk_group_id = os.environ['VK_GROUP_ID']
    comics_filename = 'image.jpg'
    start_comics_number = 1
    end_comics_number = 2700

    try:
        comics_img, comics_funny_comment, = get_comics(random.randint(start_comics_number, end_comics_number))
        fetch_comics(comics_img, comics_filename)

        server_for_upload_photo = get_wall_upload_server(vk_token, vk_group_id)['response']['upload_url']
        server, photo, photo_hash = upload_image_to_vk('image.jpg', server_for_upload_photo)

        owner_id, media_id = save_wall_photo(vk_group_id, photo, server, photo_hash, vk_token)
        publish_photo_on_the_wall(media_id, owner_id, vk_group_id, comics_funny_comment, vk_token)
    finally:
        file_to_remove = pathlib.Path(comics_filename)
        file_to_remove.unlink()


if __name__ == '__main__':
    main()
