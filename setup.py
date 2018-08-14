import os
from os import getcwd

from setuptools import setup
from pathlib import Path

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as file:
    readme = file.read()

with open('requirements.txt', 'r') as file:
    requirements = [line.strip('\n')
                    for line in file.readlines()
                    if line.strip('\n')]

CMD = 'brightness'

OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['objc', 'cv2', 'face_recognition'],
    'bdist_base': str(Path(getcwd()).parent) + '/build',
    'dist_dir': str(Path(getcwd()).parent) + '/dist'
}

setup(
    name="change_brightness",
    version="0.1.0",
    author="Alex DeLorenzo",
    author_email="alexdelorenzo@gmail.com",
    description="Use facial recognition and system idle time to dim your screen.",
    license="AGPL-3.0",
    keywords="facial recognition brightness screen display change mac windows linux",
    url="https://github.com/thismachinechills/brightness",
    packages=['brightness'],
    long_description=readme,
    zip_safe=False,
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        'console_scripts':
            ['brightness = brightness.change_brightness:run']
    },

    ## app nonsense
    app=['brightness/change_brightness.py'],
    datafiles=['brightness/.'],
    options={'py2app': OPTIONS},
    setup_requires=['py2app']

)
