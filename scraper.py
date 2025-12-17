import json
import time
import re
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm#hi
import config

def extract_assessment_details(soup: BeautifulSoup, url: str) -> Optional[Dict]:
    try:
        assessment = {
            'url': url,
            'name': '',
            'description': '',
            'test_type': '',
            'category': '',
            'duration': '',
            'skills': []
        }

        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            assessment['name'] = title_elem.get_text(strip=True)

        desc_elem = soup.find('div', class_=re.compile('description|content|overview', re.I))
        if desc_elem:
            assessment['description'] = desc_elem.get_text(strip=True)[:500]
        elif soup.find('p'):
            paragraphs = soup.find_all('p')[:3]
            assessment['description'] = ' '.join([p.get_text(strip=True) for p in paragraphs])[:500]

        meta_text = soup.get_text().lower()
        if 'personality' in meta_text or 'behavior' in meta_text:
            assessment['test_type'] = 'P'
        elif 'knowledge' in meta_text or 'skill' in meta_text or 'technical' in meta_text:
            assessment['test_type'] = 'K'
        elif 'cognitive' in meta_text:
            assessment['test_type'] = 'C'
        else:
            assessment['test_type'] = 'K'

        duration_match = re.search(r'(\d+)\s*(minute|min|hour|hr)', meta_text, re.I)
        if duration_match:
            assessment['duration'] = duration_match.group(0)

        return assessment if assessment['name'] else None

    except Exception as e:
        return None

def get_sitemap_urls(session: requests.Session) -> Set[str]:
    urls = set()
    try:
        sitemap_urls = [
            'https://www.shl.com/sitemap.xml',
            'https://www.shl.com/sitemap_index.xml',
            'https://www.shl.com/products-sitemap.xml'
        ]

        for sitemap_url in sitemap_urls:
            try:
                response = session.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    for loc in soup.find_all('loc'):
                        url = loc.get_text()
                        if 'product' in url.lower() or 'assessment' in url.lower():
                            urls.add(url)
            except:
                continue

        print(f"Found {len(urls)} URLs from sitemaps")
    except:
        pass

    return urls

def scrape_category_pages(session: requests.Session) -> Set[str]:
    urls = set()

    category_pages = [
        'https://www.shl.com/solutions/products/',
        'https://www.shl.com/products/assessments/',
        'https://www.shl.com/products/assessments/skills-and-simulations/',
        'https://www.shl.com/products/assessments/personality-and-behavior/',
        'https://www.shl.com/products/assessments/cognitive-ability/',
        'https://www.shl.com/solutions/products/product-catalog/',
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for page_url in category_pages:
        try:
            response = session.get(page_url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(pattern in href for pattern in ['product-catalog/view/', '/products/', 'assessment']):
                    if not href.startswith('http'):
                        href = 'https://www.shl.com' + href
                    if 'shl.com' in href:
                        urls.add(href)

            time.sleep(0.5)
        except:
            continue

    print(f"Found {len(urls)} URLs from category pages")
    return urls

def generate_url_patterns() -> Set[str]:
    urls = set()

    common_assessments = [
        'verify-interactive-', 'verify-g-plus', 'universal-competency-framework',
        'capp-assessment', 'motivational-questionnaire', 'occupational-personality-questionnaire',
        'saville-assessment', 'business-attitudes-questionnaire', 'sales-assessment',
        'customer-contact', 'mechanical-comprehension', 'spatial-reasoning',
        'numerical-reasoning', 'verbal-reasoning', 'logical-reasoning',
        'situational-judgement', 'emotional-intelligence', 'leadership-assessment'
    ]

    for name in common_assessments:
        urls.add(f'https://www.shl.com/solutions/products/product-catalog/view/{name}/')
        urls.add(f'https://www.shl.com/products/product-catalog/view/{name}/')

    return urls

def load_urls_from_training_data() -> List[str]:
    import pandas as pd

    try:
        df = pd.read_excel(config.TRAIN_DATA_FILE, sheet_name='Train-Set')
        urls = df['Assessment_url'].unique().tolist()
        print(f"Loaded {len(urls)} training URLs")
        return urls
    except:
        return []

def scrape_catalog_page(session: requests.Session) -> List[str]:
    print("Fetching catalog...")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = session.get(config.SHL_CATALOG_URL, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        assessment_urls = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'product-catalog/view/' in href or '/products/' in href:
                if not href.startswith('http'):
                    href = 'https://www.shl.com' + href
                assessment_urls.add(href)

        print(f"Found {len(assessment_urls)} URLs from main catalog")
        return list(assessment_urls)

    except:
        return []

def scrape_shl_catalog() -> List[Dict]:
    print("=" * 60)
    print("SHL Enhanced Scraper")
    print("=" * 60)

    session = requests.Session()
    all_urls = set()

    print("\nStrategy 1: Training data URLs")
    all_urls.update(load_urls_from_training_data())

    print("\nStrategy 2: Main catalog page")
    all_urls.update(scrape_catalog_page(session))

    print("\nStrategy 3: Sitemap")
    all_urls.update(get_sitemap_urls(session))

    print("\nStrategy 4: Category pages")
    all_urls.update(scrape_category_pages(session))

    print("\nStrategy 5: Common URL patterns")
    all_urls.update(generate_url_patterns())

    assessment_urls = list(all_urls)
    print(f"\nTotal unique URLs: {len(assessment_urls)}")

    if len(assessment_urls) < config.MIN_ASSESSMENTS:
        print(f"Warning: {len(assessment_urls)} < {config.MIN_ASSESSMENTS}")

    assessments = []
    print("\nScraping details...")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for url in tqdm(assessment_urls):
        try:
            response = session.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            assessment = extract_assessment_details(soup, url)

            if assessment and assessment['name']:
                assessments.append(assessment)

            time.sleep(0.5)

        except:
            continue

    print(f"\n{'=' * 60}")
    print(f"Successfully scraped {len(assessments)} assessments")
    print(f"{'=' * 60}")

    return assessments

def save_catalog(assessments: List[Dict], filename: str = None):
    if filename is None:
        filename = config.CATALOG_FILE

    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {filename}")

def main():
    assessments = scrape_shl_catalog()

    if assessments:
        save_catalog(assessments)

        print("\nStatistics:")
        print(f"  Total: {len(assessments)}")

        test_types = {}
        for a in assessments:
            tt = a.get('test_type', 'Unknown')
            test_types[tt] = test_types.get(tt, 0) + 1

        print("\n  Test types:")
        for tt, count in sorted(test_types.items()):
            print(f"    {tt}: {count}")
    else:
        print("\nNo assessments scraped")

if __name__ == "__main__":
    main()
