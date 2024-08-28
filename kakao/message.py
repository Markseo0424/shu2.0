from datetime import datetime


class Message:
    def __init__(self, date, time, user, msg):
        self.date = date
        self.time = time
        self.user = user
        self.msg = msg
        try:
            self.datetime = self.calc_datetime()
        except TypeError:
            self.datetime = datetime.min

    @property
    def plain_msg(self):
        return f'{self.date} {self.time} {self.user}: {self.msg}'

    def calc_datetime(self):
        string = self.date[:-3] + self.time
        string = string.replace("오후", "PM").replace("오전", "AM")
        dt_format = "%Y년 %m월 %d일 %p %I:%M"
        return datetime.strptime(string, dt_format)

    def __lt__(self, other):
        return self.datetime < other.datetime

    def __le__(self, other):
        return self.datetime <= other.datetime

    def __gt__(self, other):
        return self.datetime > other.datetime

    def __ge__(self, other):
        return self.datetime >= other.datetime

    def __eq__(self, other):
        return self.datetime == other.datetime and self.msg == other.msg and self.user == other.user
