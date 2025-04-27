import asyncio
from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from datetime import datetime
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import pytz
import gspread
from google.oauth2.service_account import Credentials



markets = [
    "KXHIGHDEN",
    "KXHIGHCHI",
    "KXHIGHMIA",
    "KXHIGHAUS",
    "KXHIGHPHIL",
    "KXHIGHLAX",
]

hour = 26

url = [
    f"https://www.weather.gov/wrh/timeseries?site=KDEN&hours={hour}",
    f"https://www.weather.gov/wrh/timeseries?site=KMDW&hours={hour}",
    f"https://www.weather.gov/wrh/timeseries?site=KMIA&hours={hour}",
    f"https://www.weather.gov/wrh/timeseries?site=KAUS&hours={hour}",
    f"https://www.weather.gov/wrh/timeseries?site=KPHL&hours={hour}",
    f"https://www.weather.gov/wrh/timeseries?site=KLAX&hours={hour}",
]

xml_url = [
    "https://forecast.weather.gov/MapClick.php?lat=39.8589&lon=-104.6733&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=41.7842&lon=-87.7553&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=25.7934&lon=-80.2901&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=30.1945&lon=-97.6699&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=39.8721&lon=-75.2407&FcstType=digitalDWML",
    "https://forecast.weather.gov/MapClick.php?lat=33.9425&lon=-118.409&FcstType=digitalDWML",
]

timezone = [
    "America/Denver",
    "America/Chicago",
    "US/Eastern",
    "US/Central",
    "US/Eastern",
    "America/Los_Angeles",
]


def xml_scrape(xml_url, timezone, market):

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

        denver_today = datetime.now(timezone).day

        next_day_high = forecasted[forecasted['DateTime'].dt.day == denver_today]['Temperature'].idxmax()#[::-1]
        date = forecasted['DateTime'].iloc[next_day_high]
        hour_of_high = forecasted['DateTime'].iloc[next_day_high].hour
        temp_high = forecasted['Temperature'].iloc[next_day_high]

        return [str(date), str(hour_of_high), str(temp_high), str(market)]

    except Exception as e:
      print(e)


def to_sheets(sheet_name, datetime):
    scropes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

    creds = Credentials.from_service_account_file("credentials.json", scopes=scropes)
    client = gspread.authorize(creds)

    sheet_id = "1JjBzplMaAfL3zXF_aRkAa1OuCS-W07RriC7itBNguNQ"
    sheet = client.open_by_key(sheet_id)
    
    sheet.worksheet(sheet_name).append_row(datetime)

async def click_and_see_menu(markets, url_scrape):
    
    options = webdriver.ChromeOptions()
    
    async with webdriver.Chrome(options=options) as driver:
        url = url_scrape
        print(f"Navigating to {url}")
        await driver.get(url)

        try:
            
            # Click Dew Point button
            dew_point = "//button[@aria-label='Show Dew Point']"
            dew_point_button = await driver.find_element(By.XPATH, dew_point, timeout=5)
            await dew_point_button.click()

            # Click Humidity button
            humidity = "//button[@aria-label='Show Relative Humidity']"
            humidity_button = await driver.find_element(By.XPATH, humidity, timeout=5)
            await humidity_button.click()
            
            # Open menu
            menu_button_selector = '.highcharts-contextbutton' 
            menu_button = await driver.find_element(By.CSS_SELECTOR, menu_button_selector, timeout=5)
            await menu_button.click()

            await asyncio.sleep(2)  # Short pause for menu animation
            
            # Click "View data table"
            data_table_xpath = "//li[@class='highcharts-menu-item' and contains(text(), 'View data table')]"
            data_table_item = await driver.find_element(By.XPATH, data_table_xpath, timeout=5)
            await data_table_item.click()

            await asyncio.sleep(1)  # Wait for table to render
            
            # Find table - using more flexible selector since ID might change
            table = await driver.find_element(By.CSS_SELECTOR, "table[summary='Table representation of chart.']", timeout=5)
            
            # Extract headers
            # headers = []
            date_elements = await table.find_elements(By.TAG_NAME, "th")
            # for header in header_elements:
            #     headers.append(await header.text)
            
            dates = [await header.text for header in date_elements]
            dates = dates[2:]
    
            

            temps = []
            rows = await table.find_elements(By.CSS_SELECTOR, "tbody tr")
            for row in rows:
                cells = await row.find_elements(By.TAG_NAME, "td")
                # temps = [await cell.text for cell in cells]
                for cell in cells:
                    temps.append(await cell.text)
                    
            all_markets = [markets] * len(temps)

            return [dates, temps, all_markets]
            
    
                    
            # for i,j in zip(dates[2:],temps):
            #     # print(i,j)
            #     await to_sheets(sheet_name='Sheet1', datetime=[i,j, markets])
            #     await asyncio.sleep(1) 

           
         

            
        except Exception as e:
            print(f"Error: {e}")
            # Take screenshot for debugging
            # await driver.save_screenshot("error.png")

        # await asyncio.sleep(15)

if __name__ == "__main__":
    for i,j in zip(markets, url):
        output = asyncio.run(click_and_see_menu(markets=i, url_scrape=j))
        # print(output)
        for a,b,c in zip(output[0], output[1], output[2]):
            to_sheets(sheet_name='Sheet1', datetime=[a,b,c])

    for i,j,k in zip(xml_url, timezone, markets):
        to_sheets(sheet_name='Sheet2', datetime=(xml_scrape(xml_url=i, timezone=j,market=k)))
                                           