from time import sleep
from typing import Dict, Callable, List
from subprocess import getstatusoutput
import platform

import numpy as np
import face_recognition
import cv2
import click

HID_IDLE_CMD = "ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print $NF/1000000000; exit}'"
BRIDGESUPPORT_FILE = ".bridgesupport"
IOKIT_FRAMEWORK = "/System/Library/Frameworks/IOKit.framework"
DISPLAY_CONNECT = b"IODisplayConnect"
kIODisplayBrightnessKey = "brightness"

STATUS_SUCCESS = 0
NO_IDLE = 0.0
NO_BRIGHTNESS = 0

DEFAULT_CAPTURE_DEV = 0
FRAMES = 3
IDLE_MIN_SEC = 10


def import_iokit(iokit_location: str = IOKIT_FRAMEWORK, namespace: Dict[str, Callable] = None):
    if namespace is None:
        namespace = globals()

    with open(BRIDGESUPPORT_FILE, 'r') as f:
        bridgesupport_file = f.read()

    objc.parseBridgeSupport(bridgesupport_file,
                            namespace,
                            objc.pathForFramework(iokit_location))


_platform = platform.platform()

if 'Darwin' in _platform:
    from CoreFoundation import CFStringCreateWithCString, CFRelease, kCFStringEncodingASCII
    import objc

    import_iokit()
    _platform = 'Darwin'

elif 'Windows' in _platform:
    import wmi
    _platform = 'Windows'

elif 'Linux' in _platform:
    status, output = getstatusoutput("which xbacklight")

    if status != STATUS_SUCCESS:
        raise Exception("Please install xbacklight.")

    _platform = 'Linux'

else:
    raise Exception('Unknown host platform. This works on macOS, Windows and Linux.')


def get_mac_idle() -> float:
    status, hid_idle_seconds = getstatusoutput(HID_IDLE_CMD)

    if status != STATUS_SUCCESS:
        return NO_IDLE

    return float(hid_idle_seconds)


def get_linux_idle() -> float:
    status, idle = getstatusoutput("xprintidle")

    if status != STATUS_SUCCESS:
        return NO_IDLE

    return float(idle)


IDLE_FUNCS: Dict[str, Callable[[], float]] = {
    'Darwin': get_mac_idle,
    'Linux': get_linux_idle,
    'Windows': lambda x: NO_IDLE
}


def get_idle() -> float:
    return IDLE_FUNCS[_platform]()

# def get_brightness() -> float:
#     IODisplayGetFloatParameter(service, 0, kIODisplayBrightnessKey, brightness)


def set_brightness_mac(brightness: int) -> int:
    brightness /= 100
    service = IOServiceGetMatchingService(kIOMasterPortDefault,
                                          IOServiceMatching(DISPLAY_CONNECT))
    return IODisplaySetFloatParameter(service,
                                      0,
                                      kIODisplayBrightnessKey,
                                      brightness)


def set_brightness_windows(brightness: int):
    return wmi.WMI(namespace='wmi') \
        .WmiMonitorBrightnessMethods()[0] \
        .WmiSetBrightness(brightness, 0)


def set_brightness_linux(brightness: int) -> int:
    status, output = getstatusoutput(f'xbacklight -set {brightness}')
    return status


BRIGHTNESS_FUNCS: Dict[str, Callable[[int], int]] = {
    'Darwin': set_brightness_mac,
    'Linux': set_brightness_linux,
    'Windows': set_brightness_windows
}


def set_brightness(brightness: int) -> int:
    return BRIGHTNESS_FUNCS[_platform](brightness)


def get_snapshots(capture_device: int = DEFAULT_CAPTURE_DEV, frames: int = FRAMES) -> List[np.array]:
    cam = cv2.VideoCapture(capture_device)

    # I've tried this across several Macs: Often, the first frame that is captured
    # by opencv is completely black. Grab a few frames instead.
    frames = [cam.read()[1] for _ in range(frames)]
    cam.release()

    return frames


def contains_face(frame: np.array) -> bool:
    return len(face_recognition.face_locations(frame)) > 0


def detect_and_adjust(capture_device: int,
                      brightness: int = NO_BRIGHTNESS,
                      idle_minimum: float = IDLE_MIN_SEC,
                      frames: int = FRAMES) -> float:
    """
    Detect if the system is idle, if it is, then see if we can
    capture a face from the given capture_device.

    If there's at least one face, don't set the brightness.

    If there's no faces, set the brightness to brightness.

    When done, return the amount of seconds until the next invocation.

    :param capture_device:
    :param brightness:
    :param idle_minimum:
    :param frames:
    :return:
    """
    idle_time = get_idle()

    if not idle_time > idle_minimum:
        return idle_minimum - idle_time

    if not any(map(contains_face, get_snapshots(capture_device, frames))):
        set_brightness(brightness)

    return idle_minimum


@click.command(help="Use system idle information and facial recognition to change screen brightness "
                    "when your computer idle and there isn't anyone in front of the screen.")
@click.option('-d', '--device',
              default=DEFAULT_CAPTURE_DEV, show_default=True,
              help="Capture device.")
@click.option('-b', '--brightness',
              default=NO_BRIGHTNESS, show_default=True,
              type=click.types.IntRange(0, 100),
              help="Screen brightness between 0 and 100.")
@click.option('-i', '--idle',
              default=IDLE_MIN_SEC, show_default=True,
              help="Seconds between inactivtiy and facial recognition.")
@click.option('-f', '--frames',
              default=FRAMES, show_default=True,
              help="Number of frames to capture in succession. \n"
                   "Increase this value if you're getting false negatives")
@click.option('-s', '--step', is_flag=True, help='Enable stepping.')
def run(device: int, brightness: float, idle: float, frames: int, step: bool):
    if frames <= 0:
        print("Error: number of frames cannot be less than 1.")
        exit(1)

    while True:
        sleep_for = detect_and_adjust(device, brightness, idle, frames)
        sleep(sleep_for)


if __name__ == '__main__':
    run()
