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


