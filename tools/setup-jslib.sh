#!/bin/bash

set -e

if [ ! -f "orgviz/__init__.py" ]
then
    echo "execute this script at root of the working directory"
    exit 1
fi

tmpdir=tmp
logf=$tmpdir/setup-jslib.log
destdir=orgviz/static/lib

# FullCalendar (http://arshaw.com/fullcalendar/)
fc_name=fullcalendar-1.5.2
fc_zipname=$fc_name.zip
fc_url="http://arshaw.com/fullcalendar/downloads/"$fc_zipname
fc_zippath=$tmpdir/$fc_zipname

# jQuery Hotkeys (https://github.com/tzuryby/jquery.hotkeys)
hk_name=jquery.hotkeys

# ColorBox (http://jacklmoore.com/colorbox)
cb_name=colorbox

log-it(){
    {
        echo
        echo "------------------------------------------------------------"
        date
        echo "$@"
        echo
    } >> $logf
}

mkdir -p $tmpdir
rm -rf $logf

log-it "Donload JS libraries"
git submodule --quiet update --init >> $logf
[ -e "$fc_zippath" ] || wget $fc_url -O $fc_zippath -a $logf

log-it "Decompress JS libraries"
rm -rf $tmpdir/$fc_name/
unzip $fc_zippath -d $tmpdir >> $logf

log-it "Copy JS libraries"
rm -rf $destdir
mkdir -p $destdir
cp -r $tmpdir/$fc_name/fullcalendar $destdir
cp -r $tmpdir/$fc_name/*-LICENSE.txt $destdir/fullcalendar
cp -r $tmpdir/$fc_name/jquery $destdir
cp -r lib/$hk_name/jquery.hotkeys.js $destdir/jquery
cp -r lib/$cb_name/colorbox $destdir
cp -r lib/$cb_name/example1/* $destdir/colorbox

# Note: Only FullCalendar has license document.  That's why I am not
# copying it only for FullCalendar.
