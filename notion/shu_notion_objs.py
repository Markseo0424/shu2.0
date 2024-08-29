class ShuNotionObjs:
    @staticmethod
    def toolPage(page_dict: dict) -> dict:
        """
        :param page_dict: dict with keys 'title', 'name', 'start', 'end', 'code'
        :return: dict obj of new tool page
        """
        pageObj = {
            "properties":
                {
                    "대여자":
                        {
                            "id": "UFzD", "type": "rich_text", "rich_text":
                            [
                                {
                                    "type": "text", "text":
                                    {
                                        "content": page_dict['name']
                                    },
                                    "annotations":
                                        {
                                            "bold": False, "italic": False, "strikethrough": False, "underline": False,
                                            "code": False, "color": "default"
                                        },
                                    "plain_text": page_dict['name']
                                }
                            ]
                        },

                    "대여 일시": {
                        "id": "%5CdTW",
                        "type": "date",
                        "date":
                            {
                                "start": page_dict['start'],
                                "end": page_dict['end'],
                            }
                    },

                    "반출":
                        {
                            "id": "o%7CGv",
                            "type": "checkbox",
                            "checkbox": False
                        },

                    "반납":
                        {
                            "id": "%7B%7DmP",
                            "type": "checkbox",
                            "checkbox": False
                        },

                    "이름":
                        {
                            "id": "title",
                            "type": "title",
                            "title":
                                [
                                    {
                                        "type": "text",
                                        "text":
                                            {
                                                "content": page_dict['title']
                                            }
                                    }
                                ]
                        },

                    "대여코드":
                        {
                            'id': '%3CTcM',
                            'type': 'rich_text',
                            'rich_text': [
                                {
                                    'type': 'text',
                                    'text':
                                        {
                                            'content': page_dict['code']
                                        },
                                }
                            ]
                        }
                }
        }

        return pageObj

    ANN = {
        "id": "ae9e5e48-e39c-4f0a-8aac-3e30b0108ae9",
        "name": "아나국",
        "color": "yellow"
    }

    archive_multiselect = {
        "ANN": {
            "id": "628cc2ed-eb7c-4ef3-a94c-ea3dbc870ea1",
            "name": "아나국",
            "color": "purple"
        },
        "VID": {
            "id": "7dc86315-25fa-4947-997d-1d93fc7032ca",
            "name": "영상국",
            "color": "blue"
        },
        "REP": {
            "id": "892b735a-1b6a-4954-96c0-19c6d2b4ad21",
            "name": "보도국",
            "color": "orange"
        },
        "TEC": {
            "id": "716a3ced-d615-4721-ba43-a59d1b40d532",
            "name": "기술국",
            "color": "green"
        }
    }
