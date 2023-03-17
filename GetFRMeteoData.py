import pandas as pd
import numpy as np
import requests
import lxml.html as lh
from datetime import datetime, timedelta
import sys
import getopt
import locale

urlbase= "https://www.historique-meteo.net/france"

# Labels to grab
labels = ['TempÃ©rature maximale',
          'TempÃ©rature minimale',
          'Vitesse du vent',
          'HumiditÃ©',
          'VisibilitÃ©',
          'Couverture nuageuse',
          'DurÃ©e du jour']

# Old regions (but the web site refers to these regions
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

# New French regions breakdown
reg_target = ['Île-de-France', 'Nouvelle-Aquitaine', 'Auvergne-Rhône-Alpes',
       'Bourgogne-Franche-Comté', 'Hauts-de-France', 'Grand Est',
       'Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte',
       'Centre-Val de Loire', 'Normandie', 'Pays de la Loire', 'Bretagne',
       'Occitanie', "Provence-Alpes-Côte d'Azur", 'Corse']

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
    return np.nan

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
    index = _region + "_" + _day
    dataset = pd.DataFrame(columns=labels, index=[index])
    # Loop with all the required labels to grab their data
    for label in labels:
        val = getOneMeteoFeature(doc, table, label)
        dataset[label][index] = getValue(val)
    dataset['region'] = _region
    return dataset

# Return the meteo data for 1 day for all region
# _day : day to retrieve meteo (format YYYY/MM/DD)
def getAllRegionByDay(_day, _userRegion):
  all_day_dataset = pd.DataFrame()
  print (f"Grab Meteo Data for {_day}")
  
  # Loop through all regions and get their meteo data per day
  if _userRegion == "":
    # print (f"userRegion: <{_userRegion}>")
    for region in regions:
    #print (".", end='')
        try:
            dataframe_region = get1RegionMeteoByDay(region, _day)
            all_day_dataset = pd.concat([all_day_dataset, dataframe_region])
        except:
            print(f'Error while retreiving data for {region}, day {_day} | ', sys.exc_info()[0])    
  else: 
    # print (f"userRegion: <{_userRegion}>")
    try:
        dataframe_region = get1RegionMeteoByDay(_userRegion, _day)
        all_day_dataset = pd.concat([all_day_dataset, dataframe_region])
    except:
        print(f'Error while retreiving data for {region}, day {_day} | ', sys.exc_info()[0])  
    
    
  # reformat dataset columns names
  all_day_dataset.columns = ['TempMax_Deg',
                            'TempMin_Deg',
                            'Wind_kmh',
                            'Wet_percent',
                            'Visibility_km',
                            'CloudCoverage_percent',
                            'Dayduration_hour',
                            'region']
  all_day_dataset['day'] = _day
  return all_day_dataset

def GetMeteoData(_start, _End, _Folder, _userRegion):
    ds = pd.DataFrame()
    end_of_loop = False
    
    # Convert in datetime
    start = datetime.strptime(_start, "%Y/%m/%d")
    end = datetime.strptime(_End, "%Y/%m/%d")
    filename = "MeteoFR_region_" + _start.replace('/', '-') + "_" + _End.replace('/', '-') + ".csv"
    
    # Loop from start date to end
    while (start <= end):
        ds_one_day = getAllRegionByDay(start.strftime("%Y/%m/%d"), _userRegion)
        ds = pd.concat([ds, ds_one_day])
        start = start + timedelta(days=1)
    
    return filename, ds

# return the number of minutes in a time
def convTimeInMinute(_time):
  time = datetime.strptime(str(_time), "%H:%M:%S")
  return float(time.hour * 60 + time.minute)

# convert float and replace no numerical data by nan
# take care to convert by using locale (point or comma)
def defaultFloat(val):
    if str(val).isnumeric():
        return float(val.replace(".", locale.localconv()['decimal_point']))
    else:
        print ("> Error while converting " + str(val))
        return np.nan

