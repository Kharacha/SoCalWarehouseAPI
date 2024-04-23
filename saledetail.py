from bs4 import BeautifulSoup


def replace_unicode_chars(text):
    return text.replace('\u2019', "'").replace('\u2013', "-").replace('\u00e7', "c")


def scrape_sale_detail(details):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(details, 'lxml')
    print(soup)

    # Extract the address from the breadcrumbs
    address_section = soup.find('h1', class_='breadcrumbs__crumb breadcrumbs__crumb-title')
    address = address_section.text.strip()

    # Extract data from highlights section
    highlights_section = soup.find('section', class_='highlights')
    # if highlights_section is not None:
    bulleted_lists = highlights_section.find_all('ul', class_='bulleted-list')
    highlights_data = []
    for bulleted_list in bulleted_lists:
        highlights = [highlight.text.strip() for highlight in bulleted_list.find_all('li')]
        highlights_data.extend(highlights)

    # Initialize facts_data as an empty dictionary
    facts_data = {}
    property_facts_facts_wrap = soup.find('div', class_='property-facts__facts-wrap')
    if property_facts_facts_wrap:
        property_facts_labels_items = property_facts_facts_wrap.find_all('div', class_='property-facts__labels-item')
        spans = soup.find_all('span', class_='expandable-suptype__text')
        facts_data = {replace_unicode_chars(item.get_text(strip=True)): replace_unicode_chars(span.get_text(strip=True)) for item, span in
                      zip(property_facts_labels_items, spans)}

    description_text = ""
    # Extract data from description section
    description_section = soup.find('section', class_='description about-address')
    if description_section is not None:
        description_div = description_section.find('div', class_='column-12 description-text')
        description_text = replace_unicode_chars(description_div.find('p', class_='pre-wrap').text.strip())
    else:
        description_section = soup.find('section', class_='description include-in-page')
        description_text = replace_unicode_chars(description_section.find('div', class_='column-12 sales-notes-text').text.strip())

    image_links = []
    mosaic_tiles = soup.find('div', class_='carousel-inner')
    if mosaic_tiles:
        slides = mosaic_tiles.find_all('div', class_='slide')
        for slide in slides:
            img_tag = slide.find('img')

            if img_tag:
                if 'src' in img_tag.attrs:
                    img_link = img_tag['src']
                    image_links.append(img_link)
                if 'lazy-src' in img_tag.attrs:
                    lazy_img_link = img_tag['lazy-src']
                    image_links.append(lazy_img_link)

    # Create a dictionary to store the extracted data
    detail_data = {
        "address": address,
        "highlights": [highlights_data],
        "summary": description_text,
        "property_facts": facts_data,
        "image_links": image_links
    }

    return detail_data
