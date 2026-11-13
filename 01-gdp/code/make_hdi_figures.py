'''Create the HDI and component figures using the shared course style.'''

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from matplotlib.ticker import FuncFormatter, NullLocator


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


YEAR = 2023
DATA_FILENAME = 'HDR25_Composite_indices_complete_time_series.csv'
DATA_URL = f'https://hdr.undp.org/sites/default/files/2025_HDR/{DATA_FILENAME}'
PEER_COUNTRIES = ['PRT', 'USA', 'DEU', 'BRA', 'CHN', 'IND', 'NGA', 'JPN']
LABEL_OFFSETS = {
    ('life_expectancy', 'PRT'): (-7, -15),
    ('life_expectancy', 'USA'): (7, -15),
    ('life_expectancy', 'ISL'): (7, 4),
    ('life_expectancy', 'SMR'): (-7, 7),
    ('expected_schooling', 'PRT'): (-7, -15),
    ('expected_schooling', 'USA'): (7, -15),
    ('expected_schooling', 'ISL'): (7, 4),
    ('expected_schooling', 'GRC'): (-7, 7),
    ('hdi', 'PRT'): (-7, -16),
    ('hdi', 'USA'): (7, -14),
    ('hdi', 'DEU'): (-7, 8),
    ('hdi', 'BRA'): (-7, 6),
    ('hdi', 'CHN'): (7, -18),
    ('hdi', 'IND'): (7, -16),
    ('hdi', 'NGA'): (7, -15),
    ('hdi', 'JPN'): (-7, 2),
    ('hdi', 'ISL'): (7, 13),
    ('hdi', 'SSD'): (7, -14),
}


def load_data() -> pd.DataFrame:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / DATA_FILENAME
    if not path.exists():
        response = requests.get(DATA_URL, timeout=90)
        response.raise_for_status()
        path.write_bytes(response.content)

    # UNDP distributes this release as a Windows-1252 CSV.
    frame = pd.read_csv(path, encoding='cp1252', low_memory=False)
    columns = {
        'iso3': 'country_code',
        'country': 'country_name',
        f'hdi_rank_{YEAR}': 'hdi_rank',
        f'hdi_{YEAR}': 'hdi',
        f'le_{YEAR}': 'life_expectancy',
        f'eys_{YEAR}': 'expected_schooling',
        f'gnipc_{YEAR}': 'gni_pc',
    }
    # A published HDI rank excludes regional aggregates and unranked territories.
    data = frame.loc[frame[f'hdi_rank_{YEAR}'].notna(), list(columns)].rename(
        columns=columns
    )
    values = ['hdi', 'life_expectancy', 'expected_schooling', 'gni_pc']
    data = data.replace([np.inf, -np.inf], np.nan).dropna(subset=values)
    data = data.loc[data[values].gt(0).all(axis=1)].copy()
    if data.empty or data['country_code'].duplicated().any():
        raise RuntimeError('UNDP data must contain one observation per country.')
    return data.sort_values('country_name').reset_index(drop=True)


def extreme_countries(data: pd.DataFrame, column: str) -> list[str]:
    return data.loc[
        [data[column].idxmin(), data[column].idxmax()], 'country_code'
    ].tolist()


def money_tick(value, _position) -> str:
    return f'${value / 1_000:g}k' if value >= 1_000 else f'${value:g}'


