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

def fetch_page(url):
    """Fetch HTML for content retrieval"""
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
        
    return response.content

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
    return {
        "source": "NASDAQ",
        "title": title,
        "url": url,
        "guid": guid,
        "published": published,
        "author": author,
        "categories": [],
        "description": description,
        "content": content
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
  
