STATUS_SUCCESS = 0
NO_IDLE = 0.0
NO_BRIGHTNESS = 0

# defaults, user can override
DEFAULT_CAPTURE_DEV = 0
DEFAULT_FRAMES = 2
DEFAULT_IDLE_MIN_SEC = 5 * 60


# mac specific
BRIDGESUPPORT_FILE = ".bridgesupport"
IOKIT_FRAMEWORK = "/System/Library/Frameworks/IOKit.framework"
DISPLAY_CONNECT = b"IODisplayConnect"
kIODisplayBrightnessKey = "brightness"


# idle cmds
LINUX_IDLE_CMD = "xprintidle"
MAC_IDLE_CMD = "ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print $NF/1000000000; exit}'"
