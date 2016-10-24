import urllib
import urllib2
import re
import json
import argparse
import sys
import datetime
from HTMLParser import HTMLParser

"""

Parses the HTML to find a list of the rows of the table and the name of the city/state
"""
class CustomParser(HTMLParser):

    def __init__(self,col_names =['name','actual','mean','record']):
        HTMLParser.__init__(self)
        self.table_found=False
        self.row_found=False
        self.data_found=False
        self.search_city=False
        self.rows=[]
        self.col_names=col_names
        self.city=None
    def handle_starttag(self, tag, attrs):
        #Look for heading to find the city
        if tag=='h2':
            for attr,val in attrs:
                if val=="city-nav-header is-parent" and attr=="class":
                    self.search_city=True
        #Look through the table to find the entries
        if self.table_found:
            if tag=="tr":
                self.iter=iter(self.col_names)
                self.row_found=True
                self.row={}
            if tag=="td" and self.row_found:
                self.data_found=True
                self.value=self.iter.next()
        #Search for the table to make sure it is the correct data entries
        if tag=="table":
            for attr,val in attrs:
                if val=="historyTable" and attr=="id":
                    self.table_found=True

    def handle_endtag(self, tag):
        #Exit the table
        if tag=="table":
            self.table_found=False
        #Update the row in the list
        if tag=="tr":
            #If this row has any meaningful data
            if self.row:
                #Look through in fill in any missing columns
                for col in self.col_names:
                    #If the column is a record seperate the record and year for the JSON
                    if col=='record' and col in self.row:
                        t,y=self.row[col].split('\n')
                        self.row[col]={"temp":t,"year":y.strip('()')}
                    #Else if it does not exist then add it a null value
                    if col not in self.row:
                        self.row[col]="-"
                self.rows.append(self.row)
            #Add row to list
            self.row_found=False
            self.row={}
        #Stop searching for column
        if tag=="td":
            self.data_found=False

    def handle_data(self, data):
        #When data is found check if searching for city or tabluar data
        if self.search_city==True:
            #Get the city name
            self.city=data.strip()
            self.search_city=False
        #Search through tables
        if self.data_found:
            #Look at the current column and add the data
            if self.value in self.row:
                self.row[self.value]=self.row[self.value]+data
            else:
                #Incase there is multiple tags in the table entry keep on adding
                self.row[self.value]=data+" "
            #Format the entry to stay tidy
            self.row[self.value]=self.row[self.value].strip()


def scrape(city,state,day,month,year,dest="output",output="file"):

    today=datetime.date.today()
    first_date=datetime.date(1956, 1, 1)
    #Check args
    if (not day==None) and (not month==None) and (not year==None):
            try:
                test_date=datetime.date(int(year),int(month),int(day))
            except ValueError as e:
                return 'Enter A Valid Date'
            if test_date>today:
                return "Enter date before today"
            if first_date>test_date:
                return 'This Date is invalid pick date after 1/1/1956'
    else:
        return 'Enter A Valid Date'
    if city==None or state==None:
        return 'Enter A Valid City and State'

    formURL="https://www.wunderground.com/history/cgi-bin/findweather/getForecast?"

    #Build Request
    code =  city+", "+state
    month=month
    day=day
    year=year
    data = {
            "code" : code,
            "month":month,
            "day": day,
            "year":year,
            "airportorwmo":"query",
            "historytype":"DailyHistory",
            "backurl":"/history/index.html"
           }
    #Encode the request to HTTP Post
    encoded_post=urllib.urlencode(data)
    request=urllib2.Request(formURL,encoded_post)
    #Send Request and get response
    response=urllib2.urlopen(request)
    html=response.read()

    #Setup custom HTML Parser
    html_parser=CustomParser()
    html_parser.feed(html)

    #Check if city is correct
    check_city=re.compile("^\s*"+city+"\s*,\s*"+state+"\s*$",re.I)
    if html_parser.city and not check_city.match(html_parser.city):
        return 'Either the city does not exist in the database or it was incorrectly entered'
    elif not html_parser.city:
        return 'Either the city does not exist in the database or it was incorrectly entered'
    #Write Regex to determine if the row is referencing the Temperature
    check_temp=re.compile("^(Mean|Max|Min) Temperature\s*$")
    parsed={x['name']:{y:x[y] for y in x if not y=='name'} for x in html_parser.rows if check_temp.match(x['name'])}
    data={"Location":city,"Day":day,"Year":year,"Month":month,"Data":parsed}
    jsonoutput=json.dumps(data)

    #Write To Output, Right now only a file
    if output=="file" and not dest==None:
        with open(dest,'w+') as f:
            f.write(jsonoutput)
            return "Good"
    elif output=='func':
        return jsonoutput
    else:
        return "Pick a valid output method"


#Main Execution
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='wunderground.com temperature scrapper')
    parser.add_argument('-c', action="store",dest='city',help='City of lookup')
    parser.add_argument('-s', action="store",dest='state',help='State the city is in, use state code, ie. GA, NY')
    parser.add_argument('-d', action="store",dest='day',help="Day of month")
    parser.add_argument('-m', action="store",dest='month',help="Month of year, use numerical values from 1-12")
    parser.add_argument('-y', action="store",dest='year',help="The year")
    parser.add_argument('-f', action="store",dest='dest',default="output",help="Destination for Json output ")
    parser.add_argument('-o', action="store",dest='output',default="file",help="How to output the Json")
    args= parser.parse_args(sys.argv[1:])
    print scrape(args.city,args.state,args.day,args.month,args.year,args.dest,args.output)
