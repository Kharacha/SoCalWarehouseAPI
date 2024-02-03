import concurrent
import math
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
from saledetail import scrape_sale_detail
from file1 import scrape_properties
from file2 import scrape_listings
from fake_useragent import UserAgent
import random

app = Flask(__name__)
CORS(app)

agents = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15"
]

# heading = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"

ua = UserAgent()
headers = {'User-Agent': random.choice(agents)}

#headers = {'User-Agent':str(ua.chrome)}
#headers = {'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1" }

# Define a ThreadPoolExecutor
executor = ThreadPoolExecutor()

session = requests.Session()
# session.headers.update(headers)

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


    response = session.get(url_listings, headers=headers)
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


@app.route('/getdetails', methods=['GET'])
def find_details():
    detailid = request.args.get('detailid')
    url_details = f'https://www.loopnet.com/listing/{detailid}'

    details = session.get(url_details, headers=headers)
    details_content = details.content

    result = scrape_sale_detail(details_content)

    combined_details = {
        'buildingDetail':
            result
    }
    return jsonify(combined_details)


if __name__ == '__main__':
    app.run(debug=True)
