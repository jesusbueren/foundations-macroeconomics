'''Create the U.S. nominal and real GDP figure.'''

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
    POINT_GREY,
    TEXT_GREY,
    apply_course_style,
    save_figure,
)
from common.python.fred import series as fred_series  # noqa: E402


SERIES = {
    'nominal_gdp': 'GDP',
    'real_gdp': 'GDPC1',
    'recession': 'USRECQ',
}
START_DATE = '1950-01-01'


def load_data() -> pd.DataFrame:
    frames = [
        fred_series(series_id, value_name, CACHE_DIR)
        for value_name, series_id in SERIES.items()
    ]
    data = frames[0]
    for frame in frames[1:]:
        data = data.merge(frame, on='date', how='inner')
    return data.loc[data['date'].ge(START_DATE)].reset_index(drop=True)


def trillions_tick(value, _position) -> str:
    return f'${value:,.0f}'


def plot_figure(data: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    nominal = data['nominal_gdp'] / 1_000
    real = data['real_gdp'] / 1_000

    ax.fill_between(
        data['date'],
        0,
        1,
        where=data['recession'].gt(0),
        transform=ax.get_xaxis_transform(),
        color=POINT_GREY,
        alpha=0.22,
        linewidth=0,
        zorder=0,
    )
    ax.plot(
        data['date'],
        nominal,
        color=COURSE_ORANGE,
        linewidth=2.5,
        zorder=3,
    )
    ax.plot(
        data['date'],
        real,
        color=COURSE_BLUE,
        linewidth=2.5,
        zorder=3,
    )

    reference_date = pd.Timestamp('2017-01-01')
    ax.axvline(
        reference_date,
        color=TEXT_GREY,
        linewidth=1.0,
        linestyle=(0, (3, 3)),
        alpha=0.75,
        zorder=2,
    )
    ax.text(
        reference_date,
        0.97,
        '2017 reference year',
        transform=ax.get_xaxis_transform(),
        ha='right',
        va='top',
        fontsize=9,
        color=TEXT_GREY,
    )

    last_date = data['date'].iloc[-1]
    label_date = last_date + pd.DateOffset(months=10)
    ax.text(
        label_date,
        nominal.iloc[-1],
        'Nominal GDP',
        color=COURSE_ORANGE,
        fontsize=10.5,
        fontweight='bold',
        va='center',
    )
    ax.text(
        label_date,
        real.iloc[-1],
        'Real GDP',
        color=COURSE_BLUE,
        fontsize=10.5,
        fontweight='bold',
        va='center',
    )

    ax.set_xlim(data['date'].min(), last_date + pd.DateOffset(years=7))
    ax.set_ylim(0, max(nominal.max(), real.max()) * 1.10)
    ax.set_ylabel('Trillions of dollars')
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_formatter(FuncFormatter(trillions_tick))
    ax.xaxis.set_major_locator(mdates.YearLocator(10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(axis='y')
    ax.set_axisbelow(True)

    latest_period = last_date.to_period('Q')
    fig.text(
        0.01,
        0.018,
        (
            'Source: BEA via FRED. '
            f'Quarterly SAAR through {latest_period}. Real GDP: chained 2017 '
            'dollars. Shading: NBER recessions.'
        ),
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(left=0.09, right=0.86, top=0.95, bottom=0.16)
    save_figure(fig, FIGURE_DIR / 'US_GDP_nominal_vs_real.pdf')
    plt.close(fig)


def main() -> None:
    apply_course_style()
    data = load_data()
    plot_figure(data)
    latest_period = data['date'].iloc[-1].to_period('Q')
    print(f'Latest observation: {latest_period}')
    print(FIGURE_DIR / 'US_GDP_nominal_vs_real.pdf')


if __name__ == '__main__':
    main()
