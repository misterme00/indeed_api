from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
from urllib.parse import urlencode
import json
import re
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
import os

os.environ['DISPLAY'] = ':0'  # Use the correct display, usually ':0'

display = Display(visible=0, size=(800, 600))
display.start()




def parse_search_page(html: str):
    data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', html)
    data = json.loads(data[0])
    return {
        "results": data["metaData"]["mosaicProviderJobCardsModel"]["results"],
        "meta": data["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"],
    }

async def scrape_search(driver: webdriver, query: str, location: str, max_results: int = 50):
    def make_page_url(offset):
        parameters = {"q": query, "l": location, "fromage": 7, "filter": 0, "start": offset}
        return "https://www.indeed.com/jobs?" + urlencode(parameters)

    print(f"scraping first page of search: {query=}, {location=}")
    driver.get(make_page_url(0))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    data_first_page = parse_search_page(driver.page_source)

    results = data_first_page["results"]
   

    total_results = sum(category["jobCount"] for category in data_first_page["meta"])
    # there's a page limit on indeed.com of 1000 results per search
    if total_results > max_results:
        total_results = max_results
    print(f"scraping remaining {total_results - 10 / 10} pages")
    other_pages = [make_page_url(offset) for offset in range(10, total_results + 10, 10)]
    
    for url in other_pages:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        results.extend(parse_search_page(driver.page_source)['results'])
        
        


    return results

def extract_job_info(job_data):
    job_info = {}

    # Extracting basic information
    job_info['title'] = job_data.get('displayTitle', '')
    job_info['company'] = job_data.get('company', '')
    job_info['location'] = job_data.get('formattedLocation', '')
    job_info['posted_time'] = job_data.get('formattedRelativeTime', '')
    job_info['jobkey'] = job_data.get('jobkey')

    # Extracting salary information
    salary_info = job_data.get('extractedSalary', {})
    job_info['salary'] = {
        'min': salary_info.get('min', None),
        'max': salary_info.get('max', None),
        'type': salary_info.get('type', '')
    }

    # Extracting job type information
    job_info['job_types'] = job_data.get('jobTypes', [])

    # Extracting additional attributes
    job_info['description'] = BeautifulSoup(job_data.get('snippet', '').strip(), 'html.parser').getText()
    job_info['link'] = job_data.get('link', '')

    return job_info



app = Flask(__name__)


@app.route('/')
def home():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    query = request.args.get('q')
    try:
        searchData =asyncio.run(scrape_search(driver, query=query, location="Remote"))
  
        jiA=[]
        for job_data in searchData:
            job_info = extract_job_info(job_data)
            jiA.append(job_info)
    finally:
        driver.quit()        
        
    return json.dumps(jiA)        
    
    
    


if __name__ == '__main__':
    app.run(port=3002)    





