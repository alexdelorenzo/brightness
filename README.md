# Installation

`git clone https://github.com/thismachinechills/brightness.git`

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
Usage: change_brightness.py [OPTIONS]

  Use system idle information and facial recognition to change screen
  brightness when your computer idle and there isn't anyone in front of the
  screen.

Options:
  -d, --device INTEGER            Capture device.  [default: 0]
  -b, --brightness INTEGER RANGE  Screen brightness between 0 and 100.
                                  [default: 0]
  -i, --idle INTEGER              Seconds between inactivtiy and facial
                                  recognition.  [default: 10]
  -f, --frames INTEGER            Number of frames to capture in succession.
                                  Increase this value if you're getting false
                                  negatives  [default: 3]
  -s, --step                      Enable stepping.
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
