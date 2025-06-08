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

hour = 25

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


def xml_scrape(xml_url, timezone, markets):

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
        
        tomorrow_day = datetime.now(timezone) + timedelta(days=1)
 
        forecasted = pd.DataFrame({'DateTime': dates[:temp_length], 'Temperature': temp})
        forecasted['DateTime'] = pd.to_datetime(forecasted['DateTime'])
        forecasted['Temperature'] = forecasted['Temperature'].apply(lambda x: str(x))
        forecasted = forecasted.sort_values(by='DateTime')
        forecasted = forecasted[forecasted['DateTime'].dt.day == tomorrow_day.day]
        forecasted['DateTime'] = forecasted['DateTime'].dt.strftime('%Y-%m-%d %H:%M')
        
        data_for_sheets = [list(forecasted.iloc[i]) + [markets] for i in range(len(forecasted))]
        
        # all_markets = [markets] * len(forecasted)

        return data_for_sheets

    except Exception as e:
      print(e)


def to_sheets(sheet_name, data_input):
    scropes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

    creds = Credentials.from_service_account_file("credentials.json", scopes=scropes)
    client = gspread.authorize(creds)

    sheet_id = "1JjBzplMaAfL3zXF_aRkAa1OuCS-W07RriC7itBNguNQ"
    sheet = client.open_by_key(sheet_id)
    
    sheet.worksheet(sheet_name).append_rows(data_input)
    
    

async def click_and_see_menu(markets, url_scrape):
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')  # Crucial for running as root or in some CI environments
    options.add_argument('--disable-dev-shm-usage') # Overcomes resource limits in /dev/shm
    options.add_argument('--disable-gpu') # Often recommended for headless
    
    async with webdriver.Chrome(options=options) as driver:
        url = url_scrape
        print(f"Navigating to {url}")
        await driver.get(url)

        try:
            await asyncio.sleep(3)
            # Click Dew Point button
            dew_point = "//button[@aria-label='Show Dew Point']"
            dew_point_button = await driver.find_element(By.XPATH, dew_point, timeout=5)
            await dew_point_button.click()
            
            await asyncio.sleep(3)
            # Click Humidity button
            humidity = "//button[@aria-label='Show Relative Humidity']"
            humidity_button = await driver.find_element(By.XPATH, humidity, timeout=5)
            await humidity_button.click()
            
            await asyncio.sleep(3)
            # Open menu
            menu_button_selector = '.highcharts-contextbutton' 
            menu_button = await driver.find_element(By.CSS_SELECTOR, menu_button_selector, timeout=5)
            await menu_button.click()

            await asyncio.sleep(3)  # Short pause for menu animation
            
            # Click "View data table"
            data_table_xpath = "//li[@class='highcharts-menu-item' and contains(text(), 'View data table')]"
            data_table_item = await driver.find_element(By.XPATH, data_table_xpath, timeout=5)
            await data_table_item.click()

            await asyncio.sleep(3)  # Wait for table to render
            
            # Find table - using more flexible selector since ID might change
            table = await driver.find_element(By.CSS_SELECTOR, "table[summary='Table representation of chart.']", timeout=5)
            
            await asyncio.sleep(3)
            
            # Extract headers
            # headers = []
            date_elements = await table.find_elements(By.TAG_NAME, "th")
            # for header in header_elements:
            #     headers.append(await header.text)
            
            await asyncio.sleep(3)
            
            dates = [await header.text for header in date_elements]
            dates = dates[2:]
    
            

            temps = []
            rows = await table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            await asyncio.sleep(2)
            
            for row in rows:
                cells = await row.find_elements(By.TAG_NAME, "td")
                # temps = [await cell.text for cell in cells]
                for cell in cells:
                    temps.append(await cell.text)
                    
            all_markets = [markets] * len(temps)
            
            
            to_lists = [list(row) for row in zip(dates, temps, all_markets)]
            
            return to_lists        
         

            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":

    for i,j in zip(markets, url):
       output = asyncio.run(click_and_see_menu(markets = i, url_scrape = j))
       #2to_sheets(sheet_name='daily_temp', data_input=output)
    
    today = datetime.today().weekday()
    if today == 1:     
        for a,b,c in zip(xml_url, timezone, markets):
            output_predict = xml_scrape(xml_url=a, timezone=b, markets=c)
            to_sheets(sheet_name='forecast', data_input=output_predict)
        
                
