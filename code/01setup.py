# Download Airport data and put into pandas object
# Download chromedriver binary

import pandas as pd
import numpy as np
import feather
import requests
import os
import sys
import platform
import zipfile
import stat

# Get airports data
def get_airport_data():
    colnames = ["openflights_id", "airport_name", "city", "country", "iata", "icao", "lat", "lon", "altitude", "timezone", "dst", "tz_zone", "type", "source"]
    airports = pd.read_csv("https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat",
                           header = None,
                           names = colnames)
    airports = airports.loc[:, ["city", "country", "iata", "lat", "lon", "altitude", "tz_zone"]]
    airports = airports[airports.iata != "\\N"]
    airports = airports[airports.country.isin(["United States", "Canada"])]
    feather.write_dataframe(airports, "../data/airports.feather")

def get_chromedriver():
    latest_chromedriver_version = requests.get("https://chromedriver.storage.googleapis.com/LATEST_RELEASE").text[:-1]

    if not os.path.exists("../bin"):
        os.makedirs("../bin")

    if sys.platform.startswith("linux"):
        if platform.architecture()[0] == "64bit":
            url = "https://chromedriver.storage.googleapis.com/" + latest_chromedriver_version + "/chromedriver_linux64.zip"
        else:
            url = "https://chromedriver.storage.googleapis.com/" + latest_chromedriver_version + "/chromedriver_linux32.zip"
    elif sys.platform == "darwin":
        url = "https://chromedriver.storage.googleapis.com/" + latest_chromedriver_version + "/chromedriver_mac64.zip"
    else:
        url = "https://chromedriver.storage.googleapis.com/" + latest_chromedriver_version + "/chromedriver_win32.zip"

    chromedriver = requests.get(url)
    with open("../bin/chromedriver.zip", "wb") as f:
        f.write(chromedriver.content)

    chromedriver_zip = zipfile.ZipFile("../bin/chromedriver.zip", "r")
    if sys.platform == "win32":
        chromedriver_zip.extract("chromedriver.exe", "../bin/")
    else:
        chromedriver_zip.extract("chromedriver", "../bin/")
    chromedriver_zip.close()
    os.remove("../bin/chromedriver.zip")
    # Make executable for user
    st = os.stat("../bin/chromedriver")
    os.chmod("../bin/chromedriver", st.st_mode | stat.S_IXUSR)

def get_phantomjs():
    if not os.path.exists("../bin"):
        os.makedirs("../bin")

    if sys.platform.startswith("linux"):
        if platform.architecture()[0] == "64bit":
            url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"
        else:
            url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-i686.tar.bz2"
    elif sys.platform == "darwin":
        url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-macosx.zip"
    else:
        url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip"


get_airport_data()
get_chromedriver()
