import telegram
import re
import os
import typing

from db import DB
from functions import tts_api_request


def inline_query_callback(bot: telegram.Bot, update: telegram.Update):
    query = update.inline_query

    if re.search('стикер', query.query) is not None:
        results: typing.List[telegram.InlineQueryResultCachedSticker] = []

        for sticker_file_id in DB().get_stickers_with_limit(50):
            results.append(
                telegram.InlineQueryResultCachedSticker(
                    id=sticker_file_id[30:], sticker_file_id=sticker_file_id,
                ),
            )
        bot.answer_inline_query(inline_query_id=query.id, results=results)
    # TODO: make it work properly
    elif re.match('голос', query.query) is not None:
        text = query.query[5:]
        voice_filename = tts_api_request.get_voice_file(text=text)
        with open(voice_filename, 'rb') as f:
            voice_result = telegram.InlineQueryResultVoice(
                id=voice_filename[-6:], voice_url=f,
            )
            bot.answer_inline_query(
                inline_query_id=query.id, results=[voice_result],
            )
        os.remove(voice_filename)
