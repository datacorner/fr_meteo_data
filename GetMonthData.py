import pandas as pd
import numpy as np
import requests
import lxml.html as lh
from datetime import datetime, timedelta

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

def getXPath(_rowidx = 1, _colidx = 4):
  return '//*[@id="content"]/div/div/div[1]/table/tbody/tr['+  str(_rowidx) + ']/td['+  str(_colidx) + ']'

# Get one feature into the web page
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
  for label in labels:
    val = getOneMeteoFeature(doc, table, label)
    dataset[label][_region] = getValue(val)
  return dataset

# Return the meteo data for 1 day / all region
def getAllRegionByDay(_day):
  all_day_dataset = pd.DataFrame()
  # go through all regions
  print ("  - Regions: ", end='')
  for region in regions:
    print (".", end='')
    dataframe_region = get1RegionMeteoByDay(region, _day)
    all_day_dataset = pd.concat([all_day_dataset, dataframe_region])
  print ("")
  # reformat dataset
  all_day_dataset.columns = ['TempMax_Deg',
                            'TempMin_Deg',
                            'Wind_kmh',
                            'Wet_percent',
                            'Visibility_km',
                            'CloudCoverage_percent',
                            'Dayduration_hour']
  all_day_dataset['day'] = _day
  return all_day_dataset

def GetMonthData(month):
  current_day = datetime.strptime(month + "/01", "%Y/%m/%d")
  current_month = current_day.month
  ds_month = pd.DataFrame()
  end_of_month = False

  while not end_of_month:
    if (current_day.month != current_month):
      end_of_month = True
    else:
      # Grab meteo information for that day
      day = current_day.strftime("%Y/%m/%d")
      print("> Day:", day)
      ds_one_day = getAllRegionByDay(day)
      ds_month = pd.concat([ds_month, ds_one_day])
    current_day = current_day + timedelta(days=1)
  ds_month.to_csv('./data/By Month (old FR regions)/' + month.replace('/', '-') + '.csv')
