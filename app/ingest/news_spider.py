"""主流媒体新闻爬取

提供基础抓取（重试/超时）、解析标题/正文与发布日期，并输出标准字典结构用于持久化与分析。
"""

import re
import time
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.nlp.clean import clean_html

HEADERS = {'User-Agent': 'Mozilla/5.0'}

class NewsSpider:
    """主流媒体新闻爬虫（面向对象）"""

    def __init__(self):
        self.headers = HEADERS

    def fetch(self, url: str, timeout: int = 10) -> str:
        for i in range(3):
            try:
                r = requests.get(url, headers=self.headers, timeout=timeout)
                if r.status_code == 200:
                    return r.text
            except Exception:
                time.sleep(2 ** i)
        return ''

    def parse(self, url: str, html: str) -> Dict:
        soup = BeautifulSoup(html, 'lxml')
        title = soup.title.text.strip() if soup.title else ''
        text = clean_html(html)
        m = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        date = m.group(1) if m else ''
        return {'source': 'news', 'url': url, 'title': title, 'published_at': date, 'content': text}

    def crawl(self, urls: List[str]) -> List[Dict]:
        items = []
        for u in urls:
            html = self.fetch(u)
            if html:
                items.append(self.parse(u, html))
        return items

def fetch(url: str, timeout: int = 10) -> str:
    """抓取页面 HTML（含指数退避重试）"""
    for i in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200:
                return r.text
        except Exception:
            time.sleep(2 ** i)
    return ''

def parse(url: str, html: str) -> Dict:
    """解析标题、正文与发布日期并结构化输出"""
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.text.strip() if soup.title else ''
    text = clean_html(html)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    date = m.group(1) if m else ''
    return {'source': 'news', 'url': url, 'title': title, 'published_at': date, 'content': text}

def crawl(urls: List[str]) -> List[Dict]:
    """批量抓取并解析新闻页面"""
    items = []
    for u in urls:
        html = fetch(u)
        if html:
            items.append(parse(u, html))
    return items