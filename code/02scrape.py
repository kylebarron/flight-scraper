# Write scraper to check flight prices at given locations
# I use airports.feather to get timezone data for all these airports

import datetime
import feather
import itertools
import pandas as pd
import re
import time
from bs4                           import BeautifulSoup
from dateutil.parser               import parse
from random                        import randint
from selenium                      import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support    import expected_conditions as EC
from selenium.webdriver.common.by  import By
from selenium.common.exceptions    import TimeoutException

class scraper(object):
    def __init__(
        self,
        origin      = None,
        destination = None,
        roundtrip   = True,
        passengers  = 1):
        
        self.origins    = origin
        self.dests      = destination
        self.roundtrip  = roundtrip
        self.data       = None
        self.passengers = passengers

        origin_list = []
        if type(self.origins) is dict:
            for value in self.origins.values():
                origin_list.append(value)
        elif type(self.origins) is str:
            origin_list.append(self.origins)
        elif type(self.origins) is list:
            origin_list = self.origins
        else:
            raise Exception('Please supply a dictionary, list, or string as the origin')

        dest_list = []
        if type(self.dests) is dict:
            for value in self.dests.values():
                dest_list.append(value)
        elif type(self.dests) is str:
            dest_list.append(self.dests)
        elif type(self.dests) is list:
            dest_list = self.dests
        else:
            raise Exception('Please supply a dictionary, list, or string as the destination')

        self.origins = [x.upper() for x in origin_list]
        self.dests   = [x.upper() for x in dest_list]

        cart_product = []
        for i in itertools.product(self.origins, self.dests):
            cart_product.append(i)
        self.data = pd.DataFrame(cart_product, columns = ['origin', 'destination'])
        self.data['merge'] = 1

    def add_dates(
        self,
        dep_datetime_earliest  = None,
        return_datetime_latest = None,
        min_trip_duration      = 1,
        max_trip_duration      = None):
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

        if diff.total_seconds() < 0:
            raise Exception('Return datetime cannot be before departure datetime')

        if max_trip_duration is None or max_trip_duration > diff.days + 1:
            max_trip_duration = diff.days + 1

        if diff.days < min_trip_duration:
            raise Exception('Minimum trip duration is longer than the difference between earliest and latest possible dates.')

        # First get all possible combinations of departure and return days,
        #  and then find the subset that matches min and max trip duration
        dep_list = pd.date_range(first_day, periods = diff.days).date.tolist()
        ret_list = pd.date_range(last_day - datetime.timedelta(days = diff.days - 1), periods = diff.days).date.tolist()

        cart_product = []
        for i in itertools.product(dep_list, ret_list):
            cart_product.append(i)

        date_pairs = pd.DataFrame(cart_product, columns=['dep_date', 'ret_date'])
        date_pairs = date_pairs[date_pairs.ret_date - date_pairs.dep_date <= datetime.timedelta(days = max_trip_duration)]
        date_pairs = date_pairs[date_pairs.ret_date - date_pairs.dep_date >= datetime.timedelta(days = min_trip_duration)]

        # Now add on dep_time and ret_time if first or last day
        date_pairs.loc[date_pairs.dep_date == first_day, 'dep_time'] = first_day_time
        date_pairs.loc[date_pairs.ret_date == last_day, 'ret_time']  = last_day_time
        date_pairs['duration'] = date_pairs.ret_date - date_pairs.dep_date
        date_pairs['merge'] = 1

        self.data = pd.merge(self.data, date_pairs, on = 'merge')

    def make_url(self):
        self.data['url_dep'] = \
            'https://www.google.com/flights/beta#' \
            + 'flt=' \
            + self.data['origin'] \
            + '.' \
            + self.data['destination'] \
            + '.' \
            + self.data['dep_date'].apply(lambda x: x.strftime('%Y-%m-%d')) \
            + ';c:USD' \
            + ';e:1;sd:1;t:f;tt:o'
        if self.passengers != 1:
            self.data['url_dep'] = self.data['url_dep'] + ';px:' + self.passengers

        self.data['url_ret'] = \
            'https://www.google.com/flights/beta#' \
            + 'flt=' \
            + self.data['destination'] \
            + '.' \
            + self.data['origin'] \
            + '.' \
            + self.data['ret_date'].apply(lambda x: x.strftime('%Y-%m-%d')) \
            + ';c:USD' \
            + ';e:1;sd:1;t:f;tt:o'
        if self.passengers != 1:
            self.data['url_ret'] = self.data['url_ret'] + ';px:' + self.passengers
    
    def scrape(
        self,
        scrape_wait_time = 5,
        scrape_engine = 'chromedriver'):

        if scrape_engine.lower() == 'chromedriver':
            driver = webdriver.Chrome('../bin/chromedriver')
        elif scrape_engine.lower() == 'phantomjs':
            driver = webdriver.PhantomJS('/opt/phantomjs/bin/phantomjs')
        else:
            raise Exception("You must use 'Chromedriver' or 'PhantomJS'")

        flights_df = pd.DataFrame()
        scrape_time = str(datetime.datetime.now())[:-7]

        for i in range(len(self.data)):
            time.sleep(randint(1, 3))
            outbound_flights = self.scrape_page(self.data['url_dep'][i], driver)
            outbound_df = pd.DataFrame(outbound_flights)
            outbound_df['merge'] = 1

            time.sleep(randint(1, 3))
            return_flights = self.scrape_page(self.data['url_ret'][i], driver)
            return_df = pd.DataFrame(return_flights)
            return_df['merge'] = 1
            
            both_ways_df = pd.merge(outbound_df, return_df, on = 'merge', suffixes = ('_out', '_ret'))
            both_ways_df = both_ways_df.drop(['merge'], axis = 1)
            flights_df = flights_df.append(both_ways_df)
            
        return flights_df

    def scrape_page(self, url, driver):
        driver.get(url)
        timeout = 10
        try:
            element_present = EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '.gws-flights-results__unpriced-airlines'),
                'Prices are not available for: Southwest. Flights with unavailable prices are at the end of the list.')
            WebDriverWait(driver, timeout).until(element_present)
            time.sleep(1)
        except TimeoutException:
            print("Timed out waiting for page to load")

        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        flights_list = []
        all_results = soup.find_all(class_ = 'gws-flights-widgets-expandablecard__body')
        for n in range(len(all_results)):
            dict = {}
            stops = list(driver.find_elements_by_css_selector('.gws-flights-results__stops'))[n].text.strip()
            try:
                n_stops = int(stops[0])
            except ValueError:
                n_stops = 0
            dict['stops'] = n_stops
            
            collapsed_itinerary = list(soup.find_all(class_ = 'gws-flights-results__collapsed-itinerary'))[n]
            full_duration = collapsed_itinerary.find(class_ = 'gws-flights-results__duration').get_text()
            hours = int(re.search(r'(\d+)h\s+(\d+)m', full_duration)[1])
            minutes = int(re.search(r'(\d+)h\s+(\d+)m', full_duration)[2])
            dict['full_duration'] = hours + (minutes / 60)
            
            flight_date = list(list(soup.find_all(class_ = 'gws-flights-results__itinerary-details-heading-text'))[n].stripped_strings)[1]
            dict['flight_date'] = parse(flight_date).date()
            
            price = list(collapsed_itinerary.find(class_ = 'gws-flights-results__itinerary-price').stripped_strings)[0]
            try:
                dict['price'] = int(price[1:])
            except:
                pass
        
            dict['segments'] = []
            segments = list(all_results)[n].find_all(class_ = 'gws-flights-results__leg')
            for segment in segments:
                dict['segments'].append(self.get_segment_data(segment))
            
            # amenities = list(driver.find_elements_by_css_selector('.gws-flights-results__amenities'))[n].text.split('\n')
            flights_list.append(dict)
        
        return flights_list
    
    def get_segment_data(self, segment):
        """
        Input: a '.gws-flights-results__leg' object from BeautifulSoup
        """
        data = {}
        departure_data   = list(segment.find(class_ = 'gws-flights-results__leg-departure').stripped_strings)
        data['dep_time']         = departure_data[0]
        data['dep_airport_long'] = departure_data[1]
        data['dep_airport_code'] = departure_data[2]

        arrival_data     = list(segment.find(class_ = 'gws-flights-results__leg-arrival').stripped_strings)
        data['arr_time']         = arrival_data[0]
        data['arr_airport_long'] = arrival_data[1]
        data['arr_airport_code'] = arrival_data[2]

        flight_data   = list(segment.find(class_ = 'gws-flights-results__leg-flight').stripped_strings)
        data['airline']       = flight_data[0]
        data['seat_class']    = flight_data[1]
        data['airplane']      = flight_data[2]
        data['airline_code']  = flight_data[3]
        data['flight_number'] = flight_data[4]
        
        return data
