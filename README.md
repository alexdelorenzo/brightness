# ☀ brightness: Adjust display brightness with your 🌞

`brightness` is a command-line utility and daemon that adjusts your display's brightness.

In daemonized mode, `brightness` will use facial recognition to determine whether or not to change your display's brightness when your system goes idle.

As a command-line utility, you can use `brightness` to get and set your display's brightness.

## Use Cases

You intend to leave your screen on, even while there's little to no mouse or keyboard activity.  This can happen while watching a video, reading text or following a recipe. 

You probably don't like it when your screen goes off when you're looking at it. There's probably a camera on your screen and it's probably in front of your face.

Let's use it to make computers a little less annoying.

### You want to adjust display brightness programmatically, or you're using macOS 10.13+

Apple deprecated their public IOKit Framework APIs in favor of an undocumented CoreDisplay API. Deprecation of IOKit broke existing utilities.

However, [`brightness` takes advantage of private CoreDisplay APIs that control display brightness](https://alexdelorenzo.me/programming/2018/08/16/reverse_engineering_private_apple_apis.html), allowing us to adjust it programmatically.

# Installation

```bash
# clone the repo
git clone https://github.com/thismachinechills/brightness.git


# install the application
cd brightness
pip3 install -r requirements.txt
python3 setup.py install


# check if it worked
brightness --help
```

## Notes

I've only tested this on macOS 10.13

## Prerequisites

### Python Version
Python 3.7.0+


### Application Dependencies
`pip3 install -r requirements.txt`


### Platform Dependencies

#### macOS

macOS 10.13+. 

All dependencies can be installed with `pip3 install -r requirements.txt`.

Or
`pip3 install pyobjc`

#### Windows
Windows 10+. 

All dependencies can be installed with `pip3 install -r requirements.txt`.

Or `pip3 install wmi`

#### Linux
Please install `xbacklight` and `xprintidle`.

##### Ubuntu & Debian
`sudo apt install xbacklight xprintidle`


# Usage

```bash
Usage: brightness [OPTIONS]

  brightness is a daemon and command-line utility that adjusts your
  display's brightness.

  In daemonized mode, brightness will use facial recognition to determine
  whether or not to change your display's brightness when your system goes
  idle.

  As a command-line utility, you can use brightness to get and set your
  display's brightness.

  Run without arguments to get the current brightness for the default
  display.

  $ brightness
  75.0

Options:
  -c, --capture INTEGER           Capture device.  [default: 0]
  -b, --brightness INTEGER RANGE  Screen brightness between 0 and 100.
                                  [default: 0]
  -d, --daemon                    Run in daemonized mode. Use facial
                                  recognition when system goes idle to
                                  determine whether to change brightness.
                                  [default: False]
  -i, --idle FLOAT                Seconds between inactivtiy and facial
                                  recognition.  [default: 300]
  -f, --frames INTEGER            Number of frames to capture in succession.
                                  Increase this value if you're getting false
                                  negatives  [default: 2]
  --help                          Show this message and exit.
```

## Example

Change the brightness to 50%

`brightness -b 50`

Run in daemonized mode. If the system has been idle for 10 minutes (600 seconds), `brightness` will check for faces.

`brightness -d -i 600`

Run in daemonized mode. If the system has been idle for 120 seconds, capture 3 frames from device `0` for use in facial recognition.

`brightness -d -c 0 -b 0 -i 120 -f 3`




# Contributions
All contributions are welcomed and encouraged. 

By submitting a contribution, you agree that your modifications can be distributed under the licensing terms below.

# License
See `LICENSE`.
 
## Alternative License
Please contact me if you'd like to use this software under another license.
