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
import time
from random import randint


class scrape_flights(object):
    def __init__(self, origin=None, destination=None, roundtrip=True):
        self.origins = origin
        self.dests = destination
        self.roundtrip = roundtrip
        self.data = None

        origin_list = []
        if type(self.origins) is dict:
            for value in self.origins.values():
                origin_list.append(value)
        elif type(self.origins) is str:
            origin_list.append(self.origins)
        elif type(self.origins) is list:
            origin_list = self.origins
        else:
            raise Exception(
                "Please supply a dictionary, list, or string as the origin")

        dest_list = []
        if type(self.dests) is dict:
            for value in self.dests.values():
                dest_list.append(value)
        elif type(self.dests) is str:
            dest_list.append(self.dests)
        elif type(self.dests) is list:
            dest_list = self.dests
        else:
            raise Exception(
                "Please supply a dictionary, list, or string as the destination"
            )

        self.origins = [x.upper() for x in origin_list]
        self.dests = [x.upper() for x in dest_list]

        cart_product = []
        for i in itertools.product(self.origins, self.dests):
            cart_product.append(i)
        self.data = pd.DataFrame(
            cart_product, columns=["origin", "destination"])
        self.data["merge"] = 1

    def datetimes(
            self,
            dep_datetime_earliest=None,
            return_datetime_latest=None,
            min_trip_duration=None,
            max_trip_duration=None):
        # Add Dates and Times to self.data!
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
        dep_datetime_earliest = parse(dep_datetime_earliest)
        return_datetime_latest = parse(return_datetime_latest)
        diff = return_datetime_latest - dep_datetime_earliest
        first_day = dep_datetime_earliest.date()
        last_day = return_datetime_latest.date()
        first_day_time = dep_datetime_earliest.time()
        last_day_time = return_datetime_latest.time()

        # print("Earliest departure:", str(dep_datetime_earliest))
        # print("Latest return:"     , str(return_datetime_latest))
        # print(" ")

        if diff.total_seconds() < 0:
            raise Exception(
                "Return datetime cannot be before departure datetime")

        if min_trip_duration is None:
            min_trip_duration = 0

        if max_trip_duration is None or max_trip_duration > diff.days:
            max_trip_duration = diff.days

        if diff.days < min_trip_duration:
            raise Exception(
                "Minimum trip duration must be at least as long as the difference in days between earliest start and latest return"
            )

        # First get all possible combinations of departure and return days,
        #  and then find the subset that matches min and max trip duration
        dep_list = pd.date_range(first_day, periods=diff.days).date.tolist()
        ret_list = pd.date_range(
            last_day - datetime.timedelta(days=diff.days - 1),
            periods=diff.days).date.tolist()

        cart_product = []
        for i in itertools.product(dep_list, ret_list):
            cart_product.append(i)

        date_pairs = pd.DataFrame(
            cart_product, columns=["dep_date", "ret_date"])
        date_pairs = date_pairs[date_pairs.ret_date - date_pairs.dep_date <=
                                datetime.timedelta(days=max_trip_duration)]
        date_pairs = date_pairs[date_pairs.ret_date - date_pairs.dep_date >=
                                datetime.timedelta(days=min_trip_duration)]

        # Now add on dep_time and ret_time if first or last day
        date_pairs.loc[date_pairs.dep_date == first_day,
                       "dep_time"] = first_day_time
        date_pairs.loc[date_pairs.ret_date == last_day,
                       "ret_time"] = last_day_time
        # date_pairs["duration"] = date_pairs.ret_date - date_pairs.dep_date
        date_pairs["merge"] = 1

        self.data = pd.merge(self.data, date_pairs, on="merge")

    # def holiday_dates(self,
    #                   holiday_date = None,
    #                   max_days_off_work = None,
    #                   min_trip_duration = None,
    #                   max_trip_duration = None):
    #     # if self.holiday_date.weekday() >= 5:
    #     #     print("You supplied a weekend as a holiday")
    #
    #
    # def flight_duration(self,
    #                     max_flight_duration = None,
    #                     max_flight_duration_outbound = None,
    #                     max_flight_duration_inbound = None):
    #
    # def other_options(self,
    #                   max_stops = None,
    #                   max_price = None,
    #                   airline_included = None,
    #                   airline_excluded = None,
    #                   allow_separate_tickets = True,
    #                   connect_airport_included = None,
    #                   connect_airport_excluded = None):
    #
    # def specify_times(self,
    #                   time_outbound_dep_begin = None,
    #                   time_outbound_dep_end = None,
    #                   time_outbound_arr_begin = None,
    #                   time_outbound_arr_end = None,
    #                   time_inbound_dep_begin = None,
    #                   time_inbound_dep_end = None,
    #                   time_inbound_arr_begin = None,
    #                   time_inbound_arr_end = None):
    #
    def make_url(self):

        self.data["url_dep"] = "https://www.google.com/flights/#search"
        self.data[
            "url_dep"] = self.data["url_dep"] + ";f=" + self.data["origin"]
        self.data[
            "url_dep"] = self.data["url_dep"] + ";t=" + self.data["destination"]
        self.data["url_dep"] = self.data["url_dep"] + ";d=" + self.data[
            "dep_date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        self.data["url_dep"] = self.data["url_dep"] + ";tt=o;eo=e"

        self.data["url_ret"] = "https://www.google.com/flights/#search"
        self.data[
            "url_ret"] = self.data["url_ret"] + ";f=" + self.data["destination"]
        self.data[
            "url_ret"] = self.data["url_ret"] + ";t=" + self.data["origin"]
        self.data["url_ret"] = self.data["url_ret"] + ";d=" + self.data[
            "ret_date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        self.data["url_ret"] = self.data["url_ret"] + ";tt=o;eo=e"

    def scrape(self, scrape_wait_time=5, scrape_engine="chromedriver"):

        if scrape_engine == "chromedriver":
            driver = webdriver.Chrome("../bin/chromedriver")
        elif scrape_engine == "phantomjs":
            driver = webdriver.PhantomJS("/opt/phantomjs/bin/phantomjs")
        else:
            raise Exception("You must use Chromedriver or PhantomJS")

        flights_list = []
        scrape_time = str(datetime.datetime.now())[:-7]

        for i in range(len(self.data)):
            time.sleep(randint(3, 7))
            driver.get(self.data["url_dep"][i])
            soup_dep = BeautifulSoup(driver.page_source, "lxml")
            time.sleep(randint(3, 7))
            driver.get(self.data["url_ret"][i])
            soup_ret = BeautifulSoup(driver.page_source, "lxml")

            # flights_list = []
            # for flight in soup_dep.find_all("a", class_=re.compile("OMOBOQD-d-X")):
            for flight in soup_dep.find_all("a", elm="il"):
                dict = {
                    "dep_href":
                        flight.get("href"),
                    "dep_price":
                        flight.find(class_="OMOBOQD-d-Ab").get_text(),
                    "dep_oneway":
                        flight.find(class_="OMOBOQD-d-Cb").get_text(),
                    "dep_airline_icon":
                        flight.find(class_="OMOBOQD-d-i").get("src"),
                    "dep_departure":
                        flight.find(class_="OMOBOQD-d-Zb").span.get("tooltip"),
                    "dep_arrival":
                        flight.find(class_="OMOBOQD-d-Zb")
                        .span.find_next_sibling("span").get("tooltip"),
                    "dep_airline_text":
                        flight.find(class_="OMOBOQD-d-j").span.get_text(),
                    "dep_duration":
                        flight.find(class_="OMOBOQD-d-E").get_text(),
                    "dep_number_of_stops":
                        flight.find(class_="OMOBOQD-d-Qb").get_text(),
                    "scrape_time":
                        scrape_time,
                    "id":
                        i}
                if flight.find(
                        class_="OMOBOQD-d-Qb").get_text().lower() != "nonstop":
                    dict["dep_layover_info"] = flight.find(
                        class_="OMOBOQD-d-Z").get_text()
                try:
                    dict["dep_wifi"] = flight.find(
                        class_="OMOBOQD-d-jc").get("tooltip"),
                except AttributeError:
                    pass
                flights_list.append(dict)

            # for flight in soup_ret.find_all("a", class_=re.compile("OMOBOQD-d-X")):
            for flight in soup_ret.find_all("a", elm="il"):
                dict = {
                    "ret_href":
                        flight.get("href"),
                    "ret_price":
                        flight.find(class_="OMOBOQD-d-Ab").get_text(),
                    "ret_oneway":
                        flight.find(class_="OMOBOQD-d-Cb").get_text(),
                    "ret_airline_icon":
                        flight.find(class_="OMOBOQD-d-i").get("src"),
                    "ret_departure":
                        flight.find(class_="OMOBOQD-d-Zb").span.get("tooltip"),
                    "ret_arrival":
                        flight.find(class_="OMOBOQD-d-Zb")
                        .span.find_next_sibling("span").get("tooltip"),
                    "ret_airline_text":
                        flight.find(class_="OMOBOQD-d-j").span.get_text(),
                    "ret_duration":
                        flight.find(class_="OMOBOQD-d-E").get_text(),
                    "ret_number_of_stops":
                        flight.find(class_="OMOBOQD-d-Qb").get_text(),
                    "scrape_time":
                        scrape_time,
                    "id":
                        i}
                if flight.find(
                        class_="OMOBOQD-d-Qb").get_text().lower() != "nonstop":
                    dict["ret_layover_info"] = flight.find(
                        class_="OMOBOQD-d-Z").get_text()
                try:
                    dict["ret_wifi"] = flight.find(
                        class_="OMOBOQD-d-jc").get("tooltip"),
                except AttributeError:
                    pass
                flights_list.append(dict)

            #
            # temp_df = pd.DataFrame(flights_list)
            # flights_df.append(temp_df)

        flights_df = pd.DataFrame(flights_list)
        return flights_df




test = scrape_flights(origin = "bos", destination = ["LAX", "SEA"])
test.datetimes("July 20 10:00 am", "July 22 5:00 pm")
test.make_url()
flights = test.scrape()

test.data


airports = feather.read_dataframe("../data/airports.feather")
flights

test.data["url_ret"][0]

flight.find(class_= "OMOBOQD-d-Ab").get_text()


soup_ret.get_text

flight
soup_ret.find_all("a", elm = "il")

new_driver = webdriver.Chrome("../bin/chromedriver")

new_driver.get("https://www.google.com/flights/#search;f=LAX;t=BOS;d=2017-07-21;tt=o;eo=e")
soup_ret = BeautifulSoup(new_driver.page_source, "lxml")

for flight in soup_ret.find_all("a", elm = "il"):
    print(flight)

soup_ret.find_all("a", elm = "il")

flights
