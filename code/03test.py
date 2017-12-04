test = scraper(origin = 'bos', destination = ['LAX'])
test.data
test.add_dates('December 20', 'December 21')
test.data
test.make_url()
# test.data
test.data['url_dep'][0]
data = test.scrape()
## This works as of 12/3/2017, 7:59:51 PM


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
airports = feather.read_dataframe("../data/airports.feather")


test = scrape_flights(origin = "bos", destination = ["LAX", "SEA"])
test.datetimes("July 20 10:00 am", "July 22 5:00 pm")
test.make_url()
flights = test.scrape()
