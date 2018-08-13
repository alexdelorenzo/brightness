from subprocess import getstatusoutput
from typing import Dict, Callable

from common import MAC_IDLE_CMD, STATUS_SUCCESS, NO_IDLE, LINUX_IDLE_CMD


def get_linux_idle() -> float:
    status, idle = getstatusoutput(LINUX_IDLE_CMD)

    if status != STATUS_SUCCESS:
        return NO_IDLE

    return float(idle)


def get_mac_idle() -> float:
    status, hid_idle_seconds = getstatusoutput(MAC_IDLE_CMD)

    if status != STATUS_SUCCESS:
        return NO_IDLE

    return float(hid_idle_seconds)


IDLE_FUNCS: Dict[str, Callable[[], float]] = {
    'Darwin': get_mac_idle,
    'Linux': get_linux_idle,
    'Windows': lambda x: NO_IDLE
}
