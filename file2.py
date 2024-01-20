import requests
from bs4 import BeautifulSoup
import re
import json
import time


def scrape_listings(response):
    soup = BeautifulSoup(response, 'lxml')
    property_list = []

    # Find all <article> elements with class 'placard'
    articles = soup.find_all('article', class_='placard')

    for article in articles:
        id_element = article['data-id']

        title_element = article.find('a', class_='left-h4')
        listing_title = title_element.text.strip() if title_element else ""

        # Extracting location details using different elements
        location_element = article.find('a', class_='right-h6')
        location = location_element.text.strip() if location_element else ""

        # Check if both title and address are not just spaces before adding to the property list
        if listing_title and location:
            # Extracting space available
            space_available_element = article.find('a', class_='right-h4')
            space_available = space_available_element.text.strip() if space_available_element else ""

            # Extracting only the text content of the third li element for price
            price_ul_element = article.find('div', class_='auction auction-data-points')
            price_value = None

            if price_ul_element:
                price_li_elements = price_ul_element.find_all('li')
                for li_element in price_li_elements:
                    span_element = li_element.find('span')
                    if span_element and 'Starting bid' in span_element.text:
                        price_value = span_element.text.replace('Starting bid', '').strip()
                        break

            # Use regular expression to match patterns like "Number Category"
            match = re.match(r'^(\d+)\s+(.+)$', listing_title)
            placard_number, new_title = match.groups() if match else ("", listing_title)

            # Extracting images
            carousel_inner = article.find('div', class_='carousel-inner')
            first_image_url = "No Image"

            if carousel_inner:
                slides = carousel_inner.find_all('div', class_='slide')
                if slides:
                    first_slide = slides[0]
                    figure = first_slide.find('figure')
                    img_tag = figure.find('img', class_='image-hide') if figure else None

                    if img_tag and 'src' in img_tag.attrs:
                        first_image_url = img_tag['src']

            # Create a dictionary for each property
            property_data = {
                'ID': id_element,
                'Title': f"{placard_number} {new_title}",
                'Image URL': first_image_url,
                'Address': location,
                'Price': price_value,
                'Building Info': [space_available]
            }

            # Append the dictionary to the property list
            property_list.append(property_data)

    return property_list


