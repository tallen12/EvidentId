# EvidentId
The webscaper for the coding Assignment referenced in the emailed PDF. Scrapes https://www.wunderground.com/history by taking in the city and date at the command line and outputs a file containg the JSON representation of the temperature table. 

The command line interface flags are such:

-c:City of lookup

-s:State the city is in, use state code, ie. GA, NY

-d:Day of month

-m:Month of year, use numerical values from 1-12

-y:The year using all four digits

If one of the flags is not set or entered incorrectly the program will output an error message, and produce an output. 

