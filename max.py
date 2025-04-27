import pytz
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import xml.etree.ElementTree as ET



timezone = [
    "America/Denver",
    "America/Chicago",
    "US/Eastern",
    "US/Central",
    "US/Eastern",
    "America/Los_Angeles",
]

xml_url = [
    "https://forecast.weather.gov/MapClick.php?lat=39.8589&lon=-104.6733&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=41.7842&lon=-87.7553&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=25.7934&lon=-80.2901&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=30.1945&lon=-97.6699&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=39.8721&lon=-75.2407&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=33.9425&lon=-118.409&FcstType=digitalDWML",
]


def xml_scrape(xml_url, timezone):

    try:
        timezone = pytz.timezone(timezone)
        response = requests.get(xml_url)
        root = ET.fromstring(response.content)

        start_times = root.findall('.//start-valid-time')
        dates = [time.text for time in start_times]

        temperature_element = root.find('.//temperature[@type="hourly"]')
        value_elements = temperature_element.findall('.//value')
        temp = [int(value.text) for value in value_elements if isinstance(value.text, str)]
        temp_length = len(temp)
 
        forecasted = pd.DataFrame({'DateTime': dates[:temp_length], 'Temperature': temp})
        forecasted['DateTime'] = pd.to_datetime(forecasted['DateTime'])
        forecasted = forecasted.sort_values(by='DateTime')

        denver_today = datetime.now(timezone).day + 1

        next_day_high = forecasted[forecasted['DateTime'].dt.day == denver_today]['Temperature'].idxmax()#[::-1]
        date = forecasted['DateTime'].iloc[next_day_high]
        hour_of_high = forecasted['DateTime'].iloc[next_day_high].hour
        temp_high = forecasted['Temperature'].iloc[next_day_high]
        
        date = date.strftime('%Y-%m-%d %H:%M:%S')

        return [date, hour_of_high, temp_high]

    except Exception as e:
      print(e)
      

print(xml_scrape(xml_url = xml_url[0], timezone=timezone[0]))