'''Create the Portugal nominal GDP, real GDP, and oil-price figure.'''

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator


REPO_ROOT = Path(__file__).resolve().parents[2]
CHAPTER_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = CHAPTER_DIR / 'data' / 'cache'
FIGURE_DIR = CHAPTER_DIR / 'slides' / 'figures'
sys.path.insert(0, str(REPO_ROOT))

from common.python.course_plot_style import (  # noqa: E402
    COURSE_BLUE,
    COURSE_ORANGE,
    TEXT_GREY,
    apply_course_style,
    save_figure,
)
from common.python.fred import series as fred_series  # noqa: E402


SERIES = {
    'nominal_gdp': 'CPMNACSCAB1GQPT',
    'real_gdp': 'CLVMNACSCAB1GQPT',
    'oil_price': 'DCOILBRENTEU',
}
START_DATE = pd.Timestamp('2025-01-01')
BASE_DATE = pd.Timestamp('2025-01-01')


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    nominal = fred_series(SERIES['nominal_gdp'], 'nominal_gdp', CACHE_DIR)
    real = fred_series(SERIES['real_gdp'], 'real_gdp', CACHE_DIR)
    oil = fred_series(SERIES['oil_price'], 'oil_price', CACHE_DIR)

    gdp = nominal.merge(real, on='date', how='inner')
    gdp = gdp.loc[gdp['date'].ge(START_DATE)].copy()
    base = gdp.loc[gdp['date'].eq(BASE_DATE)]
    if base.empty:
        raise RuntimeError('The 2025 Q1 GDP reference observation is missing.')
    for column in ['nominal_gdp', 'real_gdp']:
        gdp[f'{column}_index'] = gdp[column] / base.iloc[0][column] * 100

    oil = oil.loc[oil['date'].ge(START_DATE)].copy()
    oil = (
        oil.set_index('date')['oil_price']
        .resample('MS')
        .mean()
        .dropna()
        .rename('oil_price')
        .reset_index()
    )
    return gdp, oil


def oil_tick(value, _position) -> str:
    return f'${value:,.0f}'


def annotate_peak(ax, oil: pd.DataFrame, year: int, label: str) -> None:
    observations = oil.loc[oil['date'].dt.year.eq(year)]
    if observations.empty:
        return
    peak = observations.loc[observations['oil_price'].idxmax()]
    peak_date = peak['date']
    peak_value = peak['oil_price']
    ax.scatter(
        [peak_date],
        [peak_value],
        color=COURSE_ORANGE,
        edgecolor='white',
        linewidth=0.8,
        s=45,
        zorder=4,
    )
    ax.annotate(
        f'{label}: ${peak_value:.0f}',
        (peak_date, peak_value),
        xytext=(0, 9),
        textcoords='offset points',
        ha='center',
        va='bottom',
        fontsize=9,
        color=TEXT_GREY,
    )


def plot_figure(gdp: pd.DataFrame, oil: pd.DataFrame) -> None:
    fig, (gdp_ax, oil_ax) = plt.subplots(
        2,
        1,
        figsize=(10.6, 5.6),
        sharex=True,
        gridspec_kw={'height_ratios': [2.0, 1.0], 'hspace': 0.16},
    )

    gdp_ax.plot(
        gdp['date'],
        gdp['nominal_gdp_index'],
        color=COURSE_ORANGE,
        linewidth=2.7,
    )
    gdp_ax.plot(
        gdp['date'],
        gdp['real_gdp_index'],
        color=COURSE_BLUE,
        linewidth=2.7,
    )
    gdp_ax.axhline(100, color='#9CA3AF', linewidth=0.8, linestyle=(0, (3, 3)))
    gdp_ax.text(
        gdp['date'].iloc[-1] + pd.DateOffset(days=35),
        gdp['nominal_gdp_index'].iloc[-1],
        'Nominal GDP',
        color=COURSE_ORANGE,
        fontsize=10.5,
        fontweight='bold',
        va='center',
    )
    gdp_ax.text(
        gdp['date'].iloc[-1] + pd.DateOffset(days=35),
        gdp['real_gdp_index'].iloc[-1],
        'Real GDP',
        color=COURSE_BLUE,
        fontsize=10.5,
        fontweight='bold',
        va='center',
    )
    gdp_ax.set_ylabel('GDP index\n(2025 Q1 = 100)')
    gdp_ax.set_title(
        'Nominal and real GDP',
        loc='left',
        color=COURSE_BLUE,
        fontsize=11,
        fontweight='bold',
    )
    gdp_ax.grid(axis='y')
    gdp_ax.set_axisbelow(True)

    oil_ax.fill_between(
        oil['date'],
        oil['oil_price'],
        0,
        color=COURSE_ORANGE,
        alpha=0.12,
        linewidth=0,
    )
    oil_ax.plot(
        oil['date'],
        oil['oil_price'],
        color=COURSE_ORANGE,
        linewidth=2.2,
    )
    annotate_peak(oil_ax, oil, 2026, '2026 peak')
    oil_ax.set_ylabel('Dollars\nper barrel')
    oil_ax.set_title(
        'Brent oil price',
        loc='left',
        color=COURSE_BLUE,
        fontsize=11,
        fontweight='bold',
    )
    oil_ax.yaxis.set_major_locator(MultipleLocator(40))
    oil_ax.yaxis.set_major_formatter(FuncFormatter(oil_tick))
    oil_ax.set_ylim(0, max(140, oil['oil_price'].max() * 1.18))
    oil_ax.grid(axis='y')
    oil_ax.set_axisbelow(True)

    final_date = max(gdp['date'].iloc[-1], oil['date'].iloc[-1])
    oil_ax.set_xlim(START_DATE, final_date + pd.DateOffset(months=7))
    oil_ax.xaxis.set_major_locator(mdates.YearLocator())
    oil_ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    gdp_period = gdp['date'].iloc[-1].to_period('Q')
    oil_period = oil['date'].iloc[-1].strftime('%b. %Y')
    fig.text(
        0.01,
        0.018,
        (
            'Sources: Eurostat GDP and U.S. EIA Brent oil prices via FRED. '
            f'GDP through {gdp_period}; oil through {oil_period} (partial month). '
            'GDP is seasonally adjusted; oil is a monthly average.'
        ),
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(left=0.10, right=0.84, top=0.95, bottom=0.17)
    save_figure(fig, FIGURE_DIR / 'portugal-nominal-real-gdp-oil.pdf')
    plt.close(fig)


def main() -> None:
    apply_course_style()
    gdp, oil = load_data()
    plot_figure(gdp, oil)
    gdp_latest = gdp['date'].iloc[-1].to_period('Q')
    oil_latest = oil['date'].iloc[-1]
    print(f'GDP latest: {gdp_latest}')
    print(f'Oil latest: {oil_latest:%Y-%m}')
    print(FIGURE_DIR / 'portugal-nominal-real-gdp-oil.pdf')


if __name__ == '__main__':
    main()
