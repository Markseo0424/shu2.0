import re, datetime, json
from .notion import Notion
from .notion_objs import NotionObjs as o
from .shu_notion_objs import ShuNotionObjs as so


class ShuNotionTools:
    def __init__(self, token, toolDbId, tool_list):
        self.notion = Notion(token=token)
        self.tool = toolDbId
        self.tool_list = tool_list

    def __createToolPage(self, title, name, start, end, code):
        """
        :param title: title of page
        :param name: user name who rent
        :param start: start time in list [y,m,d,h,mn]
        :param end: end time in list [y,m,d,h,mn]
        :param code: rent code
        :return: page id
        """
        page_dict = {
            'title': title,
            'name': name,
            'start': self.notion.dateString(*start),
            'end': self.notion.dateString(*end),
            'code': code
        }

        page = so.toolPage(page_dict)
        self.notion.create(self.tool, page)

        pageUrl = self.notion.read(self.tool)['results'][0]['url']

        # return only id, not full url
        return re.split('/|-', pageUrl)[-1]

    def reserveTool(self, information: dict, code):
        """
        :param information: reservation information dict, keys with 'name', 'tool_list', 'date_start', 'date_end', 'purpose'
        :param code: reservation code
        :return reserve page ids
        """

        name = information['name']
        tool_list = information['tool_list']
        date_start = information['date_start']
        date_end = information['date_end']
        purpose = information['purpose']

        # list of page id
        reserved_ids = []

        if '녹음실' in tool_list:
            tool_list.remove('녹음실')

            # create page first, add contents next
            page_id = self.__createToolPage('녹음실 대여', name, date_start, date_end, code)

            objs = [
                o.title('대여 목적'),
                o.text(purpose),
                o.text(''),
                o.title('대여 시간'),
                o.check("‘대여 일시’ 속성에 자세히 기입해주시기 바랍니다. (종료일, 시간 포함)", True)
            ]

            self.notion.add_blocks(page_id, objs)

            reserved_ids.append(page_id)

        # if were only '녹음실', end reservation
        if len(tool_list) == 0:
            return reserved_ids

        page_id = self.__createToolPage('장비 내부 대여', name, date_start, date_end, code)
        objs = []
        objs.append(o.title('대여 장비'))

        # check if tool is on reservation
        for tool in self.tool_list:
            objs.append(o.check(tool, tool in tool_list))

        objs.append(o.text(''))
        objs.append(o.title('대여 목적'))
        objs.append(o.text(purpose))
        objs.append(o.text(''))
        objs.append(o.title('대여 시간'))
        objs.append(o.check("‘대여 일시’ 속성에 자세히 기입해주시기 바랍니다. (종료일, 시간 포함)", True))
        self.notion.add_blocks(page_id, objs)

        reserved_ids.append(page_id)

        return reserved_ids

    def removeToolPage(self, code):
        """
        :param code: code of page to remove
        :return: 0 if remove success, 1 if no code exists, 2 if got error
        """

        condition = {
            "filter": {
                "property": "대여 일시",
                "date": {
                    "on_or_after": datetime.datetime.now().strftime("%Y-%m-%d")
                }
            },
            "sorts": [
                {
                    "property": "대여 일시",
                    "direction": "descending"
                }
            ]
        }

        try:
            db = self.notion.read(self.tool, data=json.dumps(condition))
            for page in db["results"]:
                if len(page["properties"]["대여코드"]["rich_text"]) > 0:
                    if page["properties"]["대여코드"]["rich_text"][0]["text"]["content"] == code:
                        self.notion.remove(page["id"])
                        return 0
            return 1

        except:
            return 2

    def __dateOverlap(self, start, end, res_start, res_end, strict=True):
        if strict:
            return not (end < res_start or start > res_end)
        else:
            return not (end <= res_start or start >= res_end)

    def dateConflict(self, dates):
        """
        :param dates: list of dates, [start, end]. each is form of [y,m,d,h,mn]
        :return: tuple of (has passed, links with conflict, list of fatal or not)
        """

        start = datetime.datetime(*dates[0])
        end = datetime.datetime(*dates[1])

        fatal = []
        links = []

        # filter searches by the day reservation ends
        condition = {
            "filter": {
                "property": "대여 일시",
                "date": {
                    "on_or_before": end.strftime("%Y-%m-%d")
                }
            },
            "sorts": [
                {
                    "property": "대여 일시",
                    "direction": "descending"
                }
            ]
        }

        db = self.notion.read(self.tool, data=json.dumps(condition))

        # check if new reservation conflicts with existing reservation
        for res in db['results']:
            # get dates of existing reservation
            res_start = datetime.datetime.strptime(res['properties']['대여 일시']['date']['start'][:16], '%Y-%m-%dT%H:%M')
            res_end = datetime.datetime.strptime(res['properties']['대여 일시']['date']['end'][:16], '%Y-%m-%dT%H:%M')

            # check conflict
            if self.__dateOverlap(start, end, res_start, res_end):
                links.append(res['url'])
                if self.__dateOverlap(start, end, res_start, res_end, strict=False):
                    fatal.append(True)
                else:
                    fatal.append(False)

        return len(links) == 0, links, fatal

    def __isStudio(self, page_id):
        page = self.notion.client.blocks.children.list(page_id)
        return page['results'][0]['heading_2']['rich_text'][0]['text']['content'] == '대여 목적'

    def toolConflict(self, tools, links, fatal_list):
        """
        :param tools: tools to reserve
        :param links: links of conflict dates
        :param fatal_list: fatal list of links
        :return: tuple of (has passed, links with conflict, list of fatal or not)
        """
        conflict_dict = {}

        fatal = False

        # check if 녹음실 reservation conflicts
        if '녹음실' in tools:
            conflict_dict['녹음실'] = []

            for i, url in enumerate(links):
                page_id = url.split('/')[-1]
                if self.__isStudio(page_id):
                    conflict_dict['녹음실'].append(url)
                    fatal = fatal or (fatal_list[i] and True)

            # remove 녹음실 key if doesn't conflict
            if len(conflict_dict['녹음실']) == 0:
                del conflict_dict['녹음실']

            idx = tools.index('녹음실')
            tools.pop(idx)
            fatal_list.pop(idx)

        # check if tools conflicts

        for i, url in enumerate(links):
            page_id = url.split('/')[-1]
            # do something only for tool reservation
            # TODO: make this more efficient
            if self.__isStudio(page_id):
                continue

            page = self.notion.client.blocks.children.list(page_id)
            toolList = [page['results'][i]['to_do']['rich_text'][0]['text']['content'] for i in
                        range(len(page['results'])) if page['results'][i]['type'] == 'to_do' and len(
                    page['results'][i]['to_do']['rich_text'][0]['text']['content']) < 40 and
                        page['results'][i]['to_do']['checked']]

            # check if reserving tool is in conflict day
            day_fatal = False
            for tool in tools:
                if tool in toolList:
                    if tool not in conflict_dict.keys():
                        conflict_dict[tool] = []
                    conflict_dict[tool].append(url)
                    day_fatal = True

            # if tool is in conflicting day and that day is fatal, make fatal true
            fatal = fatal or (fatal_list[i] and day_fatal)

        return len(conflict_dict) == 0, conflict_dict, fatal

    def __updateChecks(self, pageId, take_out, returned):
        self.notion.update(pageId, {
            "properties": {
                "반출": {
                    "checkbox": take_out
                },
                "반납": {
                    "checkbox": returned
                }
            }
        })

    def evalChecks(self):
        condition = {
            "filter": {
                "property": "반납",
                "checkbox": {
                  "equals": False
                }
            }
        }

        db = self.notion.read(self.tool, data=json.dumps(condition))

        # get list of (id, taked_out, returned) only for not returned reservations

        datas = [(d['id'],
                  datetime.datetime.strptime(d['properties']['대여 일시']['date']['start'][:16],
                                             '%Y-%m-%dT%H:%M') < datetime.datetime.now(),
                  datetime.datetime.strptime(d['properties']['대여 일시']['date']['end'][:16],
                                             '%Y-%m-%dT%H:%M') < datetime.datetime.now())
                 for d in db['results'] if not d['properties']['반납']['checkbox']]

        for data in datas:
            self.__updateChecks(*data)

