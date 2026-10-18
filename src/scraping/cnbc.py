import xml.etree.ElementTree as ET

import requests
import json
from bs4 import BeautifulSoup
import time

from concurrent.futures import ThreadPoolExecutor
MAX_WORKERS = 5

from scraping.common import (
    fetch_feed,
    fetch_page,
    make_article_key,
    make_article
)

CNBC_US_RSS_URL = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15837362"
CNBC_WORLD_RSS_URL = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362"

CNBC_FEEDS = (
    CNBC_US_RSS_URL,
    CNBC_WORLD_RSS_URL
)

NAMESPACES = {
    "metadata": "http://search.cnbc.com/rss/2.0/modules/siteContentMetadata"
}

def parse_article(item):
    """Convert RSS item to standardized dict"""

    title = item.findtext("title")
    url = item.findtext("link")
    published = item.findtext("pubDate")
    description = item.findtext("description")
    guid = item.findtext("guid")
    content = get_article_content(url)

    # In relation to first scraper (Fortune)
    # Categories/Content not provided. Returned as empty
    return make_article(
        source = "CNBC",
        title = title,
        url = url,
        guid = guid,
        published = published,
        author = None,
        categories = [],
        description = description,
        content = content
    )

def get_article_content(url):
    """Extract text content from CNBC article"""

    html = fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    content_element = soup.find("div", class_="ArticleBody-articleBody")

    if content_element is None:
        return ""

    return content_element.get_text(" ", strip=True)

def scrape_feed(feed_url, known_keys=None):
    """Scrape CNBC RSS feeds"""

    if known_keys is None:
        known_keys = set()

    xml_data = fetch_feed(feed_url)
    
    root = ET.fromstring(xml_data)
        
    new_items = []
    
    for item in root.findall(".//item"):
        url = item.findtext("link")
        guid = item.findtext("guid")

        key = make_article_key("CNBC", guid=guid, url=url)

        if key in known_keys:
            continue

        new_items.append(item)

        if key is not None:
            known_keys.add(key)

    articles = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(safe_parse_article, new_items)

        articles = [article for article in results if article is not None]
    
    return articles

def scrape_cnbc(known_keys=None):
    if known_keys is None:
        known_keys = set()

    articles = []

    for feed_url in CNBC_FEEDS:
        feed_articles = scrape_feed(feed_url, known_keys)

        articles.extend(feed_articles)

    return articles

def safe_parse_article(item):
    try:
        return parse_article(item)
    except Exception as error:
        url = item.findtext("link")
        print(f"Failed to parse {url}: {error}")
        return None

if __name__ == "__main__":
    articles = scrape_cnbc()

    print(f"Found {len(articles)} articles\n")

    for article in articles:
        print(article["title"])