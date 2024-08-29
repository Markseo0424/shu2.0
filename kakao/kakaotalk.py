import pywinauto.findwindows
from pywinauto import findwindows
from pywinauto import application
from util.post_key_win32 import *
from .chatroom import Chatroom


class Kakaotalk:
    def __init__(self, name='카카오톡', path="C:\\Program Files (x86)\\Kakao\\KakaoTalk\\KakaoTalk.exe"):
        self.app = application.Application(backend='uia')

        self.name = name
        self.path = path

        self.handle = None
        self.chatRooms = {}

        self.id = 'seojo0424@naver.com'
        self.pw = 'hello world!!'

        self.open()

    def searchHandle(self, name, n=5, delay=1):
        handle = 0

        for i in range(n):
            handle = win32gui.FindWindow(None, name)

            if handle == 0:
                time.sleep(delay)
            else:
                break

        return handle

    def open(self):
        try:
            self.app.connect(title_re=self.name)
        except pywinauto.findwindows.ElementNotFoundError:
            self.app.start(self.path)

        self.handle = self.searchHandle(self.name)

    def reopen(self):
        self.app.kill()
        self.open()
        time.sleep(10)
        self.manageChatrooms()

    def openChatroom(self, name):
        """
        :param name: name of chatroom to open
        :return: chatroom that is opened
        """
        self.handle = self.searchHandle(self.name)

        main_view = win32gui.FindWindowEx(self.handle, None, "EVA_ChildWindow", None)
        contact_list_view = win32gui.FindWindowEx(main_view, None, "EVA_Window", None)
        chat_room_list_view = win32gui.FindWindowEx(main_view, contact_list_view, "EVA_Window", None)
        edit = win32gui.FindWindowEx(chat_room_list_view, None, "Edit", None)
        win32api.SendMessage(edit, win32con.WM_SETTEXT, 0, name)
        time.sleep(0.5)
        SendReturn(edit)

        if name not in self.chatRooms.keys():
            self.chatRooms[name] = Chatroom(self.searchHandle(name))
        else:
            self.chatRooms[name].handle = self.searchHandle(name)

        return self.chatRooms[name]

    def closeChatroom(self, name):
        """
        :param name: name of chatroom to close
        """

        if name not in self.chatRooms:
            return

        del self.chatRooms[name]

    def manageChatrooms(self):
        dels = []
        for key in self.chatRooms:
            searched = self.searchHandle(key, n=1)
            if searched != self.chatRooms[key].handle:
                if searched != 0:
                    self.chatRooms[key].handle = searched
                else:
                    dels.append(key)

        for key in dels:
            self.openChatroom(key)

    def login(self):
        dlg = self.app[self.name]
        dlg['Edit'].type_keys('^a' + self.id + '{TAB}' + self.pw + '{ENTER}', with_spaces=True, with_tabs=True)



if __name__ == "__main__":
    kakao = Kakaotalk()
    # kakao.login()
    # kakao.openChatroom('서지훈')
    # kakao.chatRooms['서지훈'].read()

    print("done")