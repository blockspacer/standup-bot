import os
import datetime
from telegram import User
from telegram import Message

import config


class Logger:
    def __init__(self) -> None:
        self.log_file_path = 'data/log.txt'

    def log(self, user: User, message: Message) -> None:
        if (
                message.chat_id != config.TB_CHAT_ID
                and message.chat_id != config.MY_LOCAL_CHAT_ID
        ):
            with open(self.log_file_path, 'a') as log_file:
                log_text = '  '.join(
                    [
                        str(message.date),
                        user.name,
                        user.first_name if user.first_name else '',
                        user.last_name if user.last_name else '',
                        message.text,
                    ],
                )
                log_text.replace('\n', '')
                log_file.write(log_text + '\n')

    def error(self, text: str) -> None:
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(
                'ERROR: '
                + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                + ' '
                + text
                + '\n',
            )

    def get_logfile_path(self) -> str:
        return self.log_file_path

    def clear(self) -> None:
        os.remove(self.log_file_path)
        with open(self.log_file_path, 'a'):
            os.utime(self.log_file_path, None)
