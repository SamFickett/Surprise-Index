import xml.etree.ElementTree as ET

import requests
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

NASDAQ_RSS_URL = "https://www.nasdaq.com/feed/nasdaq-original/rss.xml"

NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/"
}

def extract_article_content(url):
    """Extract article content from NASDAQ article page"""

    html = fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    # Template 1
    content_element = soup.find("div", id="text")

    if content_element is not None:
        return content_element.get_text(" ", strip=True)

    # Template 2
    text_blocks = soup.select("div.nsdq-mercury-text-block")

    content_parts = []

    for block in text_blocks:
        text = block.get_text(" ", strip=True)
        if text:
            content_parts.append(text)

    return " ".join(content_parts)

def parse_article(item):
    """Convert RSS item to standardized dict"""

    title = item.findtext("title")
    url = item.findtext("link")
    published = item.findtext("pubDate")
    author = item.findtext("dc:creator", namespaces=NAMESPACES)
    description = item.findtext("description")
    guid = item.findtext("guid")
    content = extract_article_content(url)

    # In relation to first scraper (Fortune)
    # Categories/Content not provided. Returned as empty
    return make_article(
        source = "NASDAQ",
        title = title,
        url = url,
        guid = guid,
        published = published,
        author = author,
        categories = [],
        description = description,
        content = content
    )

def scrape_nasdaq(known_keys=None):
    """Scrape NASDAQ RSS feed"""

    if known_keys is None:
        known_keys = set()

    seen_keys = set(known_keys)

    xml_data = fetch_feed(NASDAQ_RSS_URL)

    root = ET.fromstring(xml_data)
    
    new_items = []

    for item in root.findall(".//item"):
        url = item.findtext("link")
        guid = item.findtext("guid")

        key = make_article_key("NASDAQ", guid=guid, url=url)

        if key in seen_keys:
            continue

        new_items.append(item)

        if key is not None:
            seen_keys.add(key)

    articles = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(
            executor.map(
                safe_parse_article,
                new_items
            )
        )

        for article in results:
            if article is not None:
                articles.append(article)

    return articles

def safe_parse_article(item):
    try:
        return parse_article(item)
    
    except Exception as error:
        url = item.findtext("link")

        print(f"Failed to parse {url}: {error}")

        return None

if __name__ == "__main__":
    articles = scrape_nasdaq()

    print(f"Found {len(articles)} articles\n")

    success_count = 0
    fail_count = 0

    for article in articles:
        if article["content"]:
            success_count += 1
            print(f"SUCCESS: {article["title"]}")
            print(f"Content Length: {len(article["content"])}")
        else:
            fail_count += 1
            print(f"FAILED: {article["title"]}")
            print(f"URL: {article["url"]}")

        print()

    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
  


"""
TODO:
Remove disclaimer/legal text from the block templates
"""