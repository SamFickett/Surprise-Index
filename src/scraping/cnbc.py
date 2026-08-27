import xml.etree.ElementTree as ET

import requests
import json
from bs4 import BeautifulSoup

CNBC_US_RSS_URL = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15837362"
CNBC_WORLD_RSS_URL = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362"

NAMESPACES = {
    "metadata": "http://search.cnbc.com/rss/2.0/modules/siteContentMetadata"
}

def fetch_feed(url):
    """Download RSS feed, return XML"""

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    return response.content

def fetch_page(url):
    """Fetch HTML for content retrieval"""
        
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
        
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
            
    return response.text

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
    return {
        "source": "CNBC",
        "title": title,
        "url": url,
        "guid": guid,
        "published": published,
        "author": None,
        "categories": [],
        "description": description,
        "content": content
    }

def get_article_content(url):
    """Extract text content from CNBC article"""

    html = fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    content_element = soup.find("div", class_="ArticleBody-articleBody")

    if content_element is None:
        return ""

    return content_element.get_text(" ", strip=True)

def clean_html(html):
    """HTML -> plain text"""

    soup = BeautifulSoup(html, "html.parser")

    return soup.get_text(" ", strip=True)

def scrape_feed(feed_url):
    """Scrape CNBC RSS feeds"""
    
    xml_data = fetch_feed(feed_url)
    
    root = ET.fromstring(xml_data)
        
    articles = []
    
    for item in root.findall(".//item"):
        article = parse_article(item)
        articles.append(article)
    
    return articles

def scrape_cnbc():
    us_articles = scrape_feed(CNBC_US_RSS_URL)
    world_articles = scrape_feed(CNBC_WORLD_RSS_URL)

    all_articles = us_articles + world_articles

    seen = set()
    unique_articles = []

    for article in all_articles:
        guid = article["guid"]

        if guid not in seen:
            seen.add(guid)
            unique_articles.append(article)

    return unique_articles

if __name__ == "__main__":
    articles = scrape_cnbc()

    print(f"Found {len(articles)} articles\n")

    for article in articles:
        print(article["title"])