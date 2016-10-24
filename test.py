import webscraper

tests=[(["Atlanta", "GA", "10","23","1950"],'This Date is invalid pick date after 1/1/1956'),
 (["Atlanta", "GA", "10","23","2017"],"Enter date before today"),
 (["Atlanta", "GA", "10","23","None"],'Enter A Valid Date'),
 (["Atlanta", "GA", "10","None","2016"],'Enter A Valid Date'),
 (["Atlanta", "GA", "None","23","2016"],'Enter A Valid Date'),
 (["Atlanta", "GA", "10","23",None],'Enter A Valid Date'),
 (["Atlanta", "GA", "10",None,"2016"],'Enter A Valid Date'),
 (["Atlanta", "GA", None,"23","2016"],'Enter A Valid Date'),
 ([None, "GA", "10","23","2016"],'Enter A Valid City and State'),
 (["Atlanta", None, "10","23","2016"],'Enter A Valid City and State'),
 (["Atlanta", "NY", "10","23","2016"],'Either the city does not exist in the database or it was incorrectly entered'),
 (["New York", "GA","10","23","2016"],'Either the city does not exist in the database or it was incorrectly entered'),
 (["None", "NY", "10","23","2016"],'Either the city does not exist in the database or it was incorrectly entered'),
 (["New York", "None","10","23","2016"],'Either the city does not exist in the database or it was incorrectly entered')]

args=["-c","-s","-m","-d","-y"]
for t,r in tests:
    print t
    assert webscraper.scrape(t[0],t[1],t[3],t[2],t[4])==r
