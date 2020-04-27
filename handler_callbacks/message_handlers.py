import telegram
from telegram import KeyboardButton
from telegram import InlineKeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardMarkup
from telegram import Message

import datetime
import time
import random
import json
import os
import typing
import re

import config
import currency
from . import job_handlers
import userful_urls as urls
import invite_links as invs
from search_photo import search_photo
from select_pgsql import metrics_select
from logger import Logger
from db import DB
from bot import jobs_queue


db = DB()
logger = Logger()


def message_handler_callback(bot: telegram.Bot, update: telegram.Update):
    source_chat_id = update.message.chat_id
    text = update.message.text if update.message.text else ''
    text = text.lower()

    if (
            source_chat_id == config.TB_CHAT_ID
            or source_chat_id == config.MY_LOCAL_CHAT_ID
    ) and re.match('стендап', text) is not None:
        time_opt = re.search('[0-2][0-9]:[0-5][0-9]', text)
        if time_opt is not None:
            time_str = time_opt.group()
            hour, minute = time_str.split(':')
            if 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59:
                job_handlers.change_standup_job_schedule(
                    jobs_queue=jobs_queue,
                    time_str=time_str,
                    hour=int(hour),
                    minute=int(minute),
                )

                bot.send_message(
                    chat_id=source_chat_id,
                    text=f'Время стендапа изменено на {time_str}',
                )
    elif update.message.sticker:
        file_id = update.message.sticker.file_id
        db.add_sticker(file_id=file_id)
    elif re.search('стикер', text) is not None:
        random_file_id = random.choice(db.get_stickers())
        bot.send_sticker(chat_id=source_chat_id, sticker=random_file_id)
    elif re.search('дискорд', text) is not None:
        reply_text = 'Го дискорд \n\n ' + config.DISCORD_REFERENCE
        bot.send_message(chat_id=source_chat_id, text=reply_text)
    elif re.match('жив\?', text) is not None:
        reply_text = 'Да'
        bot.send_message(
            chat_id=source_chat_id,
            text=reply_text,
            reply_to_message_id=update.message.message_id,
        )
    elif re.match('курс', text) is not None:
        currency_name = currency.fetch_currency_name(text=text)
        if not currency_name:
            return

        currency_value = currency.get_currency(currency_name=currency_name)
        if currency_value:
            reply_text = f'Курс {currency_name} к рублю: ' + currency_value
            bot.send_message(
                chat_id=source_chat_id,
                text=reply_text,
                reply_to_message_id=update.message.message_id,
            )
    elif re.match('(когда|во сколько)\\ {1,}стендап', text) is not None:
        reply_text = 'Стендап в ' + db.get_standup_time()
        bot.send_message(chat_id=source_chat_id, text=reply_text)
    elif re.match('картинка', text) is not None:
        words = text.split(' ', maxsplit=1)
        if len(words) == 2:
            photo_url = search_photo(photo_name=words[1])
            if photo_url.startswith('http'):
                photo = telegram.InputMediaPhoto(
                    search_photo(photo_name=words[1]),
                )
                bot.send_media_group(
                    chat_id=source_chat_id, media=[photo], timeout=5,
                )
    elif re.match('бот.{1,}ты.*', text) is not None:
        reply_button = KeyboardButton(text='извини')

        keyboard_markup = ReplyKeyboardMarkup(keyboard=[[reply_button]])

        bot.send_message(
            chat_id=source_chat_id,
            reply_to_message_id=update.message.message_id,
            text='А может ты?',
            reply_markup=keyboard_markup,
        )
    elif text == 'извини':
        remove_reply_keyboard = telegram.ReplyKeyboardRemove()
        bot.send_message(
            chat_id=source_chat_id,
            text='Прощаю',
            reply_markup=remove_reply_keyboard,
            reply_to_message_id=update.message.message_id,
        )
    elif re.match('мои фото', text) is not None:
        limit = 10
        request_limit = re.search('лимит \d{1,2}', text)
        if request_limit is not None:
            _, limit_str = request_limit.group().split()
            limit = int(limit_str)
        photo_sizes = bot.get_user_profile_photos(
            user_id=update.effective_user.id, offset=0, limit=limit,
        ).photos
        photos_media: typing.List[telegram.InputMediaPhoto] = []
        for photo_size_chunk in photo_sizes:
            photos_media.append(
                telegram.InputMediaPhoto(media=photo_size_chunk[0]),
            )

        photos = telegram.InputMediaPhoto(media=photo_sizes[0][0])
        bot.send_media_group(
            chat_id=source_chat_id,
            reply_to_message_id=update.message.message_id,
            media=photos_media,
        )

    elif re.match('инвайт ссылки', text) is not None:
        keyboard = [
            [
                InlineKeyboardButton(
                    'автоматизация', url=invs.AUTOMATIZATION_SUPPORT,
                ),
                InlineKeyboardButton('админы', url=invs.ITO_HELPLINE),
                InlineKeyboardButton(
                    'userver support', url=invs.USERVER_SUPPORT,
                ),
            ],
            [
                InlineKeyboardButton(
                    'testsuite support', url=invs.TESTSUITE_SUPPORT,
                ),
                InlineKeyboardButton(
                    'platform support', url=invs.PLATFORM_SUPPORT,
                ),
                InlineKeyboardButton('RTC support', url=invs.RTC_SUPPORT),
            ],
            [
                InlineKeyboardButton(
                    'replication support', url=invs.REPLICATION_SUPPORT,
                ),
                InlineKeyboardButton(
                    'backend releases', url=invs.BACKEND_RELEASES,
                ),
                InlineKeyboardButton(
                    'taxi testing issues', url=invs.TAXI_TESTING_ISSUES,
                ),
            ],
            [
                InlineKeyboardButton(
                    'passport, blackbox support', url=invs.PASSPORT_BLACKBOX,
                ),
                InlineKeyboardButton('codegen support', url=invs.TAXI_CODEGEN),
                InlineKeyboardButton(
                    'experiments 3.0 support',
                    url=invs.TAXI_EXPERIMENTS_3_SUPPORT,
                ),
            ],
            [
                InlineKeyboardButton(
                    'personal data dev', url=invs.PERSONAL_DATA_DEV,
                ),
                InlineKeyboardButton('АБК support', url=invs.ABK_SUPPORT),
                InlineKeyboardButton('MDB support', url=invs.MDB_SUPPORT),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.send_message(
            chat_id=source_chat_id,
            text='инвайт ссылки:',
            reply_markup=reply_markup,
        )

    elif re.match('полезные ссылки', text) is not None:
        # teamlead_url = f'https://telegram.me/antontodua'

        keyboard = [
            [
                InlineKeyboardButton(
                    'wiki: введение в такси', url=urls.BASIC_HOWTO,
                ),
                InlineKeyboardButton(
                    'wiki: uservices', url=urls.USERVICES_DOC,
                ),
                InlineKeyboardButton(
                    'wiki: backend-py3', url=urls.BACKEND_PY3_DOC,
                ),
            ],
            [
                InlineKeyboardButton(
                    'админка прод', url=urls.TARIFF_EDITOR_PROD,
                ),
                InlineKeyboardButton(
                    'админка тестинг', url=urls.TARIFF_EDITOR_TESTING,
                ),
                InlineKeyboardButton(
                    'админка анстейбл', url=urls.TARIFF_EDITOR_UNSTABLE,
                ),
            ],
            [
                InlineKeyboardButton('кибана прод', url=urls.KIBANA_PROD),
                InlineKeyboardButton(
                    'кибана тестинг', url=urls.KIBANA_TESTING,
                ),
                InlineKeyboardButton(
                    'кибана анстейбл', url=urls.KIBANA_UNSTABLE,
                ),
            ],
            [
                InlineKeyboardButton('графана', url=urls.GRAFANA),
                InlineKeyboardButton('графит', url=urls.GRAPHITE),
            ],
            [
                InlineKeyboardButton(
                    'админка таксометра прод', url=urls.TAXIMETER_ADMIN_PROD,
                ),
                InlineKeyboardButton(
                    'админка таксометра тестинг',
                    url=urls.TAXIMETER_ADMIN_TESTING,
                ),
            ],
            [InlineKeyboardButton('кондуктор', url=urls.CONDUCTOR)],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.send_message(
            chat_id=source_chat_id,
            text='полезные ссылки:',
            reply_markup=reply_markup,
        )
    elif re.search('аврор', text) is not None:
        bot.send_location(
            chat_id=source_chat_id, latitude=55.734700, longitude=37.64260,
        )
    elif source_chat_id == config.MY_LOCAL_CHAT_ID and re.match('логи', text):
        strings_count = str()
        if text == 'логи':
            strings_count = 0
        else:
            _, strings_count = text.split(' ', 1)

        with open(logger.get_logfile_path(), 'r') as log_file:
            logs = [line for line in log_file]
            if 0 <= int(strings_count):
                bot.send_message(
                    chat_id=source_chat_id,
                    text=''.join(logs[-min(int(strings_count), len(logs)) :]),
                )
    elif (
        source_chat_id == config.MY_LOCAL_CHAT_ID
        or source_chat_id == config.TB_CHAT_ID
    ) and re.match('select \* from metrics.', text):
        bot.send_message(
            chat_id=source_chat_id,
            text=metrics_select(text),
            parse_mode=telegram.ParseMode.MARKDOWN,
        )

    logger.log(user=update.effective_user, message=update.effective_message)
