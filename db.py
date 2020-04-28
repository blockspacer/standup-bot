import os
import typing
import random


class DB:
    def __init__(self) -> None:
        self.standup_time_file_path = (
            '/home/amaxacla/telegram_bot/data/standup_time.txt'
        )
        self.stickers_dir_path = '/home/amaxacla/telegram_bot/data/stickers'
        self.stickers: typing.List[str] = os.listdir(self.stickers_dir_path)

    def get_standup_time(self) -> str:
        with open(self.standup_time_file_path, 'r') as file:
            return file.read()

    def set_standup_time(self, time: str) -> None:
        with open(self.standup_time_file_path, 'w') as file:
            file.write(time)

    def get_stickers(self) -> typing.List[str]:
        return self.stickers

    def get_stickers_with_limit(self, limit: int) -> typing.List[str]:
        if len(self.stickers) <= limit:
            return self.stickers

        stickers = self.stickers
        random.shuffle(stickers)
        return stickers[:limit]

    def add_sticker(self, file_id: str) -> None:
        if file_id not in self.stickers:
            self.stickers.append(file_id)
            sticker_filename = '/'.join([self.stickers_dir_path, file_id])
            with open(sticker_filename, 'w'):
                pass
