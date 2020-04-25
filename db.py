class DB:
    def __init__(self) -> None:
        self.standup_time_file_path = 'data/standup_time.txt'

    def get_standup_time(self) -> str:
        with open(self.standup_time_file_path, 'r') as file:
            return file.read()

    def set_standup_time(self, time: str) -> None:
        with open(self.standup_time_file_path, 'w') as file:
            file.write(time)
