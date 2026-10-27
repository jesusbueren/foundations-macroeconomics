'''Create the production-approach GDP composition figures.'''

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
from common.python.world_bank import indicator  # noqa: E402


YEARS = '2018:2025'
INDICATORS = {
    'gdp_pc': 'NY.GDP.PCAP.PP.KD',
    'agriculture': 'NV.AGR.TOTL.ZS',
    'industry': 'NV.IND.TOTL.ZS',
    'manufacturing': 'NV.IND.MANF.ZS',
    'services': 'NV.SRV.TOTL.ZS',
}
COUNTRY_ORDER = ['PRT', 'USA', 'DEU', 'FRA']
COUNTRY_LABELS = {
    'PRT': 'Portugal',
    'USA': 'United States',
    'DEU': 'Germany',
    'FRA': 'France',
}
SECTOR_LABELS = {
    'agriculture': 'Agriculture',
    'industry': 'Industry',
    'services': 'Services',
}
SECTOR_COLORS = {
    'agriculture': '#6B8E23',
    'industry': COURSE_ORANGE,
    'services': COURSE_BLUE,
}
LABEL_COUNTRIES = [
    'Portugal',
    'United States',
    'Germany',
    'France',
    'China',
    'India',
    'Nigeria',
]
PANEL_LABEL_COUNTRIES = {
    'agriculture': [
        'Portugal',
        'United States',
        'China',
        'India',
        'Nigeria',
    ],
    'manufacturing': [
        'Portugal',
        'United States',
        'Germany',
        'China',
        'India',
    ],
    'services': LABEL_COUNTRIES,
}
LABEL_POSITIONS = {
    ('agriculture', 'Portugal'): ((0, 12), 'center'),
    ('agriculture', 'United States'): ((0, 20), 'center'),
    ('agriculture', 'Germany'): ((0, 12), 'center'),
    ('agriculture', 'France'): ((0, 28), 'center'),
    ('agriculture', 'China'): ((-7, 7), 'right'),
    ('agriculture', 'India'): ((7, -13), 'left'),
    ('agriculture', 'Nigeria'): ((7, 7), 'left'),
    ('manufacturing', 'Portugal'): ((7, -13), 'left'),
    ('manufacturing', 'United States'): ((0, 22), 'center'),
    ('manufacturing', 'Germany'): ((7, 7), 'left'),
    ('manufacturing', 'China'): ((7, 7), 'left'),
    ('manufacturing', 'India'): ((0, -18), 'center'),
    ('services', 'Portugal'): ((0, 10), 'center'),
    ('services', 'United States'): ((-7, 9), 'right'),
    ('services', 'Germany'): ((0, -16), 'center'),
    ('services', 'France'): ((-7, 9), 'right'),
    ('services', 'China'): ((7, 7), 'left'),
    ('services', 'India'): ((7, -13), 'left'),
    ('services', 'Nigeria'): ((7, 7), 'left'),
}


def merge_same_year(frames: list[pd.DataFrame]) -> pd.DataFrame:
    data = frames[0].copy()
    for frame in frames[1:]:
        data = data.merge(
            frame.drop(columns='country_name'),
            on=['country_code', 'year'],
            how='inner',
        )
    return data


