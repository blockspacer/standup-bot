import random
import requests
import string


DATA_PATH = '/home/amaxacla/telegram_bot/data'


def _get_random_filename(length=12):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def _synthesize(text: str, voice_actor: str):
    with open(DATA_PATH + '/iam_token.txt') as iam_token:
        url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
        headers = {'Authorization': 'Bearer ' + iam_token.read()}

        data = {
            'text': text,
            'lang': 'ru-RU',
            'voice': voice_actor,
            'folderId': 'b1gt79g5ode54ai6sfh7',
        }

        with requests.post(
                url, headers=headers, data=data, stream=True,
        ) as resp:
            if resp.status_code != 200:
                raise RuntimeError(
                    'Invalid response received: code: %d, message: %s'
                    % (resp.status_code, resp.text),
                )

            for chunk in resp.iter_content(chunk_size=None):
                yield chunk


def get_voice_file(text: str, voice_actor: str) -> str:
    file_name = '/'.join([DATA_PATH, 'sounds', _get_random_filename()])

    with open(file_name, 'wb') as f:
        for audio_content in _synthesize(text, voice_actor):
            f.write(audio_content)

    return file_name
