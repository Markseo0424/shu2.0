from util.post_key_win32 import *
from pywinauto import clipboard
from .message import Message


class Chatroom:
    def __init__(self, handle):
        self.handle = handle
        self.__handle = handle
        self.edit = None
        self.bg = None
        self.last_msg = None
        self.msg = []

    def ensureHandles(self):
        if self.__handle != self.handle or self.edit is None or self.bg is None:
            self.__handle = self.handle
            self.edit = win32gui.FindWindowEx(self.handle, None, "RICHEDIT50W", None)
            self.bg = win32gui.FindWindowEx(self.handle, None, "EVA_VH_ListControl_Dblclk", None)

    def read(self):
        self.ensureHandles()
        PostKeyEx(self.bg, ord('A'), [w.VK_CONTROL], False)
        time.sleep(0.5)
        PostKeyEx(self.bg, ord('C'), [w.VK_CONTROL], False)
        try:
            txt = clipboard.GetData()
        except:
            print('chatroom.read.ClipboardAccessError')
            return []

        new_msgs = self.parseMessages(txt)
        return new_msgs

    def send(self, text):
        self.ensureHandles()
        SendMessage(self.edit, win32con.WM_SETTEXT, 0, text)
        SendReturn(self.edit)

    def parseMessages(self, txt):
        date = None
        time = None
        user = None
        msg = None

        new_msgs = []

        chats = txt.split('\r\n')
        for line in chats:
            if len(line) == 0:
                continue
            if line[0] == '[':
                open = 0
                idx = 0
                for i, c in enumerate(line):
                    if c == ']':
                        if idx == 0:
                            user = line[open + 1: i]
                            idx += 1
                        elif idx == 1:
                            time = line[open + 1: i]
                            msg = line[i + 2:]
                            break

                    elif c == '[':
                        open = i

                new_msg = Message(date,time,user,msg)
                if self.last_msg is None or new_msg >= self.last_msg and new_msg not in self.msg:
                    self.msg.append(new_msg)
                    new_msgs.append(new_msg)
                self.last_msg = new_msg

            elif '년' in line and \
                    '월' in line and \
                    '일' in line and \
                    '요일' in line and len(line) < 20:
                date = line

        return new_msgs