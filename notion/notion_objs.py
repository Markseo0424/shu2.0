class NotionObjs:
    @staticmethod
    def text(text):
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text":
                            {
                                "content": text,
                            }
                    }
                ]
            }
        }

    @staticmethod
    def title(text):
        return {
            "object": "block",
            "type": "heading_2",
            "heading_2":
                {
                    "rich_text":
                        [
                            {
                                "type": "text",
                                "text":
                                    {
                                        "content": text,
                                    }
                            }
                        ]
                }
        }

    @staticmethod
    def check(name, checked):
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": name
                        }
                    }
                ],
                "checked": checked
            }
        }