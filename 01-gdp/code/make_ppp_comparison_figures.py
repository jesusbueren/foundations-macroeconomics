'''Create GDP per capita comparisons for Portugal, Angola, and the US.'''

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
    apply_course_style,
    save_figure,
)
from common.python.world_bank import indicator  # noqa: E402


YEARS = '1990:2025'
LEVEL_YEAR = 2024
COUNTRY_ORDER = ['PRT', 'AGO']
LEVEL_COUNTRY_ORDER = [*COUNTRY_ORDER, 'USA']
COUNTRY_LABELS = {
    'PRT': 'Portugal',
    'AGO': 'Angola',
    'USA': 'United States',
}
INDICATORS = {
    'real_ppp': 'NY.GDP.PCAP.PP.KD',
    'market_current': 'NY.GDP.PCAP.CD',
    'ppp_current': 'NY.GDP.PCAP.PP.CD',
}


def money_tick(value, _position) -> str:
    if value >= 1_000:
        return '$' + f'{value / 1_000:g}k'
    return '$' + f'{value:g}'


def country_data(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.loc[
        frame['country_code'].isin(COUNTRY_ORDER)
    ].copy()


def plot_real_ppp(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    colors = {
        'PRT': COURSE_BLUE,
        'AGO': COURSE_ORANGE,
    }

    for code in COUNTRY_ORDER:
        series = (
            data.loc[data['country_code'].eq(code)]
            .sort_values('year')
            .dropna(subset=['real_ppp'])
        )
        ax.plot(
            series['year'],
            series['real_ppp'],
            color=colors[code],
            linewidth=2.7,
        )
        last = series.iloc[-1]
        ax.annotate(
            COUNTRY_LABELS[code],
            (last['year'], last['real_ppp']),
            xytext=(8, 0),
            textcoords='offset points',
            ha='left',
            va='center',
            color=colors[code],
            fontsize=10.5,
            fontweight='bold',
        )

    final_year = int(data['year'].max())
    ax.set_xlim(int(data['year'].min()), final_year + 4)
    ax.set_ylabel('Constant 2021 international dollars per person')
    ax.yaxis.set_major_formatter(FuncFormatter(money_tick))
    ax.grid(axis='both')
    ax.set_axisbelow(True)
    fig.text(
        0.01,
        0.018,
        (
            'Source: World Bank World Development Indicators. '
            'GDP per capita at PPP in constant 2021 international dollars, '
            f'through {final_year}.'
        ),
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(left=0.11, right=0.88, top=0.96, bottom=0.14)
    save_figure(
        fig,
        FIGURE_DIR / 'GDP_Per_Capita_Comparison.pdf',
    )
    plt.close(fig)


def latest_common_values(
    market: pd.DataFrame,
    ppp: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    data = market.merge(
        ppp.drop(columns='country_name'),
        on=['country_code', 'year'],
        how='inner',
    )
    data = data.loc[data['country_code'].isin(LEVEL_COUNTRY_ORDER)].copy()
    coverage = data.groupby('year')['country_code'].nunique()
    years = coverage.loc[coverage.eq(len(LEVEL_COUNTRY_ORDER))].index
    if years.empty:
        raise RuntimeError(
            'No common year is available for Portugal, Angola, and the US.'
        )
    if LEVEL_YEAR not in years:
        raise RuntimeError(
            f'World Bank data are not available for {LEVEL_YEAR}.'
        )
    year = LEVEL_YEAR
    data = data.loc[data['year'].eq(year)].set_index('country_code')
    return data.loc[LEVEL_COUNTRY_ORDER].reset_index(), year


def add_bar_labels(ax, bars) -> None:
    for bar in bars:
        value = bar.get_height()
        ax.annotate(
            '$' + f'{value / 1_000:.1f}k',
            (bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 6),
            textcoords='offset points',
            va='bottom',
            ha='center',
            fontsize=10,
            color='#111827',
        )


def plot_market_vs_ppp(data: pd.DataFrame, year: int) -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    positions = np.arange(len(data))
    width = 0.32

    market_bars = ax.bar(
        positions - width / 2,
        data['market_current'],
        width=width,
        color=PEER_BLUE,
        label='Market exchange rates',
    )
    ppp_bars = ax.bar(
        positions + width / 2,
        data['ppp_current'],
        width=width,
        color=COURSE_ORANGE,
        label='Purchasing power parity',
    )
    add_bar_labels(ax, market_bars)
    add_bar_labels(ax, ppp_bars)

    ax.set_xticks(
        positions,
        [COUNTRY_LABELS[code] for code in data['country_code']],
    )
    ax.set_ylabel('GDP per capita')
    ax.yaxis.set_major_formatter(FuncFormatter(money_tick))
    ax.set_ylim(0, data[['market_current', 'ppp_current']].max().max() * 1.18)
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    ax.legend(
        ncol=2,
        loc='upper center',
        bbox_to_anchor=(0.5, 1.08),
        frameon=False,
    )
    fig.text(
        0.01,
        0.018,
        (
            f'Source: World Bank World Development Indicators, {year}. '
            'Market values are current US dollars; PPP values are current '
            'international dollars.'
        ),
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(left=0.11, right=0.97, top=0.88, bottom=0.16)
    save_figure(
        fig,
        FIGURE_DIR / 'GDP_Per_Capita_PPP_vs_Mkt.pdf',
    )
    plt.close(fig)


def main() -> None:
    apply_course_style()
    real_ppp = country_data(
        indicator(
            INDICATORS['real_ppp'],
            'real_ppp',
            CACHE_DIR,
            YEARS,
        )
    )
    market = indicator(
        INDICATORS['market_current'],
        'market_current',
        CACHE_DIR,
        YEARS,
    )
    ppp = indicator(
        INDICATORS['ppp_current'],
        'ppp_current',
        CACHE_DIR,
        YEARS,
    )

    comparison, year = latest_common_values(market, ppp)
    plot_real_ppp(real_ppp)
    plot_market_vs_ppp(comparison, year)

    print(FIGURE_DIR / 'GDP_Per_Capita_Comparison.pdf')
    print(FIGURE_DIR / 'GDP_Per_Capita_PPP_vs_Mkt.pdf')


if __name__ == '__main__':
    main()
