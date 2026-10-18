import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

from scraping.common import (
    fetch_feed,
    clean_html,
    make_article_key,
    make_article
)

FORTUNE_RSS_URL = "https://fortune.com/feed/fortune-feeds/?id=3230629"

NAMESPACES = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/"
}

def parse_article(item):
    """Convert RSS item to standardized dict"""

    title = item.findtext("title")
    url = item.findtext("link")
    published = item.findtext("pubDate")
    author = item.findtext("dc:creator", namespaces=NAMESPACES)
    description = item.findtext("description")
    guid = item.findtext("guid")

    content_element = item.find("content:encoded", namespaces=NAMESPACES)

    content_html = (
        content_element.text 
        if content_element is not None 
        else ""
    )

    content = clean_html(content_html)

    categories = [
        category.text
        for category in item.findall("category")
        if category.text
    ]

    return make_article(
        source = "Fortune",
        title = title,
        url = url,
        guid = guid,
        published = published,
        author = author,
        categories = categories,
        description = description,
        content = content
    )

def scrape_fortune(known_keys=None):
    """Scrape Fortune RSS feed"""

    if known_keys is None:
        known_keys = set()

    xml_data = fetch_feed(FORTUNE_RSS_URL)

    root = ET.fromstring(xml_data)
    
    articles = []

    for item in root.findall(".//item"):
        url = item.findtext("link")
        guid = item.findtext("guid")

        key = make_article_key("Fortune", guid=guid, url=url)

        if key in known_keys:
            continue

        article = parse_article(item)
        articles.append(article)

        if key is not None:
            known_keys.add(key)

    return articles

if __name__ == "__main__":
    articles = scrape_fortune()

    print(f"Found {len(articles)} articles")

    first_art = articles[0]
    for key, value in first_art.items():
        print(f"{key}: {value}")
