'''Create the expenditure-approach GDP composition figure.'''

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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
    TEXT_GREY,
    apply_course_style,
    save_figure,
)
from common.python.world_bank import indicator  # noqa: E402


YEARS = '2018:2025'
INDICATORS = {
    'household_consumption': 'NE.CON.PRVT.ZS',
    'government_consumption': 'NE.CON.GOVT.ZS',
    'investment': 'NE.GDI.TOTL.ZS',
    'net_exports': 'NE.RSB.GNFS.ZS',
}
COUNTRY_ORDER = ['PRT', 'USA', 'DEU', 'FRA']
COUNTRY_LABELS = {
    'PRT': 'Portugal',
    'USA': 'United States',
    'DEU': 'Germany',
    'FRA': 'France',
}
COMPONENTS = [
    'household_consumption',
    'government_consumption',
    'investment',
    'net_exports',
]
COMPONENT_LABELS = {
    'household_consumption': 'Households',
    'government_consumption': 'Government',
    'investment': 'Investment',
    'net_exports': 'Net exports',
}
COMPONENT_COLORS = {
    'household_consumption': COURSE_BLUE,
    'government_consumption': PEER_BLUE,
    'investment': COURSE_ORANGE,
    'net_exports': POINT_GREY,
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
    frames: list[pd.DataFrame],
) -> tuple[pd.DataFrame, int]:
    data = merge_same_year(frames)
    data = data.loc[data['country_code'].isin(COUNTRY_ORDER)].copy()
    coverage = data.groupby('year')['country_code'].nunique()
    valid_years = coverage.loc[coverage.eq(len(COUNTRY_ORDER))].index
    if valid_years.empty:
        raise RuntimeError('No common year is available for the selected countries.')
    year = int(valid_years.max())
    data = data.loc[data['year'].eq(year)].set_index('country_code')
    data = data.loc[COUNTRY_ORDER].reset_index()
    return data, year


def add_value_labels(ax, bars, values: np.ndarray) -> None:
    for bar, value in zip(bars, values):
        if value >= 0:
            label_y = value + 1.0
            vertical_alignment = 'bottom'
        else:
            label_y = value - 1.0
            vertical_alignment = 'top'
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            label_y,
            f'{value:.1f}',
            ha='center',
            va=vertical_alignment,
            fontsize=9,
            color=TEXT_GREY,
            fontweight='bold',
        )


def plot_expenditure_composition(data: pd.DataFrame, year: int) -> None:
    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    x_positions = np.arange(len(data))
    width = 0.19
    offsets = (np.arange(len(COMPONENTS)) - 1.5) * width

    for component, offset in zip(COMPONENTS, offsets):
        values = data[component].to_numpy()
        bars = ax.bar(
            x_positions + offset,
            values,
            width=width,
            color=COMPONENT_COLORS[component],
            label=COMPONENT_LABELS[component],
            edgecolor='white',
            linewidth=0.5,
        )
        add_value_labels(ax, bars, values)

    ax.axhline(0, color='#6B7280', linewidth=0.9)
    ax.set_xticks(
        x_positions,
        [COUNTRY_LABELS[code] for code in data['country_code']],
    )
    for tick, code in zip(ax.get_xticklabels(), data['country_code']):
        if code == 'PRT':
            tick.set_color(COURSE_ORANGE)
            tick.set_fontweight('bold')

    values = data[COMPONENTS].to_numpy()
    lower_limit = min(-10, np.floor(values.min() / 5) * 5 - 5)
    upper_limit = max(75, np.ceil(values.max() / 5) * 5 + 8)
    ax.set_ylim(lower_limit, upper_limit)
    ax.set_ylabel('Share of GDP (%)')
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    ax.legend(
        ncol=4,
        loc='upper center',
        bbox_to_anchor=(0.5, 1.08),
        frameon=False,
    )
    fig.text(
        0.01,
        0.018,
        (
            f'Source: World Bank World Development Indicators, {year}. '
            'Net exports equal exports minus imports; components may not sum '
            'exactly to 100 because of statistical discrepancies.'
        ),
        ha='left',
        va='bottom',
        fontsize=8,
        color='#6B7280',
    )
    fig.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.16)
    save_figure(
        fig,
        FIGURE_DIR / 'expenditure-composition-selected-countries.pdf',
    )
    plt.close(fig)


def main() -> None:
    apply_course_style()
    frames = [
        indicator(code, component, CACHE_DIR, YEARS)
        for component, code in INDICATORS.items()
    ]
    composition, year = selected_country_composition(frames)
    plot_expenditure_composition(composition, year)

    print(f'Common year: {year}')
    print(composition[['country_code', *COMPONENTS]].to_string(index=False))
    print(FIGURE_DIR / 'expenditure-composition-selected-countries.pdf')


if __name__ == '__main__':
    main()