def selected_country_composition(
    agriculture: pd.DataFrame,
    industry: pd.DataFrame,
    services: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    data = merge_same_year([agriculture, industry, services])
    data = data.loc[data['country_code'].isin(COUNTRY_ORDER)].copy()
    coverage = data.groupby('year')['country_code'].nunique()
    valid_years = coverage.loc[coverage.eq(len(COUNTRY_ORDER))].index
    if valid_years.empty:
        raise RuntimeError('No common year is available for the selected countries.')
    year = int(valid_years.max())
    data = data.loc[data['year'].eq(year)].set_index('country_code')
    data = data.loc[COUNTRY_ORDER].reset_index()
    sectors = ['agriculture', 'industry', 'services']
    total_value_added = data[sectors].sum(axis=1)
    data[sectors] = data[sectors].div(total_value_added, axis=0) * 100
    return data, year


def latest_relationship(
    gdp: pd.DataFrame,
    sector: pd.DataFrame,
) -> pd.DataFrame:
    data = merge_same_year([gdp, sector])
    return (
        data.sort_values('year', ascending=False)
        .drop_duplicates('country_code')
        .sort_values('country_name')
        .reset_index(drop=True)
    )


def money_tick(value, _position) -> str:
    if value >= 1_000:
        return f'${value / 1_000:g}k'
    return f'${value:g}'


def plot_selected_country_composition(
    data: pd.DataFrame,
    year: int,
) -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    x_positions = np.arange(len(data))
    bottoms = np.zeros(len(data))

    for sector in ['agriculture', 'industry', 'services']:
        values = data[sector].to_numpy()
        bars = ax.bar(
            x_positions,
            values,
            width=0.64,
            bottom=bottoms,
            color=SECTOR_COLORS[sector],
            label=SECTOR_LABELS[sector],
            edgecolor='white',
            linewidth=0.7,
        )
        for bar, value, bottom in zip(bars, values, bottoms):
            if value >= 4:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bottom + value / 2,
                    f'{value:.1f}%',
                    ha='center',
                    va='center',
                    color='white',
                    fontsize=10,
                    fontweight='bold',
                )
        bottoms += values

    ax.set_xticks(
        x_positions,
        [COUNTRY_LABELS[code] for code in data['country_code']],
    )
    for tick, code in zip(ax.get_xticklabels(), data['country_code']):
        if code == 'PRT':
            tick.set_color(COURSE_ORANGE)
            tick.set_fontweight('bold')

    ax.set_ylabel('Share of total value added (%)')
    ax.set_ylim(0, 105)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    ax.legend(
        ncol=3,
        loc='upper center',
        bbox_to_anchor=(0.5, 1.08),
        frameon=False,
    )
    fig.text(
        0.01,
        0.018,
        (
            f'Source: World Bank World Development Indicators, {year}. '
            'Shares are normalized to total sector value added; '
            'industry includes construction.'
        ),
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.15)
    save_figure(
        fig,
        FIGURE_DIR / 'production-composition-selected-countries.pdf',
    )
    plt.close(fig)


def descriptive_fit(ax, data: pd.DataFrame, y_column: str) -> None:
    x_values = data['gdp_pc'].to_numpy()
    y_values = data[y_column].to_numpy()
    coefficients = np.polyfit(np.log10(x_values), y_values, deg=2)
    grid = np.geomspace(x_values.min(), x_values.max(), 250)
    fitted = np.polyval(coefficients, np.log10(grid))
    fitted = np.clip(fitted, 0, None)
    ax.plot(
        grid,
        fitted,
        color=COURSE_BLUE,
        linewidth=2.2,
        label='Descriptive fit',
        zorder=2,
    )


def add_country_labels(ax, data: pd.DataFrame, y_column: str) -> None:
    for country in PANEL_LABEL_COUNTRIES[y_column]:
        row = data.loc[data['country_name'].eq(country)]
        if row.empty:
            continue
        x_value = row.iloc[0]['gdp_pc']
        y_value = row.iloc[0][y_column]
        is_portugal = country == 'Portugal'
        offset, alignment = LABEL_POSITIONS.get(
            (y_column, country),
            ((7, 6), 'left'),
        )
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
            xytext=offset,
            textcoords='offset points',
            ha=alignment,
            fontsize=8.2,
            color=COURSE_ORANGE if is_portugal else COURSE_BLUE,
            fontweight='bold' if is_portugal else 'normal',
            zorder=5,
        )


