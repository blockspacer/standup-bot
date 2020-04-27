import telegram
import re
import typing

from db import DB


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
