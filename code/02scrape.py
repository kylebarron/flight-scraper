# Write scraper to check flight prices at given locations
# I use airports.feather to get timezone data for all these airports

import pandas as pd
import feather
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
import calendar
import re
from dateutil.parser import parse


class scrape_flights(object):
    def __init__(self,
                 origins = None,
                 dests = None,
                 
                 roundtrip = True,
                 # Either specify dates
                 # ONE FUNCTION
                 dep_date_earliest = None,
                 return_date_latest = None, # dep_date_latest = None, return_date_earliest = None, Simplify my computations right now
                 min_trip_duration = None,
                 max_trip_duration = None,
                 # Or specify a holiday date and max_days_off_work
                 # ANOTHER FUNCTION TO RESOLVE DATES
                 holiday_date = None,
                 max_days_off_work = None,
                 # Other options
                 max_stops = 2,
                 max_price = None,
                 airline_included = None,
                 airline_excluded = None,
                 # Flight times
                 time_outbound_dep_begin = None,
                 time_outbound_dep_end = None,
                 time_outbound_arr_begin = None,
                 time_outbound_arr_end = None,
                 time_inbound_dep_begin = None,
                 time_inbound_dep_end = None,
                 time_inbound_arr_begin = None,
                 time_inbound_arr_end = None,
                 # Flight durations
                 max_flight_duration = None,
                 max_flight_duration_outbound = None,
                 max_flight_duration_inbound = None,
                 allow_separate_tickets = True,
                 connect_airport_included = None,
                 connect_airport_excluded = None,
                 # Scrape options
                 scrape_wait_time = 5,
                 scrape_engine = "chromedriver"):
        if origins is None:
            origins = {
                "Boston": "BOS",
                "Providence": "PVD"
            }
        if dests is None:
            dests = {
                "Seattle, WA": "SEA",
                "Portland, OR": "PDX"
            }
        self.origins                      = origins
        self.dests                        = dests
        self.roundtrip                    = roundtrip
        self.dep_date_earliest            = dep_date_earliest
        self.return_date_latest           = return_date_latest
        self.min_trip_duration            = min_trip_duration
        self.max_trip_duration            = max_trip_duration
        self.holiday_date                 = holiday_date
        self.max_days_off_work            = max_days_off_work
        self.max_stops                    = max_stops
        self.max_price                    = max_price
        self.airline_included             = airline_included
        self.airline_excluded             = airline_excluded
        self.time_outbound_dep_begin      = time_outbound_dep_begin
        self.time_outbound_dep_end        = time_outbound_dep_end
        self.time_outbound_arr_begin      = time_outbound_arr_begin
        self.time_outbound_arr_end        = time_outbound_arr_end
        self.time_inbound_dep_begin       = time_inbound_dep_begin
        self.time_inbound_dep_end         = time_inbound_dep_end
        self.time_inbound_arr_begin       = time_inbound_arr_begin
        self.time_inbound_arr_end         = time_inbound_arr_end
        self.max_flight_duration          = max_flight_duration
        self.max_flight_duration_outbound = max_flight_duration_outbound
        self.max_flight_duration_inbound  = max_flight_duration_inbound
        self.allow_separate_tickets       = allow_separate_tickets
        self.connect_airport_included     = connect_airport_included
        self.connect_airport_excluded     = connect_airport_excluded
        self.scrape_wait_time             = scrape_wait_time
        self.scrape_engine                = scrape_engine

    def resolve_dates(self):
        # Given inputs, create a list of possible departure/return combinations
        # I.e. [[Mon, Thu], [Mon, Wed]] (but with actual dates)
        # If specified dates are included, then use those
        if not self.dep_date_earliest and not self.return_date_latest:
            self.dep_date_earliest = parse(self.dep_date_earliest).date()
            self.return_date_latest = parse(self.return_date_latest).date()
            if not self.max_trip_duration:
                d
            if not self.min_trip_duration:
                d

        if not self.holiday_date and not self.max_days_off_work:
            self.holiday_date = parse(self.holiday_date).date()
            if self.holiday_date.weekday() >= 5:
                print("You supplied a weekend as a holiday")
            else if self.holiday_date.weekday() == 0:
                self.dep_date_earliest = self.holiday_date - datetime.timedelta(days = 3)
            if not self.max_trip_duration:
            if not self.min_trip_duration:



dep = parse("August 24, 2017").date()
ret = parse("August 29, 2017").date()

dep


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


driver = webdriver.PhantomJS("/opt/phantomjs/bin/phantomjs")
driver = webdriver.Chrome("../bin/chromedriver")
scrape_time = str(datetime.datetime.now())[:-7]

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
