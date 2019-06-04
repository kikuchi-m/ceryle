
def getin(d, *keys, default=None):
    if not keys:
        return d

    k = keys[0]
    if not isinstance(d, dict) or k not in d:
        return default
    return getin(d[k], *keys[1:], default=default)
