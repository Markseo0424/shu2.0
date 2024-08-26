def split_to_num(s):
    num = ''
    for c in s[::-1]:
        if c.isnumeric():
            num = c + num

        elif num:
            break

    name = s.replace(num, '').strip()

    if not num:
        num = '0'

    return name, int(num)


def sort_tool_list(lst):
    split = [split_to_num(s) for s in lst]
    split.sort()
    res = [name + (' ' + str(num) if num else '') for name, num in split]

    return res
