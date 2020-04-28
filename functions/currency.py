import requests
import string
import re
import typing
from bs4 import BeautifulSoup

from logger import Logger


def fetch_currency_name(text: str) -> typing.Optional[str]:
    text.lstrip()
    text.rstrip()
    splitted = text.split(sep=' ')
    if len(splitted) == 2:
        return splitted[1]
    else:
        return None


def get_currency(currency_name: str) -> str:
    currency_url = f'https://yandex.ru/search/?text=курс+{currency_name}&lr=213&suggest_reqid=247412511158125217125918569019883'
    full_page = requests.get(currency_url)

    try:
        soup = BeautifulSoup(full_page.content, 'html.parser')

        converts = soup.findAll(
            'input', {'class': 'input__control', 'maxlength': '20'},
        )

        if len(converts) != 2:
            return ''
        target_currency_str = converts[1]['value'].replace(',', '.')
        if re.match('биткоин', currency_name) is not None:
            return target_currency_str
        elif re.match('рубл', currency_name) is not None:
            return '1'

        rub_currency = float(converts[0]['value'].replace(',', '.'))
        target_currency = float(target_currency_str)

        return str(round(target_currency / rub_currency, 2))
    except Exception:
        Logger().error('exception in get_currency')
        return