def plot_relationship(ax, data: pd.DataFrame, column: str, *, compact=False):
    ax.scatter(
        data['gni_pc'], data[column], s=24 if compact else 27,
        color=POINT_GREY, alpha=0.72, edgecolor='none', zorder=1,
    )
    target = data[column].to_numpy()
    if column == 'hdi':
        target = np.log(target / (1 - target))
    coefficients = np.polyfit(np.log10(data['gni_pc']), target, deg=2)
    grid = np.geomspace(data['gni_pc'].min(), data['gni_pc'].max(), 250)
    fitted = np.polyval(coefficients, np.log10(grid))
    if column == 'hdi':
        fitted = 1 / (1 + np.exp(-fitted))
    ax.plot(
        grid, fitted,
        color=COURSE_BLUE, linewidth=2.2, label='Descriptive fit', zorder=2,
    )

    countries = ['PRT', 'USA'] if compact else PEER_COUNTRIES
    countries = list(dict.fromkeys(
        countries + extreme_countries(data, 'hdi') + extreme_countries(data, column)
    ))
    for code in countries:
        row = data.loc[data['country_code'].eq(code)].iloc[0]
        is_portugal = code == 'PRT'
        color = COURSE_ORANGE if is_portugal else COURSE_BLUE
        ax.scatter(
            [row['gni_pc']], [row[column]], s=115 if is_portugal else 48,
            marker='*' if is_portugal else 'o',
            color=COURSE_ORANGE if is_portugal else PEER_BLUE,
            edgecolor='white', linewidth=0.7, zorder=4,
        )
        offset = LABEL_OFFSETS.get((column, code), (7, 6))
        name = row['country_name']
        if column == 'hdi' and code in extreme_countries(data, 'hdi'):
            name += f" ({row['hdi']:.3f})"
        ax.annotate(
            name, (row['gni_pc'], row[column]), xytext=offset,
            textcoords='offset points', ha='left' if offset[0] >= 0 else 'right',
            fontsize=8.5, color=color,
            fontweight='bold' if is_portugal else 'normal', zorder=5,
        )

    ax.set_xscale('log')
    ax.set_xlim(500, 220_000)
    ax.set_xticks(
        [1_000, 5_000, 20_000, 100_000] if compact
        else [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000]
    )
    ax.xaxis.set_major_formatter(FuncFormatter(money_tick))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.grid(axis='both', which='major')
    ax.set_axisbelow(True)


def add_source(fig, count: int) -> None:
    fig.text(
        0.01, 0.018,
        f'Source: UNDP Human Development Report 2025. {YEAR} observations; '
        f'N = {count} countries. Income is in constant 2021 international dollars.',
        ha='left', va='bottom', fontsize=8, color='#6B7280',
    )


def plot_components(data: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 5.6))
    plot_relationship(axes[0], data, 'life_expectancy', compact=True)
    axes[0].set_ylabel('Life expectancy at birth (years)')
    axes[0].set_ylim(51, 90)
    plot_relationship(axes[1], data, 'expected_schooling', compact=True)
    axes[1].set_ylabel('Expected years of schooling')
    axes[1].set_ylim(4, 23)
    for ax in axes:
        ax.set_xlabel('GNI per capita, PPP (log scale)')
    fig.legend(
        *axes[0].get_legend_handles_labels(), loc='upper center',
        bbox_to_anchor=(0.5, 0.99), frameon=False, fontsize=9,
    )
    add_source(fig, len(data))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=0.20, wspace=0.25)
    save_figure(fig, FIGURE_DIR / 'gni_life_edu_us_pt.pdf')
    plt.close(fig)


def plot_hdi(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    plot_relationship(ax, data, 'hdi')
    ax.set_xlabel('GNI per capita, PPP (constant 2021 international dollars; log scale)')
    ax.set_ylabel('Human Development Index (HDI)')
    ax.set_ylim(0.34, 1.04)
    ax.set_yticks(np.arange(0.4, 1.01, 0.1))
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    add_source(fig, len(data))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.97, bottom=0.20)
    save_figure(fig, FIGURE_DIR / 'gni_hdi_us_pt.pdf')
    plt.close(fig)


def main() -> None:
    apply_course_style()
    data = load_data()
    plot_components(data)
    plot_hdi(data)
    for name in ('gni_life_edu_us_pt.pdf', 'gni_hdi_us_pt.pdf'):
        print(FIGURE_DIR / name)


if __name__ == '__main__':
    main()
