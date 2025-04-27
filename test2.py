from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import pytz
from datetime import datetime

import asyncio


async def main():
    options = webdriver.ChromeOptions()
    # options.add_experimental_option("detach", True)
    # options.add_argument("--headless")
    async with webdriver.Chrome(options=options) as driver:
        await driver.get('https://www.weather.gov/wrh/timeseries?site=KDEN&hours=30', wait_load=True)
        await driver.sleep(5)
        await driver.wait_for_cdp("Page.domContentEventFired", timeout=15)
        await driver.sleep(5)
        menu_button_selector = '.highcharts-contextbutton'
        menu_button = await driver.find_element(By.CSS_SELECTOR, menu_button_selector, timeout=20)
        await asyncio.sleep(100) 
        await menu_button.click()
        await asyncio.sleep(10) 
        await menu_button.click()
        await menu_button.click()
        await menu_button.click()
        menu_item_selector = '.highcharts-menu-item' 
        await driver.find_element(By.CSS_SELECTOR, menu_item_selector, timeout=5)
        
        # await menu_button.click()

asyncio.run(main())