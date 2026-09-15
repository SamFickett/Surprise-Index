import requests
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from scraping.common import (
    fetch_page,
    make_article
)

MORNINGBREW_URL = "https://www.morningbrew.com/"

def get_article_links(soup):
    """Extract Morning Brew article URLs from homepage"""

    article_links = []
    seen = set()

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if href.startswith("/stories/"):
            full_url = urljoin(MORNINGBREW_URL, href)

            if full_url not in seen:
                seen.add(full_url)
                article_links.append(full_url)

    return article_links

def parse_article(article_url):
    """Morning Brew article -> Standard article dictionary"""

    html = fetch_page(article_url)
    soup = BeautifulSoup(html, "html.parser")

    json_ld_element = soup.find("script", attrs={"type": "application/ld+json"})

    metadata = json.loads(json_ld_element.string)

    article_data = metadata[0]

    title = article_data.get("headline")
    url = article_data.get("url", article_url)
    published = article_data.get("datePublished")
    description = article_data.get("description")

    authors = article_data.get("author", [])
    author = (
        authors[0].get("name")
        if authors
        else None
    )

    article_element = soup.find("article")

    content = (
        article_element.get_text(" ", strip=True)
        if article_element
        else ""
    )

    return make_article(
        source = "Morning Brew",
        title = title,
        url = url,
        guid = url,
        published = published,
        author = author,
        categories = [],
        description = description,
        content = content
    )

def scrape_morningbrew():
    """Scrape Morning Brew articles"""

    html = fetch_page(MORNINGBREW_URL)
    soup = BeautifulSoup(html, "html.parser")

    article_links = get_article_links(soup)

    articles = []

    for article_url in article_links:
        try:
            article = parse_article(article_url)
            articles.append(article)
        except requests.RequestException as error:
            print(f"Failed to scrape {article_url}: {error}")

    return articles

if __name__ == "__main__":
    articles = scrape_morningbrew()

    print(f"Found {len(articles)} articles")
    
    for article in articles:
        print(article["title"])