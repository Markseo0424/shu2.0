import json
from util.sort import sort_tool_list


class CmdKernel:
    def __init__(self, data_path='./data', callback=None):
        self.data_path = data_path
        self.callback = callback

    def __call__(self, cmd):
        """
        :param cmd: full command with !shu ~~
        :return: string output
        """

        split = cmd.split()

        if len(split) < 2:
            return "<명령이 온전하지 않습니다!>"

        type = split[1]
        args = split[2:]

        try:
            res = self.__getattribute__(type)(*args)
        except AttributeError:
            return "<해당 명령이 존재하지 않습니다!>"

        if self.callback is not None:
            self.callback()

        return res.strip()

    def __read_file(self, name="constants.json"):
        with open(self.data_path + "/" + name, encoding="UTF-8") as f:
            json_data = json.load(f)

        return json_data

    def __save_file(self, file, name="constants.json"):
        # specified sort
        file['tools'] = sort_tool_list(file['tools'])

        with open(self.data_path + "/" + name, "w", encoding="UTF-8") as f:
            json.dump(file, f, indent=4, ensure_ascii=False)

    def help(self, *args):
        des = {
            "print": '''원하는 상수를 출력합니다.
            사용법: !shu print [상수 이름 혹은 all]
            all을 입력 시 모든 상수를 출력합니다.
            ''',
            "edit": '''원하는 상수를 변경합니다.
            사용법: !shu edit [상수 이름] [변경할 상수 값]
            edit은 문자열 변수만 변경할 수 있습니다.
            ''',
            "append": '''리스트형 상수에 값을 추가합니다.
            사용법: !shu append [상수 이름] ([추가할 상수 키]) [추가할 상수 값]
            dict형 상수인 경우 키를 같이 입력해 주어야 합니다. 
            이 때 키는 한 단어로 입력해야 합니다.
            ''',
            "delete": '''리스트형 상수에서 값을 제거합니다.
            사용법: !shu delete [상수 이름] [삭제할 상수 값 또는 키]
            dict형 상수인 경우 삭제할 키를 입력해 주어야 합니다.
            '''
        }

        text = ""

        if len(args) == 0:
            args = list(des.keys())

        for command in des:
            if command in args:
                text += command + ": " + des[command] + "\n"

        return text


    def print(self, *args):
        if not args:
            return "<명령이 온전하지 않습니다!>\n사용법: !shu print [상수 이름 혹은 all]"

        file = self.__read_file()

        if "all" in args:
            text = "<현재 상수 값들입니다!>\n"
            for key in file:
                text += key + ": " + str(file[key]) + "\n"

        else:
            text = "<요청하신 값입니다!>\n"
            for key in args:
                if key in file.keys():
                    text += key + ": " + str(file[key]) + "\n"
                else:
                    text += f"KeyError: {key}은(는) 존재하지 않습니다!\n"

        return text

    def edit(self, *args):
        if len(args) < 2:
            return "<명령이 온전하지 않습니다!>\n사용법: !shu edit [상수 이름] [변경할 상수 값]"

        file = self.__read_file()

        key, value = args[0], " ".join(args[1:])

        if key not in file.keys():
            return f"<에러가 발생했습니다!>\nKeyError: {key}은(는) 존재하지 않습니다!"

        if type(file[key]) == list or type(file[key]) == dict:
            return f"<에러가 발생했습니다!>\nTypeError: {key}은(는) {type(file[key]).__name__}타입 입니다."

        file[key] = value

        self.__save_file(file)
        return f"<{key}을(를) {value}로 변경하였습니다!>"

    def append(self, *args):
        if len(args) < 2:
            return "<명령이 온전하지 않습니다!>\n사용법: !shu append [상수 이름] ([추가할 상수 키]) [추가할 상수 값]"

        file = self.__read_file()

        key = args[0]

        if key not in file.keys():
            return f"<에러가 발생했습니다!>\nKeyError: {key}은(는) 존재하지 않습니다!"

        if type(file[key]) == list:
            if len(args) < 2:
                return "<에러가 발생했습니다!>\n상수 타입이 list인 경우 파라미터는 2개 필요합니다."

            value = " ".join(args[1:])

            if value in file[key]:
                return f"<에러가 발생했습니다!>\n{value}이(가) 이미 {key}에 존재합니다!"

            file[key].append(value)
            self.__save_file(file)
            return f"<{key}에 {value}을(를) 성공적으로 추가하였습니다!>"

        elif type(file[key]) == dict:
            if len(args) < 3:
                return "<에러가 발생했습니다!>\n상수 타입이 dict인 경우 파라미터는 3개 필요합니다."

            value = " ".join(args[2:])

            file[key][args[1]] = value
            self.__save_file(file)
            return f"<{key}에 {args[1]}: {value}을(를) 성공적으로 추가하였습니다!>"

        else:
            return f"<에러가 발생했습니다!>\nTypeError: {key}은(는) {type(file[key]).__name__}타입 입니다. append가 허용되는 타입은 list, dict입니다."

    def delete(self, *args):
        if len(args) < 2:
            return "<명령이 온전하지 않습니다!>\n사용법: !shu delete [상수 이름] [삭제할 상수 값 또는 키]"

        file = self.__read_file()

        key, value = args[0], " ".join(args[1:])

        if key not in file.keys():
            return f"<에러가 발생했습니다!>\nKeyError: {key}은(는) 존재하지 않습니다!"

        if type(file[key]) == list:
            if value not in file[key]:
                return f"<에러가 발생했습니다!>\nValueError: {key}에 {value}이(가) 존재하지 않습니다!"
            file[key].remove(value)
            self.__save_file(file)
            return f"<{key}에서 {value}을(를) 성공적으로 제거하였습니다!>"

        elif type(file[key]) == dict:
            if value not in file[key].keys():
                return f"<에러가 발생했습니다!>\nKeyError: {key}에 {value}이(가) 존재하지 않습니다!"
            del file[key][value]
            self.__save_file(file)
            return f"<{key}에서 {value}을(를) 성공적으로 제거하였습니다!>"

        else:
            return f"<에러가 발생했습니다!>\nTypeError: {key}은(는) {type(file[key]).__name__}타입 입니다. delete가 허용되는 타입은 list, dict입니다."

