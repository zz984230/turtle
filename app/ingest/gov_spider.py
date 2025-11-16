"""政府官网/监管机构公告爬取

提供基础抓取（带重试与超时）、解析标题/正文与发布日期，并输出标准字典结构用于持久化。
"""

import re
import time
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.nlp.clean import clean_html

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def fetch(url: str, timeout: int = 10) -> str:
    """抓取页面 HTML

    参数
    - url: 页面地址
    - timeout: 请求超时秒数

    返回
    - str：若成功返回 HTML，否则返回空字符串
    """
    for i in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200:
                return r.text
        except Exception:
            time.sleep(2 ** i)
    return ''

def parse(url: str, html: str) -> Dict:
    """解析标题/正文与发布日期

    参数
    - url: 页面地址
    - html: 页面 HTML 文本

    返回
    - Dict：包含 `source, url, title, published_at, content`
    """
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.text.strip() if soup.title else ''
    text = clean_html(html)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    date = m.group(1) if m else ''
    return {'source': 'gov', 'url': url, 'title': title, 'published_at': date, 'content': text}

def crawl(urls: List[str]) -> List[Dict]:
    """批量抓取并解析页面

    参数
    - urls: 页面地址列表

    返回
    - List[Dict]：解析后的文档条目列表
    """
    items = []
    for u in urls:
        html = fetch(u)
        if html:
            items.append(parse(u, html))
    return items