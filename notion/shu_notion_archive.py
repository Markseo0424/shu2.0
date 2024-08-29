import json, re
from datetime import datetime, timedelta
from .notion import Notion
from .shu_notion_objs import ShuNotionObjs as so


class ShuNotionArchive:
    def __init__(self, token, arcDbId):
        self.notion = Notion(token=token)
        self.id = arcDbId

        self.team_prefix = {
            "ANN": ["ANN"],
            "VID": ["VID"],
            "REP": ["REP", "NEWS"],
            "TEC": ["TEC", "ENG"]
        }

    def post(self, video_id, title, description, thumbnail, date, playlist):
        teams = []
        for name in self.team_prefix:
            for prefix in self.team_prefix[name]:
                if prefix in playlist and name not in teams:
                    teams.append(name)

        self.notion.create(self.id, {
            "cover": {
                "type": "external",
                "external": {
                    "url": thumbnail
                }
            },
            "parent": {
                "database_id": self.id
            },
            "properties": {
                "참여 국": {
                    "id": "%5DGTZ",
                    "type": "multi_select",
                    "multi_select": [so.archive_multiselect[i] for i in teams]
                },
                "송출 날짜": {
                    "id": "cmQ%7D",
                    "type": "date",
                    "date": {
                        "start": date,
                        "end": None
                    }
                },
                "이름": {
                    "id": "title",
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }}})
        data = self.notion.read(self.id)
        page_id = re.split('/|-', data['results'][0]['url'])[-1]
        self.notion.add_blocks(page_id, [
            {
                "object": "block",
                "type": "video",
                "video": {
                    "caption": [

                    ],
                    "type": "external",
                    "external": {
                        "url": "https://www.youtube.com/watch?v=" + video_id
                    }
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "방송 설명"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": description
                            }
                        }
                    ]
                }
            }
        ])
