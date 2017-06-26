# Write scraper to check flight prices at given locations
# I use airports.feather to get timezone data for all these airports

import pandas as pd
import feather
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
import re

airports = feather.read_dataframe("../data/airports.feather")

origins = {
    "Boston": "BOS",
    "Providence": "PVD"
}

dests = {
    # Washington:
    "Seattle, WA": "SEA",
    "Spokane, WA": "GEG",
    "Pullman": "PUW",
    "Bellingham": "BLI",
    "Wenatchee": "EAT",
    "Yakima": "YKM",
    "Pasco": "PSC",
    "Walla Walla": "ALW",
    # Oregon:
    "Portland, OR": "PDX",
    "Redmond, OR": "RDM",
    "Eugene, OR": "EUG",
    "Medford, OR": "MFR",
    # California:
    "Arcata": "ACV",
    "Redding": "RDD",
    "Santa Rosa": "STS",
    "Sacramento": "SMF",
    "San Francisco": "SFO",
    "Oakland": "OAK",
    "San Jose": "SJC",
    "Monterey": "MRY",
    "Fresno": "FAT",
    "San Luis Obispo": "SBP",
    "Santa Barbara": "SBA",
    "Los Angeles": "LAX",
    "Burbank": "BUR",
    "Ontario, CA": "ONT",
    "Long Beach": "LGB",
    "Orange County": "SNA",
    "Palm Springs": "PSP",
    "Yuma, CA": "YUM",
    # Arizona
    "Tucson": "TUS",
    "Phoenix": "PHX",
    "Prescott": "PRC",
    "Flagstaff": "FLG",
    "Bullhead City, AZ": "IFP",
    "Page, AZ": "PGA",
    # Nevada
    "Reno": "RNO",
    "Las Vegas": "LAS",
    "Elko": "EKO",
    # Utah
    "St. George, UT": "SGU",
    "Cedar City, UT": "CDC",
    "Salt Lake City": "SLC",
    # Idaho
    "Twin Falls": "TWF",
    "Pocatello": "PIH",
    "Idaho Falls": "IDA",
    "Sun Valley": "SUN",
    "Boise": "BOI",
    "Lewiston": "LWS",
    # Montana
    "Kalispell": "FCA",
    "Great Falls, MT": "GTF",
    "Missoula, MT": "MSO",
    "Helena": "HLN",
    "Bozeman": "BZN",
    "Butte": "BTM",
    # Wyoming
    "Jackson": "JAC",
    "Cody": "COD",
    # Colorado
    "Denver": "DEN",
    "Colorado Springs": "COS",
    "Grand Junction": "GJT",
    "Durango": "DRO",
    "Telluride": "TEX",
    "Montrose": "MTJ",
    "Gunnison": "GUC",
    "Aspen": "ASE",
    "Vail": "EGE",
    "Hayden": "HDN",
    "Pueblo": "PUB",
    # New Mexico
    "Santa Fe": "SAF",
    "Albuquerque": "ABQ",
    # Canada
    "Victoria": "YYJ",
    "Vancouver": "YVR",
    "Calgary": "YYC",
    # Alaska
    "Anchorage": "ANC"
}

departure_dates = [
    # Three day weekends plus one or two days off work
    # Labor day
    "2017-08-31", "2017-09-01", "2017-09-02",
    #
]

return_dates = [
    # Labor day

]

driver = webdriver.PhantomJS("/opt/phantomjs/bin/phantomjs")
# driver = webdriver.Chrome("../bin/chromedriver")
scrape_time = str(datetime.now())[:-7]

driver.get("https://www.google.com/flights/#search;f=SEA;t=BOS;d=2017-09-13;tt=o")
soup = BeautifulSoup(driver.page_source, "html.parser")

flight_data = []
for flight in soup.find_all("a", class_=re.compile("OMOBOQD-d-X")):
    dict = {
        "href": flight.get("href"),
        "price": flight.find(class_= "OMOBOQD-d-Ab").get_text(),
        "oneway": flight.find(class_= "OMOBOQD-d-Cb").get_text(),
        "airline_icon": flight.find(class_= "OMOBOQD-d-i").get("src"),
        "departure": flight.find(class_="OMOBOQD-d-Zb").span.get("tooltip"),
        "arrival": flight.find(class_="OMOBOQD-d-Zb").span.find_next_sibling("span").get("tooltip"),
        "airline_text": flight.find(class_="OMOBOQD-d-j").span.get_text(),
        "duration": flight.find(class_="OMOBOQD-d-E").get_text(),
        "number_of_stops": flight.find(class_="OMOBOQD-d-Qb").get_text(),
        "scrape_time": scrape_time
    }
    if flight.find(class_="OMOBOQD-d-Qb").get_text().lower() != "nonstop":
        dict["layover_info"] = flight.find(class_="OMOBOQD-d-Z").get_text()
    try:
        dict["wifi"] = flight.find(class_= "OMOBOQD-d-jc").get("tooltip"),
    except AttributeError:
        pass
    flight_data.append(dict)



dataframe = pd.DataFrame.from_dict(flight_data)
dataframe





















def scrape_flights:
    # INPUTS: Dictionaries for origins
    # Download flight data and put into pandas dataframe

https://www.kayak.com/flights/BOS-SEA/2017-07-13/2017-07-19


def parse_origins:

def parse_dests:

def parse_departure_dates:

def parse_return_dates:

test_dict = {"hi": 1,
             "hello": 2}

for i in test_dict.keys():
    print(i)


%whos
