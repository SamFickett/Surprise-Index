import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

FORTUNE_RSS_URL = "https://fortune.com/feed/fortune-feeds/?id=3230629"

NAMESPACES = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/"
}

def fetch_feed(url):
    """Download RSS feed, return XML"""

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(FORTUNE_RSS_URL, headers=headers, timeout=30)
    response.raise_for_status()
    
    return response.content

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

    return {
        "source": "Fortune",
        "title": title,
        "url": url,
        "guid": guid,
        "published": published,
        "author": author,
        "categories": categories,
        "description": description,
        "content": content
    }

def clean_html(html):
    """HTML -> plain text"""

    soup = BeautifulSoup(html, "html.parser")

    return soup.get_text(" ", strip=True)

def scrape_fortune():
    """Scrape Fortune RSS feed"""

    xml_data = fetch_feed(FORTUNE_RSS_URL)

    root = ET.fromstring(xml_data)
    
    articles = []

    for item in root.findall(".//item"):
        article = parse_article(item)
        articles.append(article)

    return articles

if __name__ == "__main__":
    articles = scrape_fortune()

    print(f"Found {len(articles)} articles")

    first_art = articles[0]
    for key, value in first_art.items():
        print(f"{key}: {value}")

#    for article in articles:
#        print(article["title"])