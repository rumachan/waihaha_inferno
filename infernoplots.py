#! /opt/local/epd-7.3.1/bin/python
# -*- coding: utf-8 -*-
"""
Inferno Lake plots
Plots inferno lake data
Created on Wed Sep 18 09:12:48 2013

modified:
    November 4, 2013 -  Nico Fournier
    - delete inferno_data.csv file if it exists.
    December 2013 - Duncan White
    Changes to enable script to be called from both the command line and a web service:
    - date range parameters can be passed in
    - image returned as bytes (instead of being written to file)
    - data read into memory rather than to temporary files (to make it thread safe for a use by a web application)

SVN info
Updated:     $Date: 2014-04-08 15:54:56 +1200 (Tue, 08 Apr 2014) $
Revision:    $Revision: 29181 $   
@author: craigm
"""

import matplotlib 
matplotlib.use('Agg') # this prevents the display
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pandas as pd
import datetime
from datetime import date, timedelta
import os
import io
import re

import ConfigParser

'''
Main function to allow the script from the command line.
Creates a png file containing plots for the last 80 days of inferno crater data,
and writes it to the file location configured in infernoplots.cfg
'''
def main(): 
    config = InfernoPlot.loadConfig()
    dataDir = config.get('Files', 'dataDir')
    outputDir = config.get('Files', 'outputDir')
    infernoPlot = InfernoPlot(dataDir)
    currentDate = datetime.date.today()
    plotPng = infernoPlot.getPlots(currentDate-timedelta(days=80), currentDate)
    with open(os.path.join(outputDir, 'inferno.png'), 'wb') as f:
        f.write(plotPng)
    
'''
InfernoPlot contains functions for creating data plots from
inferno crater data.
'''
class InfernoPlot(object):
    
    '''
    Constructor loads the location of inferno crater data from infernoplots.cfg
    if the dataDir parameter is not provided.
    '''
    def __init__(self, dataDir=None):
        if (dataDir == None):
            config = InfernoPlot.loadConfig()
            dataDir = config.get('Files', 'dataDir')            
        self.dataDir = dataDir
        self.yearDirRegex = re.compile('\d{4}')
        self.dataFileRegex = re.compile('\d{4}\.(\d{1,3})\.Inferno-utc.csv')
    
    '''
    startDate: datetime specifying the first day in the range of data to be included in the plots
    endDate: datetime specifying the last day in the range of data to be included in the plots
    
    Returns a byte string of a png file containing four inferno crater data plots.
    '''
    def getPlots(self, startDate, endDate):
        plt.ioff()  
        
        inferno = self.getData(startDate, endDate)    
        
        ########################################
        #plot data
        ########################################
        
        figure = Figure(figsize=(10,12))
        FigureCanvas(figure)
        
        #make subplots
        axes = figure.add_subplot(4,1,1)
        inferno.OverflowRate.plot(legend=True, ax=axes)
        axes.set_ylabel("l/s")
        axes.set_xlabel("Timestamp UTC")    
    
        axes = figure.add_subplot(4,1,2)
        inferno.OverflowTemp.plot(legend=True, ax=axes)
        axes.set_ylabel("degC")
        axes.set_xlabel("Timestamp UTC")
        axes.set_ylim([-10,110])  
        
        axes = figure.add_subplot(4,1,3)
        inferno.InfernoRL.plot(legend=True, ax=axes)
        axes.set_ylabel("m")
        axes.set_xlabel("Timestamp UTC")    
        
        axes = figure.add_subplot(4,1,4)
        inferno.InfernoTemp.plot(legend=True, ax=axes)
        axes.set_ylabel("degC")
        axes.set_xlabel("Timestamp UTC")
        axes.set_ylim([-10,110])  
        
        #create a time plot drawn label
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        figure.text(0, 0, 'Plot drawn: ' + str(timestamp))
        
        figure.subplots_adjust(hspace = 1.0)

        imageBuffer = io.BytesIO()
        figure.savefig(imageBuffer, format='png')
        return imageBuffer.getvalue()

    '''
    startDate: datetime specifying the first day in the range of data to be returned
    endDate: datetime specifying the last day in the range of data to be returned
    
    Returns a byte string of inferno crater csv data.
    '''    
    def getCsvData(self, startDate, endDate):
        
        inferno = self.getData(startDate, endDate)   
        csvBuffer = io.BytesIO()
        inferno.to_csv(csvBuffer, encoding='us-ascii')
        return csvBuffer.getvalue()
        
    '''
    startDate: datetime specifying the first day in the range of data to be returned
    endDate: datetime specifying the last day in the range of data to be returned
    
    Returns a pandas DataFrame object containing inferno crater data in the given range.
    '''
    def getData(self, startDate, endDate):
        
        ####################################################
        #loop through each daily data file in range and join them together
        ####################################
        dataframeList = []
        numberOfDays = (endDate - startDate).days + 1
        for day in range(0,numberOfDays):
            date = startDate + timedelta(days=day)
            year = date.strftime("%Y")
            julian = date.strftime("%j")
            dataFile = os.path.join(self.dataDir, year, year + "." + julian + ".Inferno-utc.csv")
            if os.path.exists(dataFile):
                dataframeList.append(self.__readData(dataFile))
          
        ########################################
        #read data in
        ########################################
        return pd.concat(dataframeList)
    
    '''
    Returns the first and last day of the currently available inferno crater data.
    Values are returned as two datetimes. 
    '''
    def getDateRange(self):
        
        years = []
        for name in os.listdir(self.dataDir):
            if os.path.isdir(os.path.join(self.dataDir, name)):
                if self.yearDirRegex.match(name):
                    years.append(name)
        years.sort()
        
        firstDay = self.__getJulianDayInYear(years[0], 0)
        lastDay = self.__getJulianDayInYear(years[len(years) - 1], -1)

        return firstDay, lastDay
 
    '''
    Checks the data directory to find the first or last day data is available for in the
    given year.
    
    year: e.g "2013"
    dayPosition: 0 to get the first day in the year, -1 to get the last day in the year.
    
    Returns the first or last day, as a datetime.
    '''  
    def __getJulianDayInYear(self, year, dayPosition):
        dayFileList = []
        for name in os.listdir(os.path.join(self.dataDir, year)):
            if not os.path.isdir(os.path.join(self.dataDir, name)) and self.dataFileRegex.match(name):
                dayFileList.append(name)
        dayFileList.sort()
        julianDay = self.dataFileRegex.match(dayFileList[dayPosition]).group(1)     
        return datetime.datetime.strptime(str(year) + ' ' + str(julianDay), '%Y %j')     
        
    
    ########################################
    #Custom date converter from year.julain to DMY
    ########################################
    def __datetimeConverter(self, time):
        return datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S %Z")
    
    def __readData(self, fileName):
        return pd.read_table(fileName, skiprows=[0,2], header=0, index_col=0, date_parser=self.__datetimeConverter, usecols=[0,1,2,3,4,5,6,7,8,9])    
    
    @classmethod
    def loadConfig(cls):
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(scriptDir, 'infernoplots.cfg'))
        return config

if __name__ == '__main__':
    main()
