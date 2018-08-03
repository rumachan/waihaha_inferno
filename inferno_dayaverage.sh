#! /bin/bash

#  SCRIPT TO PRODUCE DAILY AVERAGES OF 15MIN DATA.

#rm -f /home/volcano/data/inferno/inferno_daily_average.csv

#LOOP FOR INFERNO LAKE TEMP AVERAGE

#if creating this file from scratch uncomment the awk line below

#awk 'BEGIN {print "DAY, LAKE TEMP, LAKE RL, OVERFLOW TEMP, OVERFLOW RATE"}' >> /home/volcano/data/inferno/inferno_daily_average.csv

#if creating this file from scratch change the n values to get all the data.  Data starts approx 23 june 2012 (julian day 174).  n values need to be negative, in the example below it gets data from 104 days ago to 1 day ago.

#changed to -1..-1 to just get "yesterday" and append that.
#changed to -8..-8 to  get data from a week ago.  This is to make sure all the daily data are there in case of comms outages etc.

for n in {-1..-1}; do

if [ `date -d$n"day" +%j` -ge 365 ]; then #was -ge 165
        year=`date -d-1"year" +%Y`
        else
        year=`date +%Y`
        fi
julian=`date -d$n"day" +%j`
#echo $julian
awk '{lt=lt+$6; ll=ll+$9; ot=ot+$10; ol=ol+$12}END{OFS=","; print $1, lt/NR, ll/NR, ot/NR, ol/NR}' /home/sysop/csi/inferno/$year/$year.$julian.Inferno.csv >> /home/volcano/data/inferno/inferno_daily_average.csv

done

#copy to webserver for download.
#cp /home/volcano/data/inferno/inferno_daily_average.csv /opt/local/apache/htdocs/volcanoes/okataina/inferno_daily_average.csv
cp /home/volcano/data/inferno/inferno_daily_average.csv /var/www/html/inferno/inferno_daily_average.csv

