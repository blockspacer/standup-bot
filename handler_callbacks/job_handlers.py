import telegram
from telegram.ext import JobQueue

import datetime
import random
import time

from db import DB
from logger import Logger
import config


def change_standup_job_schedule(
        jobs_queue: JobQueue, time_str: str, hour: int, minute: int,
):
    jobs_queue.stop()

    jobs = jobs_queue.jobs()
    for job in jobs:
        job.schedule_removal()

    DB().set_standup_time(time_str)

    jobs_queue.run_daily(
        callback=standup_job_handler_callback,
        time=datetime.time(hour=hour, minute=minute),
        days=(0, 1, 2, 3, 4),
    )
    jobs_queue.start()
    Logger().clear()


def standup_job_handler_callback(bot: telegram.Bot, job):
    chat_id = config.TB_CHAT_ID
    shuffled_members = config.MEMBERS_TAGS.copy()
    random.shuffle(shuffled_members)
    team_members_str = ' '.join(shuffled_members) + '\n\n'

    standup_call_text = (
        team_members_str
        + '\n'
        + random.choice(config.STANDUP_CALL_PHRASES)
        + '\n\n'
        + config.ZOOM_REFERENCE
    )

    bot.send_message(chat_id=chat_id, text=standup_call_text)

    queue_text = 'Очередность: \n\n'
    for tag in shuffled_members:
        queue_text += config.TAG_TO_NAME_MAP[tag] + '\n'

    time.sleep(1)
    bot.send_message(chat_id=chat_id, text=queue_text)

    random_sticker = random.choice(DB().get_stickers())
    time.sleep(1)
    bot.send_sticker(chat_id=chat_id, sticker=random_sticker)

    time.sleep(1)
    # Aurora location
    bot.send_location(
        chat_id=chat_id,
        latitude=55.734700,
        longitude=37.64260,
        live_period=2400,
    )
