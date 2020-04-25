import requests
import string
import re
import random
import json
from logger import Logger
from bs4 import BeautifulSoup


def search_photo(photo_name: str) -> str:
    photo_url = f'https://yandex.ru/images/search?text={photo_name}&ncrnd=1587506362789-6466307030731739'
    try:
        full_page = requests.get(photo_url)

        soup = BeautifulSoup(full_page.content, 'html.parser')

        images = soup.findAll(
            'div',
            {
                'class': 'serp-item',
                'class': 'serp-item_type_search',
                'class': 'serp-item_group_search',
            },
        )

        image_index = random.randint(0, len(images) / 2)

        image_urles = json.loads(images[image_index]['data-bem'])['serp-item'][
            'dups'
        ]
        image_url_index = int(len(image_urles) / 2)

        return image_urles[image_url_index]['origin']['url']

    except Exception as exc:
        return ''
