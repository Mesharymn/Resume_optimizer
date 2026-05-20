"""Best-effort Saudi job search helper.

This module builds search URLs for common job boards used in Saudi Arabia and
tries to extract public job cards when possible. Some websites may block bots,
change their HTML, or require login. In those cases, the module still returns
search links so the user can continue manually.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = Path('data')
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; ResumeOptimizer/1.0; +https://github.com/Mesharymn/Resume_optimizer)',
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
}


@dataclass
class JobResult:
    title: str
    company: str
    location: str
    url: str
    source: str
    description: str = ''
    posted_date: str = ''


JOB_BOARD_URLS = {
    'LinkedIn': 'https://www.linkedin.com/jobs/search/?keywords={query}&location={location}',
    'Bayt': 'https://www.bayt.com/en/saudi-arabia/jobs/{query}-jobs/',
    'Naukrigulf': 'https://www.naukrigulf.com/{query}-jobs-in-saudi-arabia',
    'Indeed Saudi': 'https://sa.indeed.com/jobs?q={query}&l={location}',
    'GulfTalent': 'https://www.gulftalent.com/saudi-arabia/jobs/title/{query}',
    'Foundit Gulf': 'https://www.founditgulf.com/search/{query}-jobs-in-saudi-arabia',
}


def build_search_url(source: str, query: str, location: str = 'Saudi Arabia') -> str:
    query_slug = quote_plus(query).replace('+', '-')
    query_plus = quote_plus(query)
    location_plus = quote_plus(location)

    template = JOB_BOARD_URLS[source]

    if source in {'Bayt', 'Naukrigulf', 'GulfTalent', 'Foundit Gulf'}:
        return template.format(query=query_slug, location=location_plus)

    return template.format(query=query_plus, location=location_plus)


def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def absolute_url(base_url: str, href: str) -> str:
    if not href:
        return base_url
    if href.startswith('http'):
        return href
    if href.startswith('/'):
        domain = re.match(r'https?://[^/]+', base_url)
        return f"{domain.group(0)}{href}" if domain else href
    return href


def fetch_page(url: str) -> BeautifulSoup | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception:
        return None


def parse_generic_jobs(source: str, url: str, max_results: int = 10) -> List[JobResult]:
    soup = fetch_page(url)

    if soup is None:
        return []

    results: List[JobResult] = []

    cards = soup.find_all(['article', 'li', 'div'], limit=300)

    for card in cards:
        if len(results) >= max_results:
            break

        link = card.find('a', href=True)
        text = clean_text(card.get_text(' '))

        if not link or len(text) < 40:
            continue

        title = clean_text(link.get_text(' '))

        if not title or len(title) < 3:
            continue

        href = absolute_url(url, link.get('href'))

        lower_text = text.lower()
        job_like_terms = ['job', 'career', 'apply', 'full time', 'remote', 'riyadh', 'jeddah', 'dammam', 'saudi']

        if not any(term in lower_text for term in job_like_terms):
            continue

        results.append(
            JobResult(
                title=title[:120],
                company='',
                location='Saudi Arabia',
                url=href,
                source=source,
                description=text[:500],
            )
        )

    return deduplicate_jobs(results)


def deduplicate_jobs(jobs: List[JobResult]) -> List[JobResult]:
    seen = set()
    unique_jobs = []

    for job in jobs:
        key = (job.title.lower(), job.url)
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs


def search_jobs(query: str, location: str = 'Saudi Arabia', max_per_source: int = 10) -> List[JobResult]:
    all_jobs: List[JobResult] = []

    for source in JOB_BOARD_URLS:
        url = build_search_url(source, query, location)
        jobs = parse_generic_jobs(source, url, max_per_source=max_per_source)

        if jobs:
            all_jobs.extend(jobs)
        else:
            all_jobs.append(
                JobResult(
                    title=f'Manual search: {query}',
                    company='',
                    location=location,
                    url=url,
                    source=source,
                    description='Live extraction was unavailable. Open the source search link manually.',
                )
            )

    return all_jobs


def save_jobs_to_csv(jobs: List[JobResult], output_file: str = 'data/saudi_jobs.csv') -> Path:
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)

    with output_path.open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=list(asdict(jobs[0]).keys()) if jobs else ['title', 'company', 'location', 'url', 'source', 'description', 'posted_date'])
        writer.writeheader()
        for job in jobs:
            writer.writerow(asdict(job))

    return output_path


if __name__ == '__main__':
    jobs = search_jobs('data analyst', 'Riyadh', max_per_source=5)
    path = save_jobs_to_csv(jobs)
    print(f'Saved {len(jobs)} jobs to {path}')
