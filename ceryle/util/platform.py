import platform


def is_linux():
    return platform.system() == 'Linux'


def is_mac():
    return platform.system() == 'Darwin'


def is_win():
    return platform.system() == 'Windows'
