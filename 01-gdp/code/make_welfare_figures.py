'''Create the welfare-motivation figures used at the start of Chapter 1.'''

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
CHAPTER_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = CHAPTER_DIR / 'data' / 'cache'
FIGURE_DIR = CHAPTER_DIR / 'slides' / 'figures'
sys.path.insert(0, str(REPO_ROOT))

from common.python.course_plot_style import (  # noqa: E402
    COURSE_BLUE,
    COURSE_ORANGE,
    PEER_BLUE,
    POINT_GREY,
    apply_course_style,
    save_figure,
)


WDI_API = 'https://api.worldbank.org/v2'
WHR_URL = 'https://files.worldhappiness.report/WHR26_Data_Figure_2.1.xlsx'
YEARS = '2022:2025'
INDICATORS = {
    'gdp_pc': 'NY.GDP.PCAP.PP.KD',
    'life_expectancy': 'SP.DYN.LE00.IN',
    'under_five_mortality': 'SH.DYN.MORT',
    'consumption': 'NE.CON.PRVT.PP.KD',
    'population': 'SP.POP.TOTL',
}
LABEL_COUNTRIES = [
    'Portugal',
    'United States',
    'Germany',
    'Brazil',
    'China',
    'India',
    'Nigeria',
    'Japan',
]
LABEL_OFFSETS = {
    'Portugal': (7, -13),
    'United States': (7, 5),
    'Germany': (7, -13),
    'Brazil': (7, -13),
    'China': (7, 5),
    'India': (7, -13),
    'Nigeria': (7, 5),
    'Japan': (7, 5),
    'Costa Rica': (7, 5),
}
SERIES_LABEL_OFFSETS = {
    ('life_expectancy', 'Germany'): (7, -18),
    ('life_expectancy', 'United States'): (7, 9),
    ('life_expectancy', 'San Marino'): (7, -14),
    ('life_evaluation', 'Germany'): (7, -13),
    ('life_evaluation', 'United States'): (7, 9),
    ('life_evaluation', 'Afghanistan'): (7, 7),
    ('life_evaluation', 'Finland'): (7, -14),
    ('under_five_mortality', 'Portugal'): (7, -17),
    ('under_five_mortality', 'Japan'): (7, 9),
    ('under_five_mortality', 'San Marino'): (7, 9),
    ('consumption_pc', 'Portugal'): (7, -17),
    ('consumption_pc', 'Japan'): (7, 9),
    ('consumption_pc', 'Germany'): (7, -13),
    ('consumption_pc', 'Brazil'): (7, -14),
    ('consumption_pc', 'China'): (7, 7),
    ('consumption_pc', 'Burundi'): (7, 7),
}
COUNTRY_ALIASES = {
    'Congo (Brazzaville)': 'Congo, Rep.',
    'Congo (Kinshasa)': 'Congo, Dem. Rep.',
    'Egypt': 'Egypt, Arab Rep.',
    'Gambia': 'Gambia, The',
    'Hong Kong S.A.R. of China': 'Hong Kong SAR, China',
    'Iran': 'Iran, Islamic Rep.',
    'Kyrgyzstan': 'Kyrgyz Republic',
    'Laos': 'Lao PDR',
    'Russia': 'Russian Federation',
    'Slovakia': 'Slovak Republic',
    'South Korea': 'Korea, Rep.',
    'State of Palestine': 'West Bank and Gaza',
    'Venezuela': 'Venezuela, RB',
    'Yemen': 'Yemen, Rep.',
}


def session() -> requests.Session:
    client = requests.Session()
    client.headers.update(
        {'User-Agent': 'foundations-macroeconomics-course/1.0'}
    )
    return client


def cached_json(name: str, url: str):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / name
    if not path.exists():
        response = session().get(url, timeout=90)
        response.raise_for_status()
        path.write_text(response.text, encoding='utf-8')
    return json.loads(path.read_text(encoding='utf-8'))


