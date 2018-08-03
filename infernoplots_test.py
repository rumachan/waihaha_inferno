#! /opt/local/epd-7.3.1/bin/python
# -*- coding: utf-8 -*-
"""
Inferno Lake plots
Plots last 90 days of inferno lake data
Created on Wed Sep 18 09:12:48 2013

modified:
    November 4, 2013 -  Nico Fournier
    - delete inferno_data.csv file if it exists.
   
@author: craigm
"""

import matplotlib 
matplotlib.use('Agg') # this prevents the display
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from datetime import date, timedelta
import shutil
import fileinput
import os

plt.ioff()

####################################################
#loop through the last 80 days of files and join them together
#first part takes files from 2 days ago to 89 days ago, strips off the first 3 header lines and joins them as one file
####################################

# ADDED BY NF ON 2013-11-04
# delete bulk file if it already exists
if os.path.exists("/home/volcano/programs/inferno/inferno_data.csv"):
    os.remove("/home/volcano/programs/inferno/inferno_data.csv")


for day in reversed(range(25,83)):
    date = datetime.date.today()-timedelta(days=day)
    year = date.strftime("%Y")
    julian = date.strftime("%j")
    File = "/home/sysop/csi/inferno/" + year + "/" + year + "." + julian + ".Inferno-utc.csv"
    data="".join(open(File).readlines()[3:])
    open("/home/volcano/programs/inferno/inferno_data.csv", "a").write(data)
  
#this creates the filename from 80 days ago.
lastdate = datetime.date.today()-timedelta(days=80)  # default is timedelta(days=80)
lastyear = lastdate.strftime("%Y")
lastjulian = lastdate.strftime("%j")
lastfile = "/home/sysop/csi/inferno/" + lastyear + "/" + lastyear + "." + lastjulian + ".Inferno-utc.csv"

#this adds the file from 90days ago with the header row intact. it creates the final data file "inferno_90days.csv"
alldata = open("/home/volcano/programs/inferno/inferno_90days-utc.csv",'w')
shutil.copyfileobj(open(lastfile, "r"),alldata)
shutil.copyfileobj(open("/home/volcano/programs/inferno/inferno_data.csv","r"),alldata)
alldata.close()

########################################
#Custom date converter from year.julain to DMY
########################################
def datetime_converter(time):
	return datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S %Z")

########################################
#read data in
########################################
inferno=pd.read_table('/home/volcano/programs/inferno/inferno_90days-utc.csv', skiprows=[2], header=1, index_col=0, date_parser=datetime_converter, usecols=[0,1,2,3,4,5,6,7,8,9])
#print inferno

########################################
#plot data
########################################
plt.figure(figsize=(10,12)) #figsize (x,y)

#make subplots
plt.subplot(4,1,1)
inferno.OverflowRate.plot(legend=True)
plt.ylabel("l/s")
plt.xlabel("Timestamp UTC")

plt.subplot(4,1,2)
inferno.OverflowTemp.plot(legend=True)
plt.ylabel("degC")
plt.xlabel("Timestamp UTC")

plt.subplot(4,1,3)
inferno.InfernoRL.plot(legend=True)
plt.ylabel("m")
plt.xlabel("Timestamp UTC")

plt.subplot(4,1,4)
inferno.InfernoTemp.plot(legend=True)
plt.ylabel("degC")
plt.xlabel("Timestamp UTC")

#create a time plot drawn label
timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
plt.annotate('Plot drawn: ' + str(timestamp), (inferno.index[-2800], 11 ), xytext=None)

#
plt.subplots_adjust(hspace = 0.5)

#remove temp files
#os.remove("/home/volcano/programs/inferno/inferno_data.csv")
#os.remove("/home/volcano/programs/inferno/inferno_90days-utc.csv")

#save the plot
plt.savefig('/var/www/html/volcanoes/okataina/inferno.png')
plt.close()
