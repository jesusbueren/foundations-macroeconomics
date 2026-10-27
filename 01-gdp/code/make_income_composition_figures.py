'''Create figures for the income approach to GDP.'''

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
CHAPTER_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = CHAPTER_DIR / 'data' / 'cache' / 'ameco-2026'
FIGURE_DIR = CHAPTER_DIR / 'slides' / 'figures'
sys.path.insert(0, str(REPO_ROOT))

from common.python.course_plot_style import (  # noqa: E402
    COURSE_BLUE,
    COURSE_ORANGE,
    PEER_BLUE,
    POINT_GREY,
    TEXT_GREY,
    apply_course_style,
    save_figure,
)


AMECO_URL = (
    'https://economy-finance.ec.europa.eu/document/download/'
    'fd885a67-e390-46fb-a6d0-bbc67d946ebf_en'
)
ZIP_PATH = CACHE_DIR / 'ameco-csv.zip'
CSV_PATH = CACHE_DIR / 'csv' / 'AMECO7.CSV'
COUNTRIES = ['Portugal', 'United States', 'France', 'Germany']
COLORS = {
    'Portugal': COURSE_ORANGE,
    'United States': COURSE_BLUE,
    'France': PEER_BLUE,
    'Germany': TEXT_GREY,
}
LABEL_Y = {
    'France': 67.4,
    'Portugal': 64.8,
    'Germany': 62.7,
    'United States': 58.2,
}


def ameco_csv() -> Path:
    '''Download and extract the official AMECO CSV release when needed.'''
    if CSV_PATH.exists():
        return CSV_PATH

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(AMECO_URL, timeout=90)
    response.raise_for_status()
    ZIP_PATH.write_bytes(response.content)

    extract_dir = CSV_PATH.parent
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as archive:
        archive.extractall(extract_dir)
    if not CSV_PATH.exists():
        raise FileNotFoundError('AMECO7.CSV was not found in the AMECO archive.')
    return CSV_PATH


def labor_share_data() -> pd.DataFrame:
    '''Return factor-cost adjusted wage shares through 2024.'''
    raw = pd.read_csv(ameco_csv(), encoding='cp1252', low_memory=False)
    data = raw.loc[
        raw['CODE'].str.endswith('.ALCD2', na=False)
        & raw['COUNTRY'].isin(COUNTRIES)
    ].copy()
    year_columns = [str(year) for year in range(1980, 2025)]
    data = data.melt(
        id_vars=['COUNTRY'],
        value_vars=year_columns,
        var_name='year',
        value_name='labor_share',
    )
    data['year'] = pd.to_numeric(data['year'])
    data['labor_share'] = pd.to_numeric(data['labor_share'], errors='coerce')
    data = data.dropna(subset=['labor_share']).sort_values(['COUNTRY', 'year'])
    data['labor_share_smoothed'] = data.groupby('COUNTRY')['labor_share'].transform(
        lambda values: values.rolling(3, min_periods=2).mean()
    )
    return data


def income_composition_data() -> pd.DataFrame:
    '''Return a 2024 decomposition of GDP by income component.'''
    raw = pd.read_csv(ameco_csv(), encoding='cp1252', low_memory=False)
    data = raw.loc[
        raw['CODE'].str.endswith(('.ALCD0', '.ALCD2'), na=False)
        & raw['COUNTRY'].isin(COUNTRIES),
        ['COUNTRY', 'CODE', '2024'],
    ].copy()
    data['measure'] = data['CODE'].str[-5:]
    data['2024'] = pd.to_numeric(data['2024'], errors='coerce')
    data = data.pivot(index='COUNTRY', columns='measure', values='2024')

    # ALCD0 is labor income as a share of market-price GDP. ALCD2 uses GDP at
    # factor cost. Their ratio identifies factor-cost GDP as a share of
    # market-price GDP, leaving net production taxes as the difference.
    data['Labor income'] = data['ALCD0']
    data['Net production taxes'] = 100 - 100 * data['ALCD0'] / data['ALCD2']
    data['Capital income'] = (
        100 - data['Labor income'] - data['Net production taxes']
    )
    return data.loc[COUNTRIES].reset_index()


