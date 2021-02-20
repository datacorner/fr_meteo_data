# Description
This project aims to retreive all the historical data between two dates.  
Run the command line:  
python GetFRMeteoData.py -s 2020/02/01 -e 2020/02/01 -f /home/benoit/temp/  

-s : starting date  
-e : end date  
-f : Folder  

#Result
The result is stored in a csv file (in the input folder) with that format:  

Index: Row index (concat of Region and day)  
TempMax_Deg: Maximum Temperature of the day in Celcius degree  
TempMin_Deg: Minimum Temperature of the day in Celcius degree  
Wind_kmh: Wind speed (km/h)  
Wet_percent: Wet in (%)  
Visibility_km: Visibility (km)  
CloudCoverage_percent: Cloud coverage (%)  
Dayduration_hour: Day/sun duration (min)  
region: Region (France new breakdown)  
day: Day in format YYYY/MM/DD  
