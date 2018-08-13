#!/usr/bin/env bash

export BRIDGESUPPORT=".bridgesupport"
export TOOLCHAINS_DIR="/Applications/Xcode.app/Contents/Developer/Toolchains"
export WORKING_DIR=`pwd`


# fix issue where gen_bridge_metadata cannot find toolchain
# https://trac.macports.org/ticket/54939
if defaults read loginwindow SystemVersionStampAsString | grep '10.13'
then
    cd "$TOOLCHAINS_DIR"

    if [ ! -e OSX10.13.xctoolchain ]
    then
        sudo ln -s XcodeDefault.xctoolchain OSX10.13.xctoolchain
    fi

    cd "$WORKING_DIR"
fi

# http://www.slevenbits.com/blog/2012/11/pyobjc-and-iokit-on-mac-os-x.html
gen_bridge_metadata -c "-l/System/Library/Frameworks/IOKit.framework/IOKit
                        -I/System/Library/Frameworks/IOKit.framework/Headers/graphics
                        -I/System/Library/Frameworks/IOKit.framework/Headers" \
                        /System/Library/Frameworks/IOKit.framework/Headers/graphics/IOGraphicsLib.h \
                        /System/Library/Frameworks/IOKit.framework/Headers/IOKitLib.h  \
                        /System/Library/Frameworks/IOKit.framework/Headers/graphics/IOGraphicsTypes.h > "$BRIDGESUPPORT"

# delete item with weird signature
# https://stackoverflow.com/questions/19456518/invalid-command-code-despite-escaping-periods-using-sed
sed -i "" -e  "/name='IOTimingInformation'/d" "./$BRIDGESUPPORT"