def plot_relationship_panel(
    ax,
    data: pd.DataFrame,
    y_column: str,
    panel_title: str,
    y_label: str,
    y_limits: tuple[float, float],
    *,
    show_ylabel: bool,
    show_legend: bool,
) -> None:
    clean = data.replace([np.inf, -np.inf], np.nan).dropna(
        subset=['gdp_pc', y_column]
    )
    clean = clean.loc[(clean['gdp_pc'] > 0) & (clean[y_column] >= 0)].copy()
    ax.scatter(
        clean['gdp_pc'],
        clean[y_column],
        s=25,
        color=POINT_GREY,
        alpha=0.72,
        edgecolor='none',
        zorder=1,
    )
    descriptive_fit(ax, clean, y_column)
    add_country_labels(ax, clean, y_column)
    ax.set_title(panel_title, color=COURSE_BLUE, fontweight='bold', pad=10)
    ax.set_xscale('log')
    ax.set_xlim(800, 140_000)
    ax.set_ylim(*y_limits)
    ax.set_xticks([1_000, 5_000, 20_000, 100_000])
    ax.xaxis.set_major_formatter(FuncFormatter(money_tick))
    ax.set_xlabel('GDP per capita at PPP')
    if show_ylabel:
        ax.set_ylabel(y_label)
    ax.grid(axis='both', which='major')
    if show_legend:
        ax.legend(loc='upper right', frameon=False, fontsize=8.5)


def year_range(data: pd.DataFrame) -> str:
    first = int(data['year'].min())
    last = int(data['year'].max())
    return str(first) if first == last else f'{first}--{last}'


def plot_production_structure(
    agriculture: pd.DataFrame,
    manufacturing: pd.DataFrame,
    services: pd.DataFrame,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 5.6))
    plot_relationship_panel(
        axes[0],
        agriculture,
        'agriculture',
        'Agriculture',
        'Share of GDP (%)',
        (0, 65),
        show_ylabel=True,
        show_legend=True,
    )
    plot_relationship_panel(
        axes[1],
        manufacturing,
        'manufacturing',
        'Manufacturing',
        'Share of GDP (%)',
        (0, 45),
        show_ylabel=False,
        show_legend=False,
    )
    plot_relationship_panel(
        axes[2],
        services,
        'services',
        'Services',
        'Share of GDP (%)',
        (20, 90),
        show_ylabel=False,
        show_legend=False,
    )
    fig.text(
        0.01,
        0.018,
        (
            'Source: World Bank World Development Indicators. '
            f'Latest observations: agriculture {year_range(agriculture)} '
            f'(N={len(agriculture)}); manufacturing '
            f'{year_range(manufacturing)} (N={len(manufacturing)}); '
            f'services {year_range(services)} (N={len(services)}).'
        ),
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(
        left=0.08,
        right=0.985,
        top=0.90,
        bottom=0.19,
        wspace=0.24,
    )
    save_figure(fig, FIGURE_DIR / 'production-structure-and-income.pdf')
    plt.close(fig)


def main() -> None:
    apply_course_style()
    gdp = indicator(
        INDICATORS['gdp_pc'],
        'gdp_pc',
        CACHE_DIR,
        YEARS,
    )
    agriculture = indicator(
        INDICATORS['agriculture'],
        'agriculture',
        CACHE_DIR,
        YEARS,
    )
    industry = indicator(
        INDICATORS['industry'],
        'industry',
        CACHE_DIR,
        YEARS,
    )
    manufacturing = indicator(
        INDICATORS['manufacturing'],
        'manufacturing',
        CACHE_DIR,
        YEARS,
    )
    services = indicator(
        INDICATORS['services'],
        'services',
        CACHE_DIR,
        YEARS,
    )

    composition, composition_year = selected_country_composition(
        agriculture,
        industry,
        services,
    )
    agriculture_relationship = latest_relationship(gdp, agriculture)
    manufacturing_relationship = latest_relationship(gdp, manufacturing)
    services_relationship = latest_relationship(gdp, services)

    plot_selected_country_composition(composition, composition_year)
    plot_production_structure(
        agriculture_relationship,
        manufacturing_relationship,
        services_relationship,
    )

    print(
        FIGURE_DIR / 'production-composition-selected-countries.pdf'
    )
    print(FIGURE_DIR / 'production-structure-and-income.pdf')


if __name__ == '__main__':
    main()
