# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import base64
import re
from datetime import datetime as dt

# BEGIN IMPORTS AND DEFS FROM Main_Indicators.py
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
  #print(" in loadTickers")
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


def allIndicators(moduleList, date):
  import datetime
  #print(" in allIndicators ")
  # create a date range
  #currentDT = datetime.datetime.now()
  #currentDT = datetime.date(2019, 2, 1)
  currentDT = dt.strptime(date, "%Y-%m-%d")
  #if currentDT.month < 10:
  #  todays_date = str(currentDT.year) + "-0" + str(currentDT.month) + "-" + str(currentDT.day)
  #else:
  #  todays_date = str(currentDT.year) + "-" + str(currentDT.month) + "-" + str(currentDT.day)
  todays_date = date
  #todays_date = str(currentDT.year) + "-" + str(currentDT.month) + "-"+  str(currentDT.day)
  # NOTE: can make the record_date a date in the past to generate previous Technical and Economic indicators
  record_date = todays_date
  print("########## date="+date)
  print("########## record_date="+record_date)
  #oneYearAgo = (currentDT - datetime.timedelta(366))
  # two years of data is needed to calculate 12M Gain and Fund X Score indicators
  twoYearsAgo = (currentDT - datetime.timedelta(731))
  start_date = str(twoYearsAgo.year) + "-" + str(twoYearsAgo.month) + "-"+  str(twoYearsAgo.day)
 
  # Load the tickers for date range
  data = loadTickers(start_date,record_date,todays_date,["SPY","BIL"])
  #print(" exited loadTickers")
  # Determine last market day of last month
  # Get the last day of last month by taking the first day of this month
  # and subtracting 1 day.
  lastDay = datetime.date(currentDT.year, currentDT.month, 1) - datetime.timedelta(1)
  # Set the day to 1 gives us the start of the month
  firstDay = lastDay.replace(day=1)
  last_EOM_date = data["SPY"].loc[firstDay:lastDay].last('1D').index # get the last market day last month
  
  strLast_EOM_date = last_EOM_date.strftime("%Y-%m-%d") # get the last market day last month
  print("Last Market Day last Month", str(strLast_EOM_date[0]))
  # print("type(strLast_EOM_date) = ", type(str(strLast_EOM_date[0])))
  # last_EOM_date = str(strLast_EOM_date[0])
  # Determine last market day of the month before last
  # Get the last day of last month by taking the first day of last month
  # and subtracting 1 day.
  # Set the day to 1 gives us the start of the month
  
  if (currentDT.month > 1):
    lastDay = datetime.date(currentDT.year, currentDT.month-1, 1) - datetime.timedelta(1)
  else:
    lastDay = datetime.date(currentDT.year-1, currentDT.month+11, 1) - datetime.timedelta(1)
  firstDay = lastDay.replace(day=1)
  previous_EOM_date = data["SPY"].loc[firstDay:lastDay].last('1D').index

  # get the last market day last month

  strPrevious_EOM_date = previous_EOM_date.strftime('%Y-%m-%d') # and month before last
  print("Last Market Day Month before last", str(strPrevious_EOM_date[0]))
  
  # the following line is equivolent to :
  # spreadsheetData = []
  #for for module in moduleList: spreadsheetData.append(__import__(module).Indicator(data))
  
  spreadsheetList = [__import__(module).Indicator(data, record_date, last_EOM_date, previous_EOM_date) for module in moduleList]
  
  # print(" done with streadsheetList ")
  # Turn aggegated results into spreadsheet.
  # print("type(spreadsheetData) = ", type(spreadsheetData))
  # print (spreadsheetData)
  print("\n")
  spreadsheet = pd.DataFrame(spreadsheetList, columns = ['Technical Indicator','Frequency', 'MonthBeforeLast', 'LastMonth','Comment'])
  print(spreadsheet)
  
  writer = pd.ExcelWriter(str('Spreadsheets/'+record_date +'_indicator_sheet.xlsx'))
  spreadsheet.to_excel(writer,'Indicators', index=False)
  writer.save()

  writer2 = pd.ExcelWriter(str('Spreadsheets/indicator_sheet.xlsx'))
  #writer2 = pd.ExcelWriter(str('assets/'+record_date +'_indicator_sheet.xlsx')) #repeats over and over
  spreadsheet.to_excel(writer2,'Indicators', index=False)
  writer2.save()
# END IMPORTS AND DEFS FROM Main_Indicators.py

#import datetime
#currentDT = datetime.datetime.now()
#todays_date = str(currentDT.year) + "-" + str(currentDT.month) + "-"+  str(currentDT.day)
## NOTE: can make the record_date a date in the past to generate previous Technical and Economic indicators
#record_date = todays_date
#spreadsheet = pd.read_excel(open('Spreadsheets/2019-7-19_indicator_sheet.xlsx','rb'), sheetname='Indicators')
#spreadsheet = pd.read_excel(open('Spreadsheets/2019-7-19_indicator_sheet.xlsx','rb'))
spreadsheet = pd.read_excel(open('Spreadsheets/indicator_sheet.xlsx','rb'))
#spreadsheet = pd.read_excel(open(str('Spreadsheets/'+record_date +'_indicator_sheet.xlsx'),'rb'))

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

all_options = {
    'America': ['New York City', 'San Francisco', 'Cincinnati'],
    'Canada': [u'Montréal', 'Toronto', 'Ottawa']
}
global_indicator = ""

modules =[name[:-3] for name in glob("i*.py")] #i.e.i01_10MSMASPY.py
modules.sort()

