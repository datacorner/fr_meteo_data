import pandas as pd
import numpy as np
import requests
import lxml.html as lh
from datetime import datetime, timedelta
import sys
import getopt

urlbase= "https://www.historique-meteo.net/france"
labels = ['TempÃ©rature maximale',
          'TempÃ©rature minimale',
          'Vitesse du vent',
          'HumiditÃ©',
          'VisibilitÃ©',
          'Couverture nuageuse',
          'DurÃ©e du jour']
regions = ['alsace',
            'aquitaine',
            'ardeche',
            'auvergne',
            'bourgogne',
            'bretagne',
            'centre',
            'champagne-ardenne',
            'corse',
            'franche-comte',
            'ile-de-re',
            'ile-de-france',
            'languedoc-roussillon',
            'limousin',
            'lorraine',
            'midi-pyrenees',
            'nord-pas-de-calais',
            'normandie',
            'pays-de-la-loire',
            'picardie',
            'poitou-charentes',
            'rh-ne-alpes',
            'provence-alpes-c-te-d-azur']

def getValue(_val):
  try:
    myval = _val.replace('Â', '').replace('°', '').replace('%', '').replace('km/h', '').replace('mm', '').replace('km', '')
    return myval
  except:
    return np.nan

def getSunTimeInSec(_val):
  try:
    vals = _val.split(':')
    return int(vals[2]) + int(vals[1]) * 60 +  int(vals[0]) * 60 * 60
  except:
    return np.nan

# Return the text value from an XPath
def getValueFromXPath(doc, _xpath):
  try:
    value = doc.xpath(_xpath)
    myval = value[0].text_content().strip()
    return myval
  except:
    return "Error"

# Get the XPath infor for the XPath reference
def getXPath(_rowidx = 1, _colidx = 4):
  return '//*[@id="content"]/div/div/div[1]/table/tbody/tr['+  str(_rowidx) + ']/td['+  str(_colidx) + ']'

# Get one feature into the web page by XPath search
def getOneMeteoFeature(_doc, _table, _feature):
  featureValue = ""
  row = 1
  endOfTable = False
  while (not endOfTable):
    label = getValueFromXPath(_doc, getXPath(row, 1))
    if (label == _feature):
      featureValue = getValueFromXPath(_doc, getXPath(row, 4) + '/b')
      break
    row = row + 1
    if ((row > len(labels)+2) or (label == 'Error')): endOfTable = True
  return featureValue

# Return the meteo data for 1 day / 1 region
def get1RegionMeteoByDay(_region, _day):
  url = urlbase + '/' + _region + '/' + _day
  #print ("Get data from: ", url)
  page = requests.get(url)
  doc = lh.fromstring(page.content)
  table = 2
  dataset = pd.DataFrame(columns=labels, index=[_region])
  # Loop with all the required labels to grab their data
  for label in labels:
    val = getOneMeteoFeature(doc, table, label)
    dataset[label][_region] = getValue(val)
  return dataset

# Return the meteo data for 1 day for all region
# _day : day to retrieve meteo (format YYYY/MM/DD)
def getAllRegionByDay(_day):
  all_day_dataset = pd.DataFrame()
  print (f"Grab Meteo Data for {_day}")
  # Loop through all regions and get their meteo data per day
  for region in regions:
    print (".", end='')
    dataframe_region = get1RegionMeteoByDay(region, _day)
    all_day_dataset = pd.concat([all_day_dataset, dataframe_region])
  print ("")
  # reformat dataset columns names
  all_day_dataset.columns = ['TempMax_Deg',
                            'TempMin_Deg',
                            'Wind_kmh',
                            'Wet_percent',
                            'Visibility_km',
                            'CloudCoverage_percent',
                            'Dayduration_hour']
  all_day_dataset['day'] = _day
  return all_day_dataset

def GetMeteoData(_start, _End, _Folder):
    ds = pd.DataFrame()
    end_of_loop = False
    
    # Convert in datetime
    start = datetime.strptime(_start, "%Y/%m/%d")
    end = datetime.strptime(_End, "%Y/%m/%d")
    filename = "MeteoFR_" + _start.replace('/', '-') + "_" + _End.replace('/', '-') + ".csv"
    
    # Loop from start date to end
    while (start <= end):
        ds_one_day = getAllRegionByDay(start.strftime("%Y/%m/%d"))
        ds = pd.concat([ds, ds_one_day])
        start = start + timedelta(days=1)
    
    print (f"Store results in {_Folder + filename}")
    ds.to_csv(_Folder + filename)
    
# Main function
def main():
    # Manage arguments
    starDate, endDate, targetFolder = '', '', ''
    try:
        argv = sys.argv[1:]
        print(argv)
        opts, args = getopt.getopt(argv , "s:e:f:")
    except getopt.GetoptError:
         print ('Error. Usage is GetFRMeteoData.py -s <Start Date> -e <End Date> -f <Target Folder>')
         sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
           print ('Usage is GetFRMeteoData.py -s <Start Date> -e <End Date> -f <Target Folder>')
       elif opt in ["-s"]:
           starDate = arg.strip()
       elif opt in ["-e"]:
           endDate = arg.strip()
       elif opt in ["-f"]:
           targetFolder = arg.strip()
    print (f"Starting Date: <{starDate}>")
    print (f"End Date Date: <{endDate}>")
    print (f"Target Folder: <{targetFolder}>")

    # Launch Meteo gathering
    GetMeteoData(starDate, endDate, targetFolder)

if __name__ == "__main__":
    main()
