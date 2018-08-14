from functools import wraps
from pathlib import Path
from subprocess import getstatusoutput
from time import sleep
from typing import List, Dict, Callable, Any, Tuple, Iterable, NamedTuple

import click
from cv2 import VideoCapture
from numpy import array

from brightness.common import NO_BRIGHTNESS, DEFAULT_CAPTURE_DEV, DEFAULT_FRAMES, DEFAULT_IDLE_MIN_SEC, STATUS_SUCCESS, \
    BRIDGESUPPORT_FILE, IOKIT_FRAMEWORK, DISPLAY_CONNECT, kIODisplayBrightnessKey, STATUS_FAILURE, Platform, \
    COREDISPLAY_FRAMEWORK
from brightness.idle import IDLE_FUNCS


def printer(args=True):
    def wrapper(func):
        @wraps(func)
        def new(*a, **kw):
            ret = func(*a, **kw)
            # if args:
            #     print(func.__name__, *a, kw, 'return', ret)
            # else:
            #     print(func.__name__, 'return', ret)

            return ret

        return new

    return wrapper


def import_iokit(iokit_location: str = IOKIT_FRAMEWORK,
                 namespace: Dict[str, Any] = None):
    if namespace is None:
        namespace = globals()

    bridgesupport_file: Path = \
        next(Path(__file__).parent.glob(BRIDGESUPPORT_FILE))

    objc.parseBridgeSupport(bridgesupport_file.read_text(),
                            namespace,
                            objc.pathForFramework(iokit_location))


# def set_brightness_mac(brightness): pass


if Platform.this() == Platform.MAC:
    from platform import mac_ver
    version, *_ = mac_ver()

    if '10.13.' in version:
        from ctypes import CDLL, c_int, c_double

        CoreDisplay = CDLL(COREDISPLAY_FRAMEWORK)
        CoreDisplay.CoreDisplay_Display_SetUserBrightness.argtypes = [c_int, c_double]
        CoreDisplay.CoreDisplay_Display_GetUserBrightness.argtypes = [c_int]
        CoreDisplay.CoreDisplay_Display_GetUserBrightness.restype = c_double


        def set_brightness_coredisplay(display: int, brightness: int) -> int:
            brightness /= 100

            return CoreDisplay.CoreDisplay_Display_SetUserBrightness(display, brightness)


        def get_brightness_coredisplay(display: int) -> float:
            brightness: float = CoreDisplay.CoreDisplay_Display_GetUserBrightness(display)

            return round(brightness * 100, 2)


        def set_brightness_mac(brightness: int):
            return set_brightness_coredisplay(0, brightness)

    else:
        import objc

        import_iokit()

        objc.ObjCLazyModule


        def set_brightness_iokit(brightness: int) -> int:
            brightness /= 100
            service = IOServiceGetMatchingService(kIOMasterPortDefault,
                                                  IOServiceMatching(DISPLAY_CONNECT))
            return IODisplaySetFloatParameter(service,
                                              0,
                                              kIODisplayBrightnessKey,
                                              brightness)


        set_brightness_mac = set_brightness_iokit


elif Platform.this() == Platform.WINDOWS:
    import wmi


elif Platform.this() == Platform.LINUX:
    status, output = getstatusoutput("which xbacklight")

    if status != STATUS_SUCCESS:
        raise Exception("Please install xbacklight.")


else:
    raise Exception('Unknown host platform. Project works on macOS, Windows and Linux.')


def get_idle() -> float:
    return IDLE_FUNCS[Platform.this()]()


def set_brightness_windows(brightness: int):
    return wmi.WMI(namespace='wmi') \
        .WmiMonitorBrightnessMethods()[0] \
        .WmiSetBrightness(brightness, 0)


def set_brightness_linux(brightness: int) -> int:
    status, output = getstatusoutput(f'xbacklight -set {brightness}')
    return status


BRIGHTNESS_FUNCS: Dict[str, Callable[[int], int]] = {
    Platform.MAC: set_brightness_mac,
    Platform.LINUX: set_brightness_linux,
    Platform.WINDOWS: set_brightness_windows
}


def set_brightness(brightness: int) -> int:
    return BRIGHTNESS_FUNCS[Platform.this()](brightness)


def get_snapshots(capture_device: int = DEFAULT_CAPTURE_DEV, frames: int = DEFAULT_FRAMES) -> List[array]:
    camera = VideoCapture(capture_device)

    # I've tried this across several Macs: Often, the first frame that is captured
    # by opencv is completely black. Grab a few frames instead.
    frames = [camera.read()[1] for _ in range(frames)]
    camera.release()

    return frames


# face_recognition takes 6 seconds to load on my computer
FACE_FUNC = 'face_locations'


def contains_face(frame: array) -> bool:
    if FACE_FUNC not in globals():
        from face_recognition import face_locations
        globals()[FACE_FUNC] = face_locations

    return len(globals()[FACE_FUNC](frame)) > 0


