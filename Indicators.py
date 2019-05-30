"""

5/29/2019 
Robert Sloan, Bill Paceman
replicating Al Zmyslowski's Technical and Economic Indicators
Based on Al Zmyslowski's Stock Market Review - Technical & Economic Indicators
from the American Association of Individual Investors www.aaii.com

TO DO

  Store stock data in a way that calculations could be accuratly recreated
  Put Spreadsheet in Al's order
  
"""
# Import libraries
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 400)
import numpy as np
import os # misc operating system interfaces
from glob import glob # unix pathname functions


#def loadTickers(start_date,record_date,todays_date,tickers,path=None):  # not sure what to use path for
def loadTickers(start_date,record_date,todays_date,tickers):
  from distutils.version import LooseVersion, StrictVersion
  from pandas_datareader import data
  if StrictVersion(pd.__version__) < StrictVersion(u'0.23.4'):
    print ("Error: Old version of pandas used in loadTickers gives columns of objects, not floats")
  print ("Pandas ",pd.__version__ , " Numpy ", np.__version__)
  if not os.path.exists('Figures'):
    os.makedirs('Figures')
  if not os.path.exists('Spreadsheets'):
    os.makedirs('Spreadsheets')

  
  return data.DataReader(tickers, 
                       start=start_date, 
                       end=record_date, 
                       data_source='yahoo')['Adj Close']


def allIndicators(moduleList):#
  import datetime

  # create a date range
  currentDT = datetime.datetime.now()
  todays_date = str(currentDT.year) + "-" + str(currentDT.month) + "-"+  str(currentDT.day)
  # NOTE: can make the record_date a date in the past to generate previous Technical and Economic indicators
  record_date = todays_date
  oneYearAgo = (currentDT - datetime.timedelta(366))
  start_date = str(oneYearAgo.year) + "-" + str(oneYearAgo.month) + "-"+  str(oneYearAgo.day)
 
  # Load the tickers for date range
  data = loadTickers(start_date,record_date,todays_date,["SPY","%5EIRX"])

  # Determine last market day of last month
  # Get the last day of last month by taking the first day of this month
  # and subtracting 1 day.
  lastDay = datetime.date(currentDT.year, currentDT.month, 1) - datetime.timedelta(1)
  # Set the day to 1 gives us the start of the month
  firstDay = lastDay.replace(day=1)
  last_EOM_date = data["SPY"].loc[firstDay:lastDay].last('1D').index # get the last market day last month
  
  strLast_EOM_date = last_EOM_date.strftime('%Y-%m-%d') # get the last market day last month
  print("Last Market Day last Month", strLast_EOM_date)

  # Determine last market day of the month before last
  # Get the last day of last month by taking the first day of last month
  # and subtracting 1 day.
  lastDay = datetime.date(currentDT.year, currentDT.month-1, 1) - datetime.timedelta(1)
  # Set the day to 1 gives us the start of the month
  firstDay = lastDay.replace(day=1)
  previous_EOM_date = data["SPY"].loc[firstDay:lastDay].last('1D').index # get the last market day last month

  strPrevious_EOM_date = previous_EOM_date.strftime('%Y-%m-%d') # and month before last
  print("Last Market Day Month before last", strPrevious_EOM_date)
  
  #spreadsheetData = []
  #for for module in moduleList: spreadsheetData.append(__import__(module).Indicator(data))
  
  spreadsheetList = [__import__(module).Indicator(data, record_date, last_EOM_date, previous_EOM_date) for module in moduleList]
  # Turn aggegated results into spreadsheet.
  # print("type(spreadsheetData) = ", type(spreadsheetData))
  # print (spreadsheetData)
  print("\n")
  spreadsheet = pd.DataFrame(spreadsheetList, columns = ['Technical Indicator','Frequency', 'MonthBeforeLast', 'LastMonth','Comment'])

  writer = pd.ExcelWriter(str('Spreadsheets/'+record_date +'_indicator_sheet.xlsx'))
  spreadsheet.to_excel(writer,'Indicators', index=False)
  writer.save()
  
  
#===========================================================================================================
# the following line is to allow the calling of this code from a command line  
if __name__ == '__main__':   
  modules =[name[:-3] for name in glob("I_*.py")]#["I5MGain","I10MSMASPY"]
  allIndicators(modules)

  

  
