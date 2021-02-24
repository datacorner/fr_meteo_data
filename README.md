# Get Meteo Data

## Requirements
If you want to use the program you'll need:  
* Python 3.7  
* Internet Access  

And if you don't want to use it, so ... just download the data in the /data directory ;-)

## Description
This project aims to retreive all the historical data between two dates. The result is copied in a csv file in the folder specified. Currently the program only grab data from internet (via https://www.historique-meteo.net/france) for France by using scraping methods. However it can be extended to get meteo informations from other countries as the web site manage many countries. 

Note: The result is by default stored using the old French regions.  

The old region to new region can be launch by running a second command line (conversion). The new regions are the ones below:  

<B>Region list: </b> 
'Île-de-France', 'Nouvelle-Aquitaine', 'Auvergne-Rhône-Alpes', 'Bourgogne-Franche-Comté', 'Hauts-de-France', 'Grand Est', 'Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte', 'Centre-Val de Loire', 'Normandie', 'Pays de la Loire', 'Bretagne', 'Occitanie', "Provence-Alpes-Côte d'Azur", 'Corse' 

## Command line details

### Run the command line for collecting data:  
```
python GetFRMeteoData.py -a collect -s <Starting Date> -e <Ending Date> -f <Destination Folder> 
```

Here are the input parameter description:  
-a : action (collect here)
-s : Starting/From date  
-e : Ending/To date  
-f : Destination Folder  

### Run the command line for conversion (Old to new regions) data:  
```
python GetFRMeteoData.py -a convert -i <input file> -o <output file> 
```

Here are the input parameter description:  
-a : action (convert here)
-i : input file  
-o : output file  

## Result
The result is stored in a csv file (in the input folder) with that format:  

* <B>Index:</b> Row index (concat of Region and day)  
* <B>TempMax_Deg:</b> Maximum Temperature of the day in Celcius degree  
* <B>TempMin_Deg:</b> Minimum Temperature of the day in Celcius degree  
* <B>Wind_kmh:</b> Wind speed (km/h)  
* <B>Wet_percent:</b> Wet in (%)  
* <B>Visibility_km:</b> Visibility (km)  
* <B>CloudCoverage_percent:</b> Cloud coverage (%)  
* <B>Dayduration_hour:</b> Day/sun duration (min)  
* <B>region:</b> Region 
* <B>day:</b> Day in format YYYY/MM/DD 