app.layout = html.Div([
    dcc.DatePickerSingle(
        id='current-date',
        date=dt.now()
    ),
    html.Div(id='display-date', style={'display': 'none'}),
    #html.Div(id='display-date'),
    
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label="Image", children=[
            dcc.RadioItems(
                #id='countries-dropdown',
                #options=[{'label': k, 'value': k} for k in all_options.keys()],
                #value='America'
                id='indicators-dropdown',
                options=[{'label': k, 'value': k} for k in modules],
                value=modules[0]
            ),
            html.Div(id='display-indicator', style={'display': 'none'}),
            html.Div(html.Img(id='display-image')),
        ]),
        dcc.Tab(label="Dataframe", children=[
            #html.H4(children='Technical Indicators'),
            html.H4(id='title-pretable'),
            html.Pre(id='display-pretable')
        ]),
        dcc.Tab(label="Debug", children=[
            html.Button(id='list-button', n_clicks=0, children='List Files'),
            html.Button(id='erase-button', n_clicks=0, children='Erase Files'),
            html.Div(id='display-files'),
            html.Div(id='erase-files', style={'display': 'none'}),
            html.H4(children='Technical Indicators'),
            generate_table(spreadsheet)
        ])
    ])
])


@app.callback(
    Output('display-files', 'children'),
    [Input('list-button', 'n_clicks')])
def display_files(nClicks):
    listOfFiles = os.listdir('assets/')
    for i in listOfFiles:
        file = "assets/"+i
        if os.path.exists(file):
            #os.remove(file)
            print("LIST "+file)
    return "|\n".join(listOfFiles)

@app.callback(
    Output('erase-files', 'children'),
    [Input('erase-button', 'n_clicks')])
def erase_files(nClicks):
    listOfFiles = os.listdir('assets/')
    for i in listOfFiles:
        file = "assets/"+i
        if os.path.exists(file):
            os.remove(file)
            print("REMOVE "+file)
    return "|\n".join(listOfFiles)

@app.callback(
    Output('display-date', 'children'),
    [Input('current-date', 'date')],
    [State('indicators-dropdown', 'value')])
def set_record_date(date, indicator):
    if date is not None:
        #date = re.sub("T*","", date)
        date = date[:10]
    print("##### current_date="+date)
    print("##### indicator   ="+indicator)
    #if os.path.exists("assets/i02_Mini-Dipper SPY.png"):
    #    os.remove("assets/i02_Mini-Dipper SPY.png")
    #module = [indicator]
    #oneIndicator(module, date)
    listOfFiles = os.listdir('assets/')
    for i in listOfFiles:
        file = "assets/"+i
        if os.path.exists(file):
            #os.remove(file)
            print("REMOVE "+file)
    modules =[name[:-3] for name in glob("i*.py")] #i.e.i01_10MSMASPY.py
    modules.sort()
    allIndicators(modules, date)
    return date

@app.callback(
    Output('display-pretable', 'children'),
    [Input('current-date', 'date')])
def set_record_date(date):
    if date is not None:
        #date = re.sub("T*","", date)
        date = date[:10]
    print("##### current_date="+date)
    df = pd.read_excel(open("Spreadsheets/"+date+"_indicator_sheet.xlsx","rb"))
    #df.rename({"Technical Indicator" : date+" Technical Indicator"}, axis=1)
    #pretable = "Technical Indicators, "+str(date)+"\n\n"+str(df)
    pretable = str(df)
    return pretable

@app.callback(
    Output('title-pretable', 'children'),
    [Input('current-date', 'date')])
def set_title_pretable(date):
    if date is not None:
        date = date[:10]
    title = "Technical Indicators, "+date
    return title

# @app.callback(
    # Output('title-table', 'children'),
    # [Input('current-date', 'date')])
# def set_title_table(date):
    # if date is not None:
        # date = date[:10]
    # title = "Technical Indicators, "+date
    # return title

#@app.callback(
#    Output('display-indicator', 'children'),
#    [Input('current-date', 'date'),
#     Input('indicators-dropdown', 'value')])
#def set_cities_options(date, indicator):
#    #module = [name for name in glob(selected_indicator+".py")]
#    if date is not None:
#        date = date[:10]
#    print("##### 2current_date="+date)
#    print("##### 2indicator   ="+indicator)
#    module = [indicator]
#    oneIndicator(module, date)
#    return indicator

@app.callback(
    Output('display-image', 'src'),
    [Input('current-date', 'date'),
     Input('indicators-dropdown', 'value')])
def set_image_options(date, selected_indicator):
    if date is not None:
        date = date[:10]
    #module = [name for name in glob(selected_indicator+".py")]
    return str("assets/"+date+"_"+selected_indicator + ".png")

# @app.callback(
#     Output('cities-dropdown', 'options'),
#     [Input('countries-dropdown', 'value')])
# def set_cities_options(selected_country):
#     #modules =[name[:-3] for name in glob("i*.py")] #i.e.i01_10MSMASPY.py
#     #modules.sort()
#     #return modules
#     return [{'label': i, 'value': i} for i in glob("i*.py")]


# @app.callback(
#     Output('cities-dropdown', 'value'),
#     [Input('cities-dropdown', 'options')])
# def set_cities_value(available_options):
#     return available_options[0]['value']


# @app.callback(
#     Output('display-selected-values', 'children'),
#     [Input('countries-dropdown', 'value'),
#      Input('cities-dropdown', 'value')])
# def set_display_children(selected_country, selected_city):
#     return u'{} is a city in {}'.format(
#         selected_city, selected_country,
#     )


if __name__ == '__main__':
    # BEGIN MAIN CODE FROM Main_Indicators.py
    #modules =[name[:-3] for name in glob("i*.py")] #i.e.i01_10MSMASPY.py
    #modules.sort()
    #allIndicators(modules, date)
    # END MAIN CODE FROM Main_Indicators.py
    print("##### START app.run_server #####")
    app.run_server(debug=True)
