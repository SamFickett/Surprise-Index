import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

NASDAQ_RSS_URL = "https://www.nasdaq.com/feed/nasdaq-original/rss.xml"

NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/"
}

def fetch_feed(url):
    """Download RSS feed, return XML"""

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(NASDAQ_RSS_URL, headers=headers, timeout=30)
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

    # In relation to first scraper (Fortune)
    # Categories/Content not provided. Returned as empty
    return {
        "source": "NASDAQ",
        "title": title,
        "url": url,
        "guid": guid,
        "published": published,
        "author": author,
        "categories": [],
        "description": description,
        "content": ""
    }

def clean_html(html):
    """HTML -> plain text"""

    soup = BeautifulSoup(html, "html.parser")

    return soup.get_text(" ", strip=True)

def scrape_nasdaq():
    """Scrape NASDAQ RSS feed"""

    xml_data = fetch_feed(NASDAQ_RSS_URL)

    root = ET.fromstring(xml_data)
    
    articles = []

    for item in root.findall(".//item"):
        article = parse_article(item)
        articles.append(article)

    return articles

if __name__ == "__main__":
    articles = scrape_nasdaq()

    print(f"Found {len(articles)} articles")

    first_art = articles[0]
    for key, value in first_art.items():
        print(f"{key}: {value}")
