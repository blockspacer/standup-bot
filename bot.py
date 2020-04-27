# -*- coding: utf-8 -*-
import telegram

import datetime

import config
from handler_callbacks import inline_queries
from handler_callbacks import job_handlers
from handler_callbacks import message_handlers
from db import DB


bot = telegram.Bot(config.TG_BOT_TOKEN)
jobs_queue = telegram.ext.JobQueue(bot=bot)


def main():
    updater = telegram.ext.Updater(bot=bot)

    message_handler = telegram.ext.MessageHandler(
        filters=telegram.ext.Filters.all,
        callback=message_handlers.message_handler_callback,
    )

    inline_query_handler = telegram.ext.InlineQueryHandler(
        callback=inline_queries.inline_query_callback,
    )

    hour, minute = DB().get_standup_time().split(':')
    jobs_queue.run_daily(
        callback=job_handlers.standup_job_handler_callback,
        time=datetime.time(hour=int(hour), minute=int(minute)),
        days=(0, 1, 2, 3, 4),
    )
    jobs_queue.start()

    updater.dispatcher.add_handler(handler=message_handler)
    updater.dispatcher.add_handler(handler=inline_query_handler)

    updater.start_polling(poll_interval=3.0)
    updater.idle()


if __name__ == '__main__':
    main()
