
import asyncio
from playwright.async_api import async_playwright
import pytz
import pandas as pd
import numpy as np
import pytz
import pandas as pd
import numpy as np
import datetime as datetime




def date_temp(timezone, datetemp_list):
    
    timezone = pytz.timezone(timezone)
    
    temps =  [float(i.split(', ')[-1].split(' ')[0][:-1]) for i in datetemp_list]
    dates = [', '.join(i.split(', ')[0:3]) for i in datetemp_list]

    timezone = pytz.timezone('America/Denver')

    current_day = datetime.now(timezone).day
    current_year = datetime.now(timezone).year

    date = [datetime.strptime(i, '%A, %b %d, %I:%M %p') for i,j in zip(dates, temps) if datetime.strptime(i, '%A, %b %d, %I:%M %p').day == current_day]
    temp = [j for i,j in zip(dates, temps) if datetime.strptime(i, '%A, %b %d, %I:%M %p').day == current_day]

    date = [i.replace(year=current_year).strftime('%Y-%m-%d %H:%M') for i in date]
    
    return [date, temp]
        
        
async def date_temp_scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        url = "https://www.weather.gov/wrh/timeseries?site=KDEN&hours=30"
        
        # Navigate to the page
        await page.goto(url)
        
        # Wait for the charts to load
        await page.wait_for_load_state("networkidle")
        
        # Wait a bit more to ensure JavaScript rendering completes
        await page.wait_for_timeout(1000)
        
        # Use a more specific selector for paths with the fill color
        # datetemp_list = await page.evaluate('''
        #        () => {
        #         const paths = Array.from(document.querySelectorAll('path'));
        #         return paths
        #             .filter(path => path.getAttribute('fill') === '#2caffe')
        #             .map(path => path.getAttribute('aria-label'));
        #     }
        # ''')
        
        
        
       
        # for i in datetemp_list:
        #     print(i)

            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(date_temp_scrape())