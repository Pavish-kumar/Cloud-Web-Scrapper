# Effectively runs at High Internet Speed

import time
import random
#import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd


# Get the page source and parse it with BeautifulSoup
async def get_page_source(driver, url):
    driver.get(url)
    driver.maximize_window()

    # Wait until the dropdown is present
    dropdown_locator = (By.CLASS_NAME, 'mt-1')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(dropdown_locator))

    dropdown = driver.find_element(*dropdown_locator)
    dropdown.click()
    dropdown.send_keys(Keys.DOWN)
    dropdown.send_keys(Keys.DOWN)
    dropdown.send_keys(Keys.ENTER)
    await asyncio.sleep(1)
    return driver.page_source


# Fetch the data from the source page returned from get_page_source() with the bs4 and selenium webdriver
async def fetch_data(session, driver, url):
    page_source = await get_page_source(driver, url)
    soup = BeautifulSoup(page_source, 'lxml')
    table = soup.find('table', class_='w-full divide-y divide-gray-300 lg:table-fixed')
    table_body = table.find('tbody', class_='divide-y divide-gray-200 bg-white')
    rows = table_body.find_all('tr')

    data_list = []
    cloud_domain = driver.find_elements(By.XPATH, "//a[@class='underline hover:text-tangelo']")
    random_indices = random.sample(range(len(cloud_domain)), len(cloud_domain))

    for random_index in random_indices:
        p = cloud_domain[random_index]
        page = p.text.replace(" ", "-")
        company_url = f"https://www.employbl.com/companies/{page}"
        r = requests.get(company_url)
        bs = BeautifulSoup(r.text, "html.parser")
        # Find the link in the company page
        link = bs.find('a',
                       class_="flex items-center justify-center text-base font-medium text-indigo-600 sm:justify-start")

        if link:
            href_value = link.get('href').replace("https://", "").replace("www.", "").replace("/", "")
            href_url = f"www.{href_value}"
            data_list.append(href_url)

        if len(data_list) >= 500:
            break

    return data_list


async def write_to_excel(data_list, url):
    # Create a DataFrame and write it to an Excel file
    filename = f'({url.replace("https://", "").replace("/", "_")})_Data.xlsx'
    df = pd.DataFrame({"Website": data_list})
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f'Data for {url} has been written to {filename}')


async def main():
    # List of URLs to extract data from
    urls = ['amazon-web-services',
            'google-cloud-platform',
            'microsoft-azure']
    chrome_options = Options()
    # Set up Chrome WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    async with aiohttp.ClientSession() as session:
        for url in urls:
            print(f"Extracting data from: {url}")
            # Fetch data and write to Excel for each URL
            data_list = await fetch_data(session, driver, f'https://www.employbl.com/company-collections/{url}')
            await write_to_excel(data_list, url)
            print(f"Extraction from {url} is successful.\n")
    # Quit the Chrome WebDriver
    driver.quit()
    print("Extraction of data is complete.")


if __name__ == "__main__":
    # Run the main function using asyncio
    asyncio.run(main())
