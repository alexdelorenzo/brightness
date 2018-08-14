import platform
from typing import Optional

STATUS_SUCCESS = 0
STATUS_FAILURE = 1
NO_IDLE = 0.0
NO_BRIGHTNESS = 0

# defaults, user can override
DEFAULT_CAPTURE_DEV = 0
DEFAULT_FRAMES = 2
DEFAULT_IDLE_MIN_SEC = 5 * 60


# mac specific
BRIDGESUPPORT_FILE = ".bridgesupport"
IOKIT_FRAMEWORK = "/System/Library/Frameworks/IOKit.framework"
COREDISPLAY_FRAMEWORK = "/System/Library/Frameworks/CoreDisplay.framework/CoreDisplay"
DISPLAY_CONNECT = b"IODisplayConnect"
kIODisplayBrightnessKey = "brightness"


# idle cmds
LINUX_IDLE_CMD = "xprintidle"
MAC_IDLE_CMD = "ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print $NF/1000000000; exit}'"


_PLATFORM = platform.platform()


class Platform:
    MAC: str = 'Darwin'
    WINDOWS: str = 'Windows'
    LINUX: str = 'Linux'

    @staticmethod
    def this() -> Optional[str]:
        _platform = platform.platform()
        platforms = Platform.MAC, Platform.WINDOWS, Platform.LINUX

        return next((platform for platform in platforms
                     if platform in _platform),
                    _platform)


