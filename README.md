# Get Meteo Data

## Requirements
Python 3.7  
Internet Access

## Description
This project aims to retreive all the historical data between two dates. The result is copied in a csv file in the folder specified. Currently the program only grab data from internet (via https://www.historique-meteo.net/france) for France by using scraping methods. However it can be extended to get meteo informations from other countries as the web site manage many countries. 

Note: Even if the web site proposes data by using the old region breakdown, the result is automatically stored by using the new French regions:  

<B>Region list: </b> 
'Île-de-France', 'Nouvelle-Aquitaine', 'Auvergne-Rhône-Alpes', 'Bourgogne-Franche-Comté', 'Hauts-de-France', 'Grand Est', 'Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte', 'Centre-Val de Loire', 'Normandie', 'Pays de la Loire', 'Bretagne', 'Occitanie', "Provence-Alpes-Côte d'Azur", 'Corse' 

## Run the program
Run the command line:  
```
python GetFRMeteoData.py -s <Starting Date> -e <Ending Date> -f <Destination Folder> 
```

Here are the input parameter description:  
-s : Starting/From date  
-e : Ending/To date  
-f : Destination Folder  

## Result
The result is stored in a csv file (in the input folder) with that format:  

* Index: Row index (concat of Region and day)  
* TempMax_Deg: Maximum Temperature of the day in Celcius degree  
* TempMin_Deg: Minimum Temperature of the day in Celcius degree  
* Wind_kmh: Wind speed (km/h)  
* Wet_percent: Wet in (%)  
* Visibility_km: Visibility (km)  
* CloudCoverage_percent: Cloud coverage (%)  
* Dayduration_hour: Day/sun duration (min)  
* region: Region (France new breakdown)  
* day: Day in format YYYY/MM/DD  
