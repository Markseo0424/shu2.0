def concat(lst, sep=' ', link_adjust=False):
    s = ''
    for i in lst:
        s += sep
        if link_adjust:
            s += "https://onairsub.notion.site/" + i.split('/')[-1]
        else:
            s += i
    return s[len(sep):]