def plot_income_composition(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.4))
    components = ['Labor income', 'Capital income', 'Net production taxes']
    colors = [COURSE_BLUE, COURSE_ORANGE, POINT_GREY]
    bottom = pd.Series(0.0, index=data.index)
    positions = range(len(data))

    for component, color in zip(components, colors):
        values = data[component]
        bars = ax.bar(
            positions,
            values,
            bottom=bottom,
            color=color,
            width=0.62,
            label=component,
        )
        for bar, value, start in zip(bars, values, bottom):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                start + value / 2,
                f'{value:.0f}%',
                ha='center',
                va='center',
                color='white' if component != 'Net production taxes' else '#374151',
                fontsize=11,
                fontweight='bold',
            )
        bottom = bottom + values

    ax.set_ylim(0, 100)
    ax.set_ylabel('Share of GDP at market prices')
    ax.set_xticks(list(positions), data['COUNTRY'])
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    ax.legend(
        loc='lower center',
        bbox_to_anchor=(0.5, 1.01),
        ncol=3,
        frameon=False,
        fontsize=10,
    )

    fig.text(
        0.01,
        0.018,
        (
            'Source: European Commission AMECO, Spring 2026; 2024 data. '
            'Labor income is adjusted for self-employment; capital income is '
            'the residual after net production taxes.'
        ),
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(left=0.09, right=0.98, top=0.84, bottom=0.17)
    save_figure(fig, FIGURE_DIR / 'income-approach-composition.pdf')
    plt.close(fig)


def plot_labor_share(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.6))

    ax.axhline(
        100 * 2 / 3,
        color='#9CA3AF',
        linewidth=1.2,
        linestyle=(0, (4, 4)),
        zorder=0,
    )
    ax.text(
        1980.5,
        67.2,
        'Two-thirds benchmark',
        color='#6B7280',
        fontsize=9,
        va='bottom',
    )

    for country in COUNTRIES:
        series = data.loc[data['COUNTRY'].eq(country)].copy()
        ax.plot(
            series['year'],
            series['labor_share_smoothed'],
            color=COLORS[country],
            linewidth=2.8 if country == 'Portugal' else 2.0,
            alpha=1.0 if country == 'Portugal' else 0.88,
        )
        endpoint = series.iloc[-1]
        endpoint_value = endpoint['labor_share_smoothed']
        ax.scatter(
            [endpoint['year']],
            [endpoint_value],
            color=COLORS[country],
            s=38,
            zorder=3,
        )
        ax.plot(
            [endpoint['year'], 2025.0],
            [endpoint_value, LABEL_Y[country]],
            color=COLORS[country],
            linewidth=0.9,
            alpha=0.75,
        )
        ax.text(
            2025.3,
            LABEL_Y[country],
            f'{country}  {endpoint_value:.1f}%',
            color=COLORS[country],
            fontsize=10,
            fontweight='bold' if country == 'Portugal' else 'normal',
            va='center',
        )

    ax.set_xlim(1979, 2034)
    ax.set_ylim(55, 78)
    ax.set_xticks([1980, 1990, 2000, 2010, 2020])
    ax.set_yticks([55, 60, 65, 70, 75])
    ax.set_ylabel('Adjusted labor share (% of factor income)')
    ax.grid(axis='y')
    ax.set_axisbelow(True)

    fig.text(
        0.01,
        0.018,
        (
            'Source: European Commission AMECO, Spring 2026. '
            'Adjusted wage share, total economy, percentage of GDP at factor '
            'cost; three-year moving average; data through 2024.'
        ),
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(left=0.09, right=0.96, top=0.96, bottom=0.15)
    save_figure(fig, FIGURE_DIR / 'income-labor-share-trends.pdf')
    plt.close(fig)


def main() -> None:
    apply_course_style()
    plot_income_composition(income_composition_data())
    data = labor_share_data()
    plot_labor_share(data)
    for country in COUNTRIES:
        series = data.loc[
            data['COUNTRY'].eq(country) & data['labor_share_smoothed'].notna()
        ]
        first = series.iloc[0]
        last = series.iloc[-1]
        first_year = int(first['year'])
        first_value = first['labor_share_smoothed']
        last_year = int(last['year'])
        last_value = last['labor_share_smoothed']
        print(
            f'{country}: {first_year} {first_value:.1f}% -> '
            f'{last_year} {last_value:.1f}%'
        )
    print(FIGURE_DIR / 'income-labor-share-trends.pdf')


if __name__ == '__main__':
    main()
