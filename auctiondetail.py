import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json


def scrape_auction_detail(details):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(details, 'lxml')

    # Extract data from highlights section
    highlights_section = soup.find('section', class_='highlights')
    bulleted_lists = highlights_section.find_all('ul', class_='bulleted-list')
    highlights_data = []
    for bulleted_list in bulleted_lists:
        highlights = [highlight.text.strip() for highlight in bulleted_list.find_all('li')]
        highlights_data.extend(highlights)

    # Extract data from description section
    description_text = ""
    description_section = soup.find('section', class_='description include-in-page')
    if description_section is not None:
        description_text = description_section.find('div', class_='column-12 sales-notes-text').text.strip()

    # Extract data from property facts section
    property_facts_section = soup.find('section', class_='listing-features property-facts')
    property_facts_div = property_facts_section.find('div', class_='property-facts-row')
    fact_names = [fact_name.text.strip() for fact_name in property_facts_div.find_all('div', class_='fact-name')]
    property_facts_values = [value.text.strip() for value in
                             property_facts_div.find_all('div', class_='property-facts-value-items')]

    # Extract data from mosaic-carousel
    mosaic_carousel = soup.find('div', id='mosaic-profile')
    mosaic_tiles = mosaic_carousel.find_all('div', class_='mosaic-tile')

    # Extract image source links from mosaic-tile divs
    image_links = [tile.find('img')['src'] if tile.find('img') else tile['data-src'] for tile in mosaic_tiles]

    # Create a dictionary to store the extracted data
    detail_data = {
        "highlights": [highlights_data],
        "summary": description_text,
        "property_facts": dict(zip(fact_names, property_facts_values)),
        "image_links": image_links
    }

    return detail_data
