# ☀ brightness: Adjust display brightness with your 🌞

`brightness` is a daemon and command-line utility you can use to adjust your display's brightness.

In daemonized mode, `brightness` will use facial recognition to determine whether or not to change your display's brightness when your system is idle.

As a command-line utility, you can use `brightness` to get and set your display's brightness.

# Installation

```bash
# clone the repo
git clone https://github.com/thismachinechills/brightness.git
cd brightness


# install the application
pip3 install -r requirements.txt
python3 setup.py install


# check if it worked
brightness --help
```


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

  Use system idle information and facial recognition to change screen
  brightness when your computer idle and there isn't anyone in front of the
  screen.

  Run without arguments to get the current brightness for the default
  display.

  $ brightness

  75.0

Options:
  -c, --capture INTEGER           Capture device.  [default: 0]
  -b, --brightness INTEGER RANGE  Screen brightness between 0 and 100.
                                  [default: 0]
  -d, --daemon                    Use this setting to simply change the
                                  display brightness, while ignoring other
                                  settings besides brightness and device.
                                  [default: False]
  -i, --idle FLOAT                Seconds between inactivtiy and facial
                                  recognition.  [default: 300]
  -f, --frames INTEGER            Number of frames to capture in succession.
                                  Increase this value if you're getting false
                                  negatives  [default: 2]
  --help                          Show this message and exit.
```

## Example
Check for system idle time every 120 seconds, then if idle, capture 2 frames from device `0` for use in facial recognition.

`python3 change_brightness.py -d 0 --brightness 0 --idle 120 -f 2`


# Contributions
All contributions are welcomed and encouraged. 

By submitting a contribution, you agree that your modifications can be distributed under the licensing terms below.

# License
See `LICENSE`.
 
## Alternative License
Please contact me if you'd like to use this software under another license.
