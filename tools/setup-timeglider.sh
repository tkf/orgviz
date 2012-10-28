#!/bin/bash

set -e

if [ ! -f "orgviz/__init__.py" ]
then
    echo "execute this script at root of the working directory"
    exit 1
fi

tmpdir=tmp
logf=$tmpdir/setup-timeglider.log
destdir=orgviz/static/lib

# Timeglider (http://timeglider.com)
tg_name=timeglider_widget_code
tg_zipname=$tg_name.zip
tg_url=http://timeglider.com/widget/$tg_zipname
tg_zippath=$tmpdir/$tg_zipname

[ -e "$tg_zippath" ] || wget $tg_url -O $tg_zippath
rm -rf $tmpdir/$tg_name
unzip $tg_zippath -d $tmpdir
mkdir -p $destdir/timeglider/
cp -r $tmpdir/$tg_name/* $destdir/timeglider/
