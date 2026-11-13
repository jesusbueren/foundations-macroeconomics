'''Small reusable helpers for Federal Reserve Economic Data (FRED).'''

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests


def series(
    series_id: str,
    value_name: str,
    cache_dir: Path,
) -> pd.DataFrame:
    '''Download one FRED series and return a date-value table.'''
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f'fred-{series_id}.csv'
    if not cache_path.exists():
        response = requests.get(
            'https://fred.stlouisfed.org/graph/fredgraph.csv',
            params={'id': series_id},
            timeout=90,
            headers={'User-Agent': 'foundations-macroeconomics-course/1.0'},
        )
        response.raise_for_status()
        cache_path.write_bytes(response.content)

    data = pd.read_csv(cache_path, na_values='.')
    date_column = data.columns[0]
    data = data.rename(
        columns={date_column: 'date', series_id: value_name}
    )
    data['date'] = pd.to_datetime(data['date'])
    data[value_name] = pd.to_numeric(data[value_name], errors='coerce')
    return data[['date', value_name]].dropna()