def frames_contain_face(capture_device: int, frames: int) -> bool:
    frames_contain_face: Iterable[bool] = \
        map(contains_face, get_snapshots(capture_device, frames))

    return any(frames_contain_face)


def on_face_adjust_brightness(capture_device: int,
                              brightness: int = NO_BRIGHTNESS,
                              frames: int = DEFAULT_FRAMES,
                              idle_minimum: float = DEFAULT_IDLE_MIN_SEC,
                              tries: int = 4,
                              _tries: int = 0) -> bool:
    """
    If face is detected in `frames` frames captured in succession from capture_device,
    set brightness to parameter value.

    Return True if brightness is changed, false if not.
    :param capture_device:
    :param brightness:
    :param frames:
    :param tries:
    :param _tries:

    :return:
    """
    if tries < 1:
        tries = 1

    if should_change_brightness(capture_device, brightness) and not frames_contain_face(capture_device, frames):
        # some time could have passed between checking for faces and awaking from idle
        if not get_idletime(idle_minimum).is_idle:
            return False

        if _tries < tries:
            return on_face_adjust_brightness(capture_device, brightness, frames, idle_minimum, tries, _tries + 1)

        set_brightness(brightness)
        return True

    return False


class IdleTime(NamedTuple):
    is_idle: bool
    idle_time: float


class ChangedTime(NamedTuple):
    is_changed: bool
    sleep_for: float


def get_idletime(idle_minimum: float = DEFAULT_IDLE_MIN_SEC) -> IdleTime:
    idle_time = get_idle()

    if idle_time > idle_minimum:
        return IdleTime(True, idle_minimum)

    return IdleTime(False, idle_minimum - idle_time)

def should_change_brightness(device: int, brightness: int) -> bool:
    return get_brightness_coredisplay(device) != brightness

def on_idle_adjust_brightness(capture_device: int,
                              brightness: int = NO_BRIGHTNESS,
                              idle_minimum: float = DEFAULT_IDLE_MIN_SEC,
                              frames: int = DEFAULT_FRAMES) -> ChangedTime:
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

    if not should_change_brightness(capture_device, brightness):
        return ChangedTime(False, idle_minimum)

    idle = get_idletime(idle_minimum)

    if not idle.is_idle:
        return ChangedTime(False, idle.idle_time)

    brightness_changed = on_face_adjust_brightness(capture_device, brightness, frames, idle_minimum)

    return ChangedTime(brightness_changed, idle_minimum)


@click.command(help="""
brightness is a daemon and command-line utility that adjusts your display's brightness.

In daemonized mode, brightness will use facial recognition to determine whether or not to change your display's brightness when your system goes idle.

As a command-line utility, you can use brightness to get and set your display's brightness."""
                    "\n\n\n"
                    "Run without arguments to get the current brightness for the default display."
                    "\n\n"
                    "$ brightness\n"
                    "\n75.0")
@click.option('-c', '--capture',
              default=DEFAULT_CAPTURE_DEV, show_default=True,
              type=click.types.INT,
              help="Capture device.")
@click.option('-b', '--brightness',
              default=NO_BRIGHTNESS, show_default=True,
              type=click.types.IntRange(0, 100),
              help="Screen brightness between 0 and 100.")
@click.option('-d', '--daemon',
              is_flag=True,
              show_default=True,
              type=click.types.BOOL,
              help="Run in daemonized mode. "
                   "Use facial recognition when system goes idle to determine whether to change brightness.")
@click.option('-i', '--idle',
              default=DEFAULT_IDLE_MIN_SEC, show_default=True,
              type=click.types.FLOAT,
              help="Seconds between inactivtiy and facial recognition.")
@click.option('-f', '--frames',
              default=DEFAULT_FRAMES, show_default=True,
              type=click.types.INT,
              help="Number of frames to capture in succession. \n"
                   "Increase this value if you're getting false negatives")
# @click.option('-s', '--step', is_flag=True, help='Enable stepping.')
def run(capture: int, brightness: int, daemon: bool, idle: float, frames: int):
    if frames <= 0:
        print("Error: number of frames cannot be less than 1.")
        exit(STATUS_FAILURE)

    # if step:
    #     print("Step flag detected, but is unimplemented.")

    if brightness and not daemon:
        set_brightness(brightness)
        exit(STATUS_SUCCESS)

    if daemon:
        print(f'Running in daemon mode. Capture {capture} Brightness {brightness} Idle {idle} Frames {frames}')

        try:
            while True:
                changed, sleep_for = on_idle_adjust_brightness(capture, brightness, idle, frames)
                sleep(sleep_for)
        except KeyboardInterrupt:
            print("Exiting...")
            exit(STATUS_FAILURE)

    if Platform.this() == Platform.MAC:
        print(get_brightness_coredisplay(0))
        exit(STATUS_SUCCESS)

    else:
        print(f"Feature not yet implemented for {Platform.this()}")
        exit(STATUS_FAILURE)


if __name__ == '__main__':
    run()
