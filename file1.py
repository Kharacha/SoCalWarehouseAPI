import requests
from bs4 import BeautifulSoup


def scrape_properties(response):
    soup = BeautifulSoup(response, 'lxml')
    property_list = []  # Initialize an empty list to store property data

    # Find all articles with the specified class
    articles = soup.find_all('article', class_='placard tier4 landscape')

    # Iterate through each article and extract data
    for article in articles:
        # Extracting ID
        id_element = article['data-id']

        # Extracting title of the building
        title_element = article.select_one('h4 a')
        title = title_element.text.strip() if title_element else "N/A"

        # Extracting image URL
        img_url = article.find('div', class_='slide').find('img')['src']

        # Extracting address, price, and other details
        address = article.find('a', class_='subtitle-beta').text.strip()
        price = article.find('li', {'name': 'Price'})
        building_info = [info.text.strip() for info in article.find('ul', class_='data-points-2c').find_all('li')]

        # Create a dictionary for each property
        property_data = {
            'ID': id_element,
            'Title': title,
            'Image URL': img_url,
            'Address': address,
            'Price': price.text.strip() if price else 'N/A',
            'Building Info': building_info
        }

        # Append the dictionary to the property list
        property_list.append(property_data)

    return property_list
