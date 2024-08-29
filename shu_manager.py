from flask import Flask, request, jsonify
from datetime import datetime,timedelta
from util.check_internet import isInternetConnected
from shu_agent import SHUAgent
import time


# Context manager that controls interval events and internet events
class SHUManager(object):
    def __init__(self, agent):
        # function name: interval info
        # interval info: in dict, key with 'every', 'time'
        # 'every' : if don't exist, time will be interval
        #           if exist, 'hour' or 'day'
        # 'time' : dict, 'hour', 'minute', 'second'

        self.agent = agent

        self.intervals = {
            "self.check_internet_and_restart": {
                "time": {"second": 10}
            },
            "self.restart_agent.0": {
                "every": "hour",
                "time": {"minute": 0}
            },
            "self.restart_agent.30": {
                "every": "hour",
                "time": {"minute": 30}
            }
        }
        self.internet_connected = isInternetConnected()

        self.app = Flask(__name__)

        @self.app.route('/command', methods=['POST'])
        def process_data():
            data = request.json
            res = self.agent.cmd("!shu " + data["input"])
            result = {"response": res, "status": 200}
            return jsonify(result)

        self.port = 5000
        self.app.run(port=self.port)

    def append(self, func_name, interval):
        self.intervals[func_name] = interval

    def check_internet_and_restart(self):
        internet_connected = isInternetConnected()

        # print(f"internet: {internet_connected}")

        if self.internet_connected and not internet_connected:
            print("internet lost")

        if not self.internet_connected and internet_connected:
            print("internet reconnected")
            self.agent.restart()

        self.internet_connected = internet_connected

    def restart_agent(self):
        self.agent.restart()

    def __run_interval(self):
        timer = {}

        for func in self.intervals:
            timer[func] = datetime.min

        while True:
            if self.internet_connected:
                for func in self.intervals:
                    last = timer[func]
                    interval = self.intervals[func]
                    if self.__eval(interval, last):
                        timer[func] = datetime.now()
                        try:
                            if "self." in func:
                                getattr(self, func.split('.')[1])()
                            else:
                                getattr(self.agent, func.split('.')[0])()
                        except Exception as e:
                            print(f"error on {func}: {type(e).__name__}, {e}")

            else:
                self.check_internet_and_restart()

            time.sleep(1)

    def __eval(self, interval, last: datetime):
        now = datetime.now()
        if 'every' in interval.keys():
            if interval['every'] == 'day':
                if now.day - last.day <= 0:
                    return False

            elif interval['every'] == 'hour':
                if now.hour - last.hour <= 0:
                    return False

            return self.__eval_time(now, interval['time'])

        else:
            sub = now - last
            hours, minutes, seconds = 0,0,0

            if 'hour' in interval['time']:
                hours = interval['time']['hour']
            if 'minute' in interval['time']:
                minutes = interval['time']['minute']
            if 'second' in interval['time']:
                seconds = interval['time']['second']

            return sub >= timedelta(hours=hours, minutes=minutes, seconds=seconds)

    def __eval_time(self, dt, time):
        if 'hour' in time.keys():
            if dt.hour != time['hour']:
                return False

        if 'minute' in time.keys():
            if dt.minute != time['minute']:
                return False

        if 'second' in time.keys():
            if dt.second != time['second']:
                return False

        return True

    def __enter__(self):
        print("check internet connection...")
        for _ in range(3):
            self.internet_connected = isInternetConnected()
            time.sleep(5)

        if self.internet_connected:
            print("internet connected")
        else:
            print("internet not connected")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__run_interval()


if __name__ == "__main__":
    shu = SHUAgent()
    with SHUManager(shu) as m:
        pass
        # m.append("echo", {"time": {"second": 5}})