# Convert Data to new regions
def convertRegionData(dataset, _userRegion):
    print ("Convert French Region with new ones")
    print ("convertRegionData> Columns to convert:", dataset.columns)
    
    # Effectively do the region mapping
    dataset['region'] = dataset['region'].map({'ile-de-france' : 'Île-de-France',
                                                     'limousin' : 'Nouvelle-Aquitaine',
                                                     'aquitaine' : 'Nouvelle-Aquitaine',
                                                     'poitou-charentes' : 'Nouvelle-Aquitaine',
                                                     '' : 'Auvergne-Rhône-Alpes',
                                                     'bourgogne' : 'Bourgogne-Franche-Comté',
                                                     'franche-comte' : 'Bourgogne-Franche-Comté',
                                                     'nord-pas-de-calais' : 'Hauts-de-France',
                                                     'picardie' : 'Hauts-de-France',
                                                     'alsace' : 'Grand Est',
                                                     'lorraine' : 'Grand Est',
                                                     '--' : 'Guadeloupe',
                                                     '--' : 'Martinique',
                                                     '--' : 'Guyane',
                                                     '--' : 'La Réunion',
                                                     '--' : 'Mayotte',
                                                     'centre' : 'Centre-Val de Loire',
                                                     'normandie' : 'Normandie',
                                                     'pays-de-la-loire' : 'Pays de la Loire',
                                                     'bretagne' : 'Bretagne',
                                                     'midi-pyrenees' : 'Occitanie',
                                                     'languedoc-roussillon' : 'Occitanie',
                                                     'provence-alpes-c-te-d-azur' : "Provence-Alpes-Côte d'Azur",
                                                     'corse' : 'Corse',
                                                     _userRegion : _userRegion
                                                    })
    
    print ("convertRegionData> Convert float data")
    # Convert in float to be able to group by
    ColumlToFloatConvert = ['TempMax_Deg',
                            'TempMin_Deg',
                            'Wind_kmh',
                            'Wet_percent',
                            'Visibility_km',
                            'CloudCoverage_percent']
    #for label in ColumlToFloatConvert:
    #    dataset[label] = [ defaultFloat(val) for val in dataset[label] ]
        #dataset[label] = dataset[label].astype(float, errors='ignore')
    
    print ("convertRegionData> Data converted in float")
    if _userRegion == "":
        dataset['Dayduration_Min'] = dataset['Dayduration_hour'].apply(convTimeInMinute)
    else:
        dataset['Dayduration_Min'] = 0  
    print ("convertRegionData> Dayduration_Min converted in minutes, new columns set: ", dataset.columns)
    # Now need to group the identical days (coming from the same region) to ensure no duplicates
    dataset = dataset.groupby(['region', 'day'], dropna=True).mean()
    
    print ("convertRegionData> Columns converted after grouping:", dataset.columns)
    
    return dataset

# Launch data gathering
def collectMeteoData(_starDate, _endDate, _targetFolder, _userRegion):
    print (f"Starting Date: <{_starDate}>")
    print (f"End Date Date: <{_endDate}>")
    print (f"Target Folder: <{_targetFolder}>")
    print (f"User Region: <{_userRegion}>")

    
    
    # Launch Meteo gathering
    try:
        filename, ds = GetMeteoData(_starDate, _endDate, _targetFolder, _userRegion)
        print (f"Store results in {_targetFolder + filename}")
        ds.to_csv(_targetFolder + "oldReg_" + filename)
    except:
        print("> Error while gathering meteo data. Error raised: ", sys.exc_info()[0])
        
# convert in new FR region
def convertMeteoDataInNewFRRegions(_userRegion, _sourcefile, _targetfile):
    print (f"Source file: <{_sourcefile}>")
    print (f"Target File: <{_targetfile}>")
    
    #try:
    dataset = pd.read_csv(_sourcefile)
    dataset_result = convertRegionData(dataset, _userRegion)
    dataset_result.to_csv(_targetfile)
    #except:
    #    print("> Impossible to convert Meteo data into new French Region. Error raised: ", sys.exc_info()[0])

def usage():
    print ('Meteo Gathering Usage is GetFRMeteoData.py -a collect -r <User Région overide : "région/city"> -s <Start Date> -e <End Date> -f <Target Folder>')
    print ('Meteo Fr New Region conversion Usage is GetFRMeteoData.py -a convert -r <User Region overide : "région/city"> -i <input file> -o <output file>')
    
# Main function
def main():
    # Manage arguments
    userRegion, starDate, endDate, targetFolder, inFile, outFile = '', '', '', '', '', ''
    action = "collect" # by default collect data
    
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv , "a:r:s:e:f:i:o:h")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            usage()
            return
        elif opt in ["-a"]:
            action = arg.strip()
        elif opt in ["-r"]:
            userRegion = arg.strip()
        elif opt in ["-s"]:
            starDate = arg.strip()
        elif opt in ["-e"]:
            endDate = arg.strip()
        elif opt in ["-f"]:
            targetFolder = arg.strip()
        elif opt in ["-i"]:
            inFile = arg.strip()
        elif opt in ["-o"]:
            outFile = arg.strip()
            
    print (f"Action to launch: <{action}>")
    
    #if bool(userRegion):
    #     # print (f"userRegion: <{userRegion}>")
    #     pass
    #else:
    #    userRegion = "Default"
    #    # print (f"userRegion: <{userRegion}>")
        
    if (action.capitalize() == "collect".capitalize()):
        collectMeteoData(starDate, endDate, targetFolder, userRegion)
        
    elif (action.capitalize() == "convert".capitalize()):
        convertMeteoDataInNewFRRegions(userRegion, inFile, outFile)
    

if __name__ == "__main__":
    main()
