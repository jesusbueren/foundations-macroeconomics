'''Small reusable helpers for World Bank Indicators data.'''

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests


API_ROOT = 'https://api.worldbank.org/v2'


def _client() -> requests.Session:
    client = requests.Session()
    client.headers.update(
        {'User-Agent': 'foundations-macroeconomics-course/1.0'}
    )
    return client


def _cached_json(cache_dir: Path, filename: str, url: str):
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / filename
    if not path.exists():
        response = _client().get(url, timeout=90)
        response.raise_for_status()
        path.write_text(response.text, encoding='utf-8')
    return json.loads(path.read_text(encoding='utf-8'))


def country_codes(cache_dir: Path) -> set[str]:
    '''Return ISO3 codes for countries, excluding World Bank aggregates.'''
    payload = _cached_json(
        cache_dir,
        'wdi-countries.json',
        f'{API_ROOT}/country?format=json&per_page=400',
    )
    return {
        item['id']
        for item in payload[1]
        if item.get('region', {}).get('value') not in {'', 'Aggregates'}
    }


def indicator(
    indicator_code: str,
    value_name: str,
    cache_dir: Path,
    years: str,
) -> pd.DataFrame:
    '''Download one indicator and return a tidy country-year table.'''
    cache_years = years.replace(':', '-')
    payload = _cached_json(
        cache_dir,
        f'wdi-{indicator_code}-{cache_years}.json',
        (
            f'{API_ROOT}/country/all/indicator/{indicator_code}'
            f'?format=json&per_page=20000&date={years}'
        ),
    )
    valid_codes = country_codes(cache_dir)
    rows = []
    for item in payload[1]:
        code = item.get('countryiso3code')
        value = item.get('value')
        if code in valid_codes and value is not None:
            rows.append(
                {
                    'country_code': code,
                    'country_name': item['country']['value'],
                    'year': int(item['date']),
                    value_name: float(value),
                }
            )
    return pd.DataFrame(rows)
