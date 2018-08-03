#! /bin/bash
gmt=/usr/bin
$gmt/gmtset INPUT_DATE_FORMAT yyyy-mm-dd
$gmt/gmtset MEASURE_UNIT cm
$gmt/gmtset GLOBAL_X_SCALE 1.0
$gmt/gmtset GLOBAL_Y_SCALE 1.0
$gmt/gmtset PAPER_MEDIA a3
$gmt/gmtset PAGE_ORIENTATION portrait
$gmt/gmtset INPUT_CLOCK_FORMAT hh:mm:ss
$gmt/gmtset TIME_FORMAT_PRIMARY abbreviated
$gmt/gmtset TIME_FORMAT_SECONDARY full
$gmt/gmtset TIME_LANGUAGE UK
$gmt/gmtset LABEL_FONT_SIZE 10
$gmt/gmtset ANNOT_FONT_SIZE_PRIMARY 10
$gmt/gmtset ANNOT_FONT_SIZE_SECONDARY 10
$gmt/gmtset HEADER_OFFSET 0c
$gmt/gmtset HEADER_FONT_SIZE 12
bin_dir=/home/volcano/bin
out_dir=/home/volcano/output/inferno

#select the data, the if loop determines which year to use. should be -1..-90 by default
for n in {-1..-82}; do

	if [ `date -d$n"day" +%j` -ge 275 ] ; then
	year=`date -d-1"year" +%Y`
	else
	year=`date +%Y`
	fi
		julian=`date -d$n"day" +%j`
		cd /home/sysop/csi/inferno/$year
		tail -n +4 $year.$julian.Inferno.csv | cat >> /home/volcano/programs/inferno/inferno_localtime_90days.csv
done


#make the plot

cd /home/volcano/programs/inferno

SCALE=-JX20T/5

#inferno lake temp#
awk '0<$6 && $6<100 {print$1"T"$2, $6}' /home/volcano/programs/inferno/inferno_localtime_90days.csv > /home/volcano/programs/inferno/infernotemp.xy
R=`$gmt/minmax -I0.5 -f0T,1f /home/volcano/programs/inferno/infernotemp.xy`
echo $R
$gmt/psxy $R $SCALE -Bsa1OS/a0f0 -Bpa7Rf1d/a5f2.5:"degC":WSEn -K -U -Sc0.05 -GRed  /home/volcano/programs/inferno/infernotemp.xy > $out_dir/inferno.ps
$gmt/pstext << eof -R0/21/0/29.7 -JX15/5 -K -O >> $out_dir/inferno.ps
0.5 6 12 0 1 TL Inferno Lake Temperature
eof

#inferno lake RL#
awk '{print$1"T"$2, $9}' /home/volcano/programs/inferno/inferno_localtime_90days.csv > /home/volcano/programs/inferno/infernoRL.xy
R=`$gmt/minmax -I0.5 -f0T,1f /home/volcano/programs/inferno/infernoRL.xy`
echo $R
$gmt/psxy $R $SCALE -Bsa1OS/a0f0 -Bpa7Rf1d/a1f0.5:"RL (m) ":WSEn -O -K -Y7 -Sc0.05 -GRed  /home/volcano/programs/inferno/infernoRL.xy >> $out_dir/inferno.ps
$gmt/pstext << eof -R0/21/0/29.7 -JX15/5 -K -O >> $out_dir/inferno.ps
0.5 6 12 0 1 TL Inferno Lake Level
eof


#inferno overflow temp#
awk '0<$10 && $10<100 {print$1"T"$2, $10}' /home/volcano/programs/inferno/inferno_localtime_90days.csv > /home/volcano/programs/inferno/overflowtemp.xy
R=`$gmt/minmax -I0.5 -f0T,1f /home/volcano/programs/inferno/overflowtemp.xy`
echo $R
$gmt/psxy $R $SCALE -Bsa1OS/a0f0 -Bpa7Rf1d/a5f2.5:"degC":WSEn -K -O -Sc0.05 -Y7 -GRed  /home/volcano/programs/inferno/overflowtemp.xy >> $out_dir/inferno.ps
$gmt/pstext << eof -R0/21/0/29.7 -JX15/5 -K -O >> $out_dir/inferno.ps
0.5 6 12 0 1 TL Inferno Overflow Temperature
eof

#inferno overflow rate#
#awk '$12 <1000 {print$1"T"$2, $12}' /home/volcano/programs/inferno/inferno_localtime_90days.csv > /home/volcano/programs/inferno/overflowrate.xy
awk '{if ($12==7999.0) print$1"T"$2, 0; else print$1"T"$2, $12 }' /home/volcano/programs/inferno/inferno_localtime_90days.csv > /home/volcano/programs/inferno/overflowrate.xy
R=`$gmt/minmax -I0.5 -f0T,1f /home/volcano/programs/inferno/overflowrate.xy`
echo $R
$gmt/psxy $R $SCALE -Bsa1OS/a0f0 -Bpa7Rf1d/a10f5:"l/s":WSEN -K -O -Sc0.05 -Y7 -GRed  /home/volcano/programs/inferno/overflowrate.xy >> $out_dir/inferno.ps
$gmt/pstext << eof -R0/21/0/29.7 -JX15/5 -O >> $out_dir/inferno.ps
0.5 6 12 0 1 TL Inferno Overflow Rate
eof

#tidy up files

rm -f *.xy
#rm /home/volcano/programs/inferno/inferno_localtime_90days.csv

$bin_dir/pstogif.pl $out_dir/inferno 300

#copy to webserver
cp $out_dir/inferno.gif /opt/local/apache/htdocs/volcanoes/okataina/inferno.gif
