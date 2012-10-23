#!/bin/sh

set -e

if [ ! -f "orgviz/__init__.py" ]
then
    echo "execute this script at root of the working directory"
    exit 1
fi

tmpdir=tmp
destdir="orgviz/static/"
libdir=$destdir/lib

fc_name=fullcalendar-1.5.2
fc_zipname=$fc_name.zip
fc_url="http://arshaw.com/fullcalendar/downloads/"$fc_zipname
fc_zippath=$tmpdir/$fc_zipname

hk_name=tzuryby-jquery.hotkeys
hk_zipname=$hk_name.zip
hk_url=https://github.com/tzuryby/jquery.hotkeys/zipball/master
hk_zippath=$tmpdir/$hk_zipname

cb_name=colorbox
cb_zipname=$cb_name.zip
cb_url=http://jacklmoore.com/colorbox/colorbox.zip
cb_zippath=$tmpdir/$cb_zipname

tg_name=timeglider-jquery_widget
tg_zipname=$tg_name.zip
tg_url=https://github.com/timeglider/jquery_widget/zipball/master
tg_zippath=$tmpdir/$tg_zipname


mkdir -p $destdir
mkdir -p $tmpdir

[ -e "$fc_zippath" ] || wget $fc_url -O $fc_zippath
[ -e "$hk_zippath" ] || wget $hk_url -O $hk_zippath
[ -e "$cb_zippath" ] || wget $cb_url -O $cb_zippath
[ -e "$tg_zippath" ] || wget $tg_url -O $tg_zippath
rm -rf $tmpdir/$fc_name/
rm -rf $tmpdir/$hk_name-*/
rm -rf $tmpdir/$cb_name/
rm -rf $tmpdir/$tg_name-*/
unzip $fc_zippath -d $tmpdir
unzip $hk_zippath -d $tmpdir
unzip $cb_zippath -d $tmpdir
unzip $tg_zippath -d $tmpdir

cp -r $tmpdir/$fc_name/fullcalendar $destdir
cp -r $tmpdir/$fc_name/jquery $destdir
cp -r $tmpdir/$hk_name-*/jquery.hotkeys.js $destdir/jquery
cp -r $tmpdir/$cb_name/colorbox $destdir
cp -r $tmpdir/$cb_name/example1/* $destdir/colorbox
mkdir -p $libdir/timeglider/
cp -r $tmpdir/$tg_name-*/* $libdir/timeglider/
