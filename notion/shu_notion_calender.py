import json
from datetime import datetime, timedelta
from .notion import Notion
from .shu_notion_objs import ShuNotionObjs as so
from util.date import dateOverlap


class ShuNotionCalendar:
    def __init__(self, token, calDbId):
        self.notion = Notion(token=token)
        self.id = calDbId
        self.calender = None

    def get(self):
        res = []

        condition = {
            "filter": {
                "property": "날짜",
                "date": {
                    "on_or_before": datetime.now().strftime("%Y-%m-%d")
                }
            }
        }

        db = self.notion.read(self.id, data=json.dumps(condition))

        for sch in db['results']:
            try:
                # if len(sch['properties']['참여 국']['multi_select']) == 0:
                #     continue

                res.append(
                    [
                        sch['properties']['날짜']['date']['start'],
                        sch['properties']['날짜']['date']['end'],
                        sch['properties']['이름']['title'][0]['text']['content'],
                        # (so.ANN in sch['properties']['참여 국']['multi_select']) and len(
                        #     sch['properties']['참여 국']['multi_select']) <= 2
                    ]
                )

                if res[-1][1] is None:
                    res[-1][1] = res[-1][0]
            except:
                continue

        self.calender = res
        return res

    def today(self):
        self.get()

        res = []
        for sch in self.calender:
            if dateOverlap(datetime.strptime(sch[0][:10], '%Y-%m-%d'),
                           datetime.strptime(sch[0][:10], '%Y-%m-%d') + timedelta(days=1),
                           datetime.now(),
                           datetime.now()):
                res.append(sch)

        return res
