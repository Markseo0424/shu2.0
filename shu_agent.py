import json, datetime
from kakao.kakaotalk import Kakaotalk
from youtube.youtube import Youtube
from notion import ShuNotionTools, ShuNotionCalendar, ShuNotionArchive
from gpt.brain import GptBrain
from cmd.kernel import CmdKernel
from util.sort import sort_tool_list
from util.concat import concat


class SHUAgent:
    def __init__(self, keys_path='./data/keys.json', constants_path='./data/constants.json',
                 prompt_path='./data/prompt.txt'):
        self.name = '슈비서'
        self.constants_path = constants_path

        with open(keys_path, 'r', encoding='UTF8') as f:
            self.keys = json.load(f)
        with open(constants_path, 'r', encoding='UTF8') as f:
            self.constants = json.load(f)
        with open(prompt_path, 'r', encoding="UTF-8") as f:
            self.prompt = f.read()

        assert 'token' in self.keys, "token doesn't exists!"

        self.cmd = CmdKernel(callback=self.reload)
        self.kakao = Kakaotalk()
        self.youtube = Youtube(
            dev_key=self.keys["youtubeDevKey"],
            channelId=self.keys["youtubeChannelId"]
        )
        self.gpt = GptBrain(
            token=self.keys['openaiKey'],
            assistant=self.keys['assistantId']
        )
        self.tools = ShuNotionTools(
            self.keys['token'],
            self.keys['databaseId'],
            self.constants['tools']
        )
        self.cal = ShuNotionCalendar(
            self.keys['token'],
            self.keys['calendarId']
        )
        self.arc = ShuNotionArchive(
            self.keys['token'],
            self.keys['archiveId']
        )

        # open chat rooms
        self.chatRooms = {}
        self.kakao.open()
        self.chatRooms['tool_chatroom'] = self.kakao.openChatroom(self.constants['tool_chatroom'])
        self.chatRooms['notice_chatroom'] = self.kakao.openChatroom(self.constants['notice_chatroom'])

    def reload(self):
        with open(self.constants_path, 'r', encoding='UTF8') as f:
            self.constants = json.load(f)
        self.chatRooms['tool_chatroom'] = self.kakao.openChatroom(self.constants['tool_chatroom'])
        self.chatRooms['notice_chatroom'] = self.kakao.openChatroom(self.constants['notice_chatroom'])
        self.kakao.manageChatrooms()

    def restart(self):
        print("restart agent")
        self.kakao.reopen()
        self.reload()

    def reserveTool(self, information):
        tools = information["tool_list"]
        dates = (information["date_start"], information["date_end"])

        # check if date conflicts
        date_passed, links, fatal_list = self.tools.dateConflict(dates)

        # if date conflicts, check if tools also conflicts.
        if not date_passed:
            tool_passed, conflicts, fatal = self.tools.toolConflict(tools, links, fatal_list)
        else:
            tool_passed = True
            conflicts = {}
            fatal = False

        # generate code by current time
        code = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

        # if passed condition, reserve tool
        if tool_passed or not fatal:
            self.tools.reserveTool(information, code)

        # write message to kakaotalk
        if tool_passed:
            self.chatRooms['tool_chatroom'].send('<장비 대여가 완료되었습니다!>\n대여 코드 : ' + code)
            print("    장비 대여 완료")
        elif fatal:
            text = '<장비 대여가 불가능합니다!> \n대여 시간이 겹칩니다. 확인 부탁드립니다!\n'
            for tool in conflicts:
                text += tool + ' : \n' + concat(conflicts[tool], sep='\n', link_adjust=True) + '\n'
            self.chatRooms['tool_chatroom'].send(text)
            print("    장비 대여 불가")
        else:
            text = '<장비 대여가 완료되었습니다!>\n대여 코드 : ' + code + '\n주의! 대여 시간이 겹칩니다. 확인 부탁드립니다!\n'
            for tool in conflicts:
                text += tool + ' : \n' + concat(conflicts[tool], sep='\n', link_adjust=True) + '\n'
            self.chatRooms['tool_chatroom'].send(text)
            print("    장비 대여 완료, 주의")

    def handleReservation(self, msg):
        print("res: ", msg.plain_msg)

        text = msg.plain_msg

        prompt = self.prompt.replace("$TOOL_LIST$", concat(self.constants['tools'], ', '))
        res = self.gpt(text, prompt)
        err = ''

        print("    assistant: \n       ", res.replace('\n', '\n        '))

        # if there is error, save it and trim message
        if 'err' in res:
            split = res.split('\n')
            res = split[0]
            err = split[1].split("err:")[1].strip()

        # make instruction list, [tools, date, purpose]
        instruction = [s.strip() for s in res.split('/')]
        instruction[0] = sort_tool_list(instruction[0].split(','))
        instruction[1] = [[int(n) for n in s.strip().split(".")] for s in instruction[1].replace(":",".").split('~')]
        print("   ", instruction)
        print("   ", err)

        information = {
            "name": msg.user,
            "tool_list": instruction[0],
            "date_start": instruction[1][0],
            "date_end": instruction[1][1],
            "purpose": instruction[2]
        }

        self.reserveTool(information=information)

    def handleCancel(self, msg):
        print("can: ", msg.plain_msg)
        code = msg.msg.split()[-1].strip()

        status = self.tools.removeToolPage(code)
        if status == 0:
            self.chatRooms["tool_chatroom"].send("<예약 취소가 완료되었습니다!>")
            print("    취소 완료")
        elif status == 1:
            self.chatRooms["tool_chatroom"].send("<해당 코드를 발견하지 못했거나 과거 대여 기록입니다.>")
            print("    취소 실패: 해당 코드가 존재하지 않습니다.")
        elif status == 2:
            self.chatRooms["tool_chatroom"].send("<에러가 발생했습니다.>")
            print("    취소 실패: 에러 발생")

    def handleCommand(self, msg):
        print("com: ", msg.plain_msg)
        response = self.cmd(msg.msg)
        self.chatRooms["tool_chatroom"].send(response)
        print("   ", response)

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

        # classify messages and send it to handler function
        for msg in msg_to_check:
            if '[예약]' in msg.msg[:20]:
                self.handleReservation(msg)
            elif '[취소]' in msg.msg[:20]:
                self.handleCancel(msg)
            elif msg.msg[0] == '!':
                self.handleCommand(msg)

    def toolCheckEvaluation(self):
        self.tools.evalChecks()
        print("sys:  evaluating rent and return")

    def calenderCheckNotion(self):
        res = self.cal.today()

        if not len(res):
            return

        text = '<오늘의 SUB 일정>\n'

        # isANN = False

        for sch in res:
            text += '\n' + sch[2]
            # if (sch[3]): isANN = True

        # if (isANN):
        #     text += '\n\n담당자 분들은 시간에 맞춰 송출 및 모니터링 해주시기 바랍니다❤'
        # else:
        text += '\n\n많은 관심 부탁드립니다❤'

        self.chatRooms['notice_chatroom'].send(text)

    def youtubeCheckUpdateNotion(self):
        new_videos = self.youtube.get_new_videos()
        if new_videos:
            print("new videos found:")
            for video in new_videos:
                print(f"    {video['title']}")

        for video in new_videos:
            self.arc.post(**video)


if __name__ == "__main__":
    shu = SHUAgent()
    # shu.tools.evalChecks()
    # shu.toolCheckUpdateNotion()
    print("done")