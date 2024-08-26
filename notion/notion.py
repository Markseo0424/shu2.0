import requests, json
from notion_client import Client


class Notion:
    def __init__(self, token):
        self.client = Client(auth=token)
        self.headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Notion-Version": "2022-02-22"
        }

    def read(self, dbId, data=None, save_path=None):
        readUrl = f"https://api.notion.com/v1/databases/{dbId}/query"

        # if data exists, post with data
        if data is not None:
            res = requests.post(readUrl, headers=self.headers, data=data)
        else:
            res = requests.post(readUrl, headers=self.headers)
        # print(res.status_code)

        # jsonify read data and save
        data = res.json()

        if save_path is not None:
            with open(save_path, "w", encoding="utf8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        return data

    def create(self, dbId, data: dict):
        url = "https://api.notion.com/v1/pages"

        # set parent database
        data["parent"] = {"database_id": dbId}

        json_data = json.dumps(data)

        res = requests.post(url, headers=self.headers, data=json_data)
        # print(res.status_code)

    def update(self, dbId, data: dict):
        url = f"https://api.notion.com/v1/pages/{dbId}"

        json_data = json.dumps(data)

        res = requests.request("PATCH", url, headers=self.headers, data=json_data)
        # print(res.status_code)

    def remove(self, dbId):
        self.update(dbId, {'archived': True})

    def add_block(self, page_id, obj):
        """
        :param page_id: page id
        :param obj: obj to add
        :return: id of added block
        """
        self.client.blocks.children.append(
            block_id=page_id,
            children=[
                obj
            ]
        )
        return self.client.blocks.children.list(page_id)['results'][-1]['id']

    def add_blocks(self, page_id, objs):
        """
        :param page_id: page id
        :param objs: objs to add (list)
        :return: list of id of added blocks
        """
        self.client.blocks.children.append(
            block_id=page_id,
            children=objs
        )
        return [block['id'] for block in self.client.blocks.children.list(page_id)['results'][-len(objs):]]

    @staticmethod
    def dateString(y, m, d, h, mn):
        return "{Y:04d}-{M:02d}-{D:02d}T{H:02d}:{Mn:02d}:00.000+09:00".format(Y=y, M=m, D=d, H=h, Mn=mn)

