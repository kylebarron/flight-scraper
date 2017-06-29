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
import itertools


class scrape_flights(object):
    def __init__(self,
                 origin      = None,
                 destination = None,
                 roundtrip   = True):
        self.origins   = origin
        self.dests     = destination
        self.roundtrip = roundtrip
        self.data      = None

        origin_list = []
        if type(self.origins) is dict:
            for value in self.origins.values():
                origin_list.append(value)
        elif type(self.origins) is str:
            origin_list.append(self.origins)
        elif type(self.origins) is list:
            origin_list = self.origins
        else:
            raise Exception("Please supply a dictionary, list, or string as the origin")
        self.origins = origin_list

        dest_list = []
        if type(self.dests) is dict:
            for value in self.dests.values():
                dest_list.append(value)
        elif type(self.dests) is str:
            dest_list.append(self.dests)
        elif type(self.dests) is list:
            dest_list = self.dests
        else:
            raise Exception("Please supply a dictionary, list, or string as the destination")
        self.dests = dest_list

        cart_product = []
        for i in itertools.product(self.origins, self.dests):
            cart_product.append(i)
        self.data = pd.DataFrame(cart_product, columns = ["Origin", "Destination"])
        self.data["merge"] = 1


    def datetimes(self,
                  dep_datetime_earliest  = None,
                  return_datetime_latest = None,
                  min_trip_duration      = None,
                  max_trip_duration      = None):
        # For testing:
        # dep_datetime_earliest  = "July 20 10:00 am"
        # return_datetime_latest = "July 25 5:00 pm"
        # min_trip_duration      = 1
        # max_trip_duration      = 4
        """
        Easiest implementation : parse a beginning and end datetime and a min or max trip duration
        dep_datetime_earliest  : String
        return_datetime_latest : String
        min_trip_duration      : Shortest trip length in days, integer
        max_trip_duration      : Longest trip length in days, integer
        OUTPUT: Pandas dataframe
        """
        dep_datetime_earliest  = parse(dep_datetime_earliest)
        return_datetime_latest = parse(return_datetime_latest)
        diff                   = return_datetime_latest - dep_datetime_earliest
        first_day              = dep_datetime_earliest.date()
        last_day               = return_datetime_latest.date()
        first_day_time         = dep_datetime_earliest.time()
        last_day_time          = return_datetime_latest.time()

        # print("Earliest departure:", str(dep_datetime_earliest))
        # print("Latest return:"     , str(return_datetime_latest))
        # print(" ")

        if diff.total_seconds() < 0:
            raise Exception("Return datetime cannot be before departure datetime")

        if diff.days < min_trip_duration:
            raise Exception("Minimum trip duration must be at least as long as the difference in days between earliest start and latest return")

        # First get all possible combinations of departure and return days,
        #  and then find the subset that matches min and max trip duration
        dep_list = pd.date_range(dep, periods = diff.days).date.tolist()
        ret_list = pd.date_range(ret - datetime.timedelta(days = diff.days - 1), periods = diff.days).date.tolist()

        cart_product = []
        for i in itertools.product(dep_list, ret_list):
            cart_product.append(i)

        date_pairs = pd.DataFrame(cart_product, columns=["dep_date", "ret_date"])
        date_pairs = date_pairs[date_pairs.ret_date - date_pairs.dep_date <= datetime.timedelta(days = max_trip_duration)]
        date_pairs = date_pairs[date_pairs.ret_date - date_pairs.dep_date >= datetime.timedelta(days = min_trip_duration)]

        # Now add on dep_time and ret_time if first or last day
        date_pairs.loc[date_pairs.dep_date == first_day, "dep_time"] = first_day_time
        date_pairs.loc[date_pairs.ret_date == last_day, "ret_time"]  = last_day_time
        # date_pairs["duration"] = date_pairs.ret_date - date_pairs.dep_date
        date_pairs["merge"] = 1

        self.data = pd.merge(self.data, date_pairs, on = "merge")

    # def



test = scrape_flights(origin = "BOS", destination = ["LAX", "SEA"])
test.datetimes("July 20 10:00 am", "July 25 5:00 pm")

test.data


x
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
            elif self.holiday_date.weekday() == 0:
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
