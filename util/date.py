def dateOverlap(start, end, res_start, res_end, strict=True):
    if strict:
        return not (end < res_start or start > res_end)
    else:
        return not (end <= res_start or start >= res_end)