def cached_file(name: str, url: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / name
    if not path.exists():
        response = session().get(url, timeout=90)
        response.raise_for_status()
        path.write_bytes(response.content)
    return path


def real_country_codes() -> set[str]:
    payload = cached_json(
        'wdi-countries.json',
        f'{WDI_API}/country?format=json&per_page=400',
    )
    return {
        item['id']
        for item in payload[1]
        if item.get('region', {}).get('value') not in {'', 'Aggregates'}
    }


def wdi_series(label: str) -> pd.DataFrame:
    indicator = INDICATORS[label]
    cache_years = YEARS.replace(':', '-')
    payload = cached_json(
        f'wdi-{indicator}-{cache_years}.json',
        (
            f'{WDI_API}/country/all/indicator/{indicator}'
            f'?format=json&per_page=20000&date={YEARS}'
        ),
    )
    valid_codes = real_country_codes()
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
                    label: float(value),
                }
            )
    return pd.DataFrame(rows)


def latest_common(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    data = left.merge(
        right.drop(columns='country_name'),
        on=['country_code', 'year'],
        how='inner',
    )
    return (
        data.sort_values('year', ascending=False)
        .drop_duplicates('country_code')
        .sort_values('country_name')
        .reset_index(drop=True)
    )


def normalize_name(value: str) -> str:
    text = unicodedata.normalize('NFKD', value)
    text = ''.join(char for char in text if not unicodedata.combining(char))
    return re.sub(r'[^a-z0-9]+', '', text.lower())


def prepare_happiness(gdp: pd.DataFrame) -> pd.DataFrame:
    path = cached_file('WHR26_Data_Figure_2.1.xlsx', WHR_URL)
    happiness = pd.read_excel(path, sheet_name=0)
    happiness = happiness.loc[
        happiness['Year'].eq(2025),
        ['Country name', 'Life evaluation (3-year average)'],
    ].copy()
    happiness = happiness.rename(
        columns={'Life evaluation (3-year average)': 'life_evaluation'}
    )
    happiness['matched_name'] = happiness['Country name'].map(
        lambda value: COUNTRY_ALIASES.get(value, value)
    )
    happiness['join_name'] = happiness['matched_name'].map(normalize_name)

    recent_gdp = (
        gdp.sort_values('year', ascending=False)
        .drop_duplicates('country_code')
        .copy()
    )
    recent_gdp['join_name'] = recent_gdp['country_name'].map(normalize_name)
    data = happiness.merge(
        recent_gdp[['country_code', 'country_name', 'year', 'gdp_pc', 'join_name']],
        on='join_name',
        how='inner',
    )
    return data.drop(columns=['matched_name', 'join_name']).reset_index(drop=True)


def prepare_consumption(
    gdp: pd.DataFrame,
    consumption: pd.DataFrame,
    population: pd.DataFrame,
) -> pd.DataFrame:
    data = gdp.merge(
        consumption.drop(columns='country_name'),
        on=['country_code', 'year'],
        how='inner',
    ).merge(
        population.drop(columns='country_name'),
        on=['country_code', 'year'],
        how='inner',
    )
    data = (
        data.sort_values('year', ascending=False)
        .drop_duplicates('country_code')
        .copy()
    )
    data['consumption_pc'] = data['consumption'] / data['population']
    return data.reset_index(drop=True)


def money_tick(value, _position) -> str:
    if value >= 1_000:
        return f'${value / 1_000:g}k'
    return f'${value:g}'


def number_tick(value, _position) -> str:
    return f'{value:g}'


def descriptive_fit(ax, x, y, log_y: bool) -> None:
    log_x = np.log10(x)
    target = np.log10(y) if log_y else y
    coefficients = np.polyfit(log_x, target, deg=2)
    grid = np.geomspace(x.min(), x.max(), 250)
    fitted = np.polyval(coefficients, np.log10(grid))
    if log_y:
        fitted = 10**fitted
    ax.plot(
        grid,
        fitted,
        color=COURSE_BLUE,
        linewidth=2.2,
        label='Descriptive fit',
        zorder=2,
    )


def add_country_labels(ax, data, y_column: str, extra_labels=()) -> None:
    extreme_countries = [
        data.loc[data[y_column].idxmin(), 'country_name'],
        data.loc[data[y_column].idxmax(), 'country_name'],
    ]
    countries = list(
        dict.fromkeys(LABEL_COUNTRIES + list(extra_labels) + extreme_countries)
    )
    for country in countries:
        row = data.loc[data['country_name'].eq(country)]
        if row.empty:
            continue
        x_value = row.iloc[0]['gdp_pc']
        y_value = row.iloc[0][y_column]
        is_portugal = country == 'Portugal'
        ax.scatter(
            [x_value],
            [y_value],
            s=115 if is_portugal else 48,
            marker='*' if is_portugal else 'o',
            color=COURSE_ORANGE if is_portugal else PEER_BLUE,
            edgecolor='white',
            linewidth=0.7,
            zorder=4,
        )
        ax.annotate(
            country,
            (x_value, y_value),
            xytext=SERIES_LABEL_OFFSETS.get(
                (y_column, country),
                LABEL_OFFSETS.get(country, (7, 5)),
            ),
            textcoords='offset points',
            fontsize=8.5,
            color=COURSE_ORANGE if is_portugal else COURSE_BLUE,
            fontweight='bold' if is_portugal else 'normal',
            zorder=5,
        )


def plot_relationship(
    data: pd.DataFrame,
    y_column: str,
    y_label: str,
    filename: str,
    source: str,
    *,
    log_y: bool = False,
    y_limits=None,
    extra_labels=(),
) -> None:
    clean = data.replace([np.inf, -np.inf], np.nan).dropna(
        subset=['gdp_pc', y_column]
    )
    clean = clean.loc[(clean['gdp_pc'] > 0) & (clean[y_column] > 0)].copy()

    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    ax.scatter(
        clean['gdp_pc'],
        clean[y_column],
        s=27,
        color=POINT_GREY,
        alpha=0.72,
        edgecolor='none',
        zorder=1,
    )
    descriptive_fit(
        ax,
        clean['gdp_pc'].to_numpy(),
        clean[y_column].to_numpy(),
        log_y=log_y,
    )
    add_country_labels(ax, clean, y_column, extra_labels)

    ax.set_xscale('log')
    ax.set_xlim(800, 140_000)
    ax.set_xticks([1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000])
    ax.xaxis.set_major_formatter(FuncFormatter(money_tick))
    ax.set_xlabel('GDP per capita, PPP (constant 2021 international dollars)')
    ax.set_ylabel(y_label)
    if log_y:
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(FuncFormatter(number_tick))
    if y_limits is not None:
        ax.set_ylim(*y_limits)
    ax.grid(axis='both', which='major')
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    fig.text(
        0.01,
        0.018,
        f'Source: {source}. Latest available observations; N = {len(clean)}.',
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(left=0.09, right=0.98, top=0.97, bottom=0.22)
    save_figure(fig, FIGURE_DIR / filename)
    plt.close(fig)


def main() -> None:
    apply_course_style()
    gdp = wdi_series('gdp_pc')
    life = latest_common(gdp, wdi_series('life_expectancy'))
    mortality = latest_common(gdp, wdi_series('under_five_mortality'))
    consumption = prepare_consumption(
        gdp,
        wdi_series('consumption'),
        wdi_series('population'),
    )
    happiness = prepare_happiness(gdp)

    plot_relationship(
        life,
        'life_expectancy',
        'Life expectancy at birth (years)',
        'welfare-life-expectancy.pdf',
        'World Bank World Development Indicators',
        y_limits=(48, 87),
    )
    plot_relationship(
        happiness,
        'life_evaluation',
        'Average life evaluation (0--10)',
        'welfare-life-evaluation.pdf',
        'World Happiness Report 2026 and World Bank',
        y_limits=(1.2, 8.2),
        extra_labels=('Costa Rica',),
    )
    plot_relationship(
        mortality,
        'under_five_mortality',
        'Under-five deaths per 1,000 live births (log scale)',
        'welfare-under-five-mortality.pdf',
        'World Bank World Development Indicators',
        log_y=True,
        y_limits=(1.0, 160),
    )
    plot_relationship(
        consumption,
        'consumption_pc',
        'Household consumption per person (log scale)',
        'welfare-consumption.pdf',
        'World Bank World Development Indicators',
        log_y=True,
        y_limits=(500, 80_000),
    )

    for name in [
        'welfare-life-expectancy.pdf',
        'welfare-life-evaluation.pdf',
        'welfare-under-five-mortality.pdf',
        'welfare-consumption.pdf',
    ]:
        print(FIGURE_DIR / name)


if __name__ == '__main__':
    main()
