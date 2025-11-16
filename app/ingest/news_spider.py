import re
import time
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.nlp.clean import clean_html

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def fetch(url: str, timeout: int = 10) -> str:
    for i in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200:
                return r.text
        except Exception:
            time.sleep(2 ** i)
    return ''

def parse(url: str, html: str) -> Dict:
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.text.strip() if soup.title else ''
    text = clean_html(html)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    date = m.group(1) if m else ''
    return {'source': 'news', 'url': url, 'title': title, 'published_at': date, 'content': text}

def crawl(urls: List[str]) -> List[Dict]:
    items = []
    for u in urls:
        html = fetch(u)
        if html:
            items.append(parse(u, html))
    return items