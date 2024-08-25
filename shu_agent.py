import json
from kakao.kakaotalk import Kakaotalk
from notion.shu_notion_tools import ShuNotionTools


class SHUAgent:
    def __init__(self, keys_path='./data/keys.json', constants_path='./data/constants.json'):
        self.name = '슈비서'

        with open(keys_path, 'r') as f:
            self.keys = json.load(f)
        with open(constants_path, 'r') as f:
            self.constants = json.load(f)

        assert 'token' in self.keys, "token doesn't exists!"

        self.kakao = Kakaotalk()
        self.tools = ShuNotionTools(
            self.keys['token'],
            self.keys['databaseId'],
            self.constants['tools']
        )

        # open chat rooms
        self.chatRooms = {}
        self.kakao.open()
        self.chatRooms['tool_chatroom'] = self.kakao.openChatroom(self.constants['tool_chatroom'])
        self.chatRooms['notice_chatroom'] = self.kakao.openChatroom(self.constants['notice_chatroom'])

    def handleReservation(self, msg):
        pass

    def handleCancel(self, msg):
        pass

    def handleCommand(self, msg):
        pass

    def toolCheckUpdateNotion(self):
        # ensure all rooms are open
        self.kakao.manageChatrooms()

        room = self.chatRooms['tool_chatroom']
        new_msg = room.read()

        # get message lists to check (after last 슈비서's talk)
        msg_to_check = []

        for msg in room.msg[::-1]:
            if msg.user == self.name:
                break
            msg_to_check.append(msg)

        msg_to_check.reverse()

        for msg in msg_to_check:
            if '[예약]' in msg.msg[:20]:
                self.handleReservation(msg)
            elif '[취소]' in msg.msg[:20]:
                self.handleCancel(msg)
            elif msg.msg[0] == '!':
                self.handleCommand(msg)
