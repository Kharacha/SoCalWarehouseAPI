import concurrent
import math

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
from file1 import scrape_properties
from file2 import scrape_listings
from fake_useragent import UserAgent
import time

app = Flask(__name__)
CORS(app)


ua = UserAgent()
headers = {'User-Agent': str(ua.chrome)}


# Define a ThreadPoolExecutor
executor = ThreadPoolExecutor()


session = requests.Session()
session.headers.update(headers)


def getMaxPage(soup):
    total_results_span = soup.find('span', class_='total-results-paging-digits')
    total_results_text = total_results_span.get_text(strip=True)

    last_page_number = total_results_text.split()[-1]

    return math.ceil(int(last_page_number) / 25)


# Define a Flask route for serving combined property data
@app.route('/getcombineddata', methods=['GET'])
def get_combined_data():

    page = request.args.get('page')
    zipcode = request.args.get('zipcode')
    city = request.args.get("city")
    state = request.args.get('state')

    if zipcode:
        zipcode = f"-{zipcode}"
    url_listings = f'https://www.loopnet.com/search/commercial-real-estate/{city}-{state}{zipcode}/for-sale/{page}'

    response = session.get(url_listings)
    response_content = response.content

    future_properties = executor.submit(scrape_properties, response_content)
    future_listings = executor.submit(scrape_listings, response_content)

    # Wait for both functions to complete
    concurrent.futures.wait([future_properties, future_listings])

    # Get the results from both futures
    properties_data = future_properties.result()
    listings_data = future_listings.result()

    combined_data = {
        'maxPage': getMaxPage(BeautifulSoup(response_content, 'lxml')),
        'propertyData': properties_data + listings_data
    }
    # Return JSON data
    return jsonify(combined_data)

if __name__ == '__main__':
    app.run(debug=True)