## For Re-usable sections of scraping code

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0"
        "(Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36"
        "(KHTML, like Gecko)"
        "Chrome/131.0 Safari/537.36"
    )
}

def fetch_url(url):
    response = SESSION.get(url, timeout = 30)
    response.raise_for_status()

    return response.text

def fetch_feed(url):
    return fetch_url(url)

def fetch_page(url):
    return fetch_url(url)

def create_session():
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504], allowed_methods=["GET"])

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()

    session.headers.update(DEFAULT_HEADERS)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

###
SESSION = create_session()
###

def clean_html(html):
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    return soup.get_text(" ", strip=True)

def make_article(
        source, 
        title, 
        url,
        published,
        guid=None,
        author=None,
        categories=None,
        description="",
        content=""
):
    return {
        "source": source,
        "title": title, 
        "url": url,
        "guid": guid or url,
        "published": published,
        "author": author,
        "categories": categories or [],
        "description": description or "",
        "content": content or ""
    }