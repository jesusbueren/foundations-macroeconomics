'''Create the production-model figures with one shared course style.'''

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
CHAPTER_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = CHAPTER_DIR / 'data' / 'pwt110.dta'
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


FIGURE_SIZE = (10.6, 5.6)
BENCHMARK_FILENAME = 'Production_Model_Scatter_Relative_US_US_Only.pdf'
COUNTRY_STYLES = {
    'USA': {'label': 'US', 'color': COURSE_ORANGE, 'marker': 'o', 'size': 100},
    'PRT': {'label': 'Portugal', 'color': COURSE_BLUE, 'marker': '*', 'size': 130},
    'ESP': {'label': 'Spain', 'color': PEER_BLUE, 'marker': 's', 'size': 65},
}
CAPITAL_OFFSETS = {'USA': (10, -23), 'PRT': (8, -18), 'ESP': (8, 16)}
SCATTER_OFFSETS = {'USA': (8, -18), 'PRT': (-8, 9), 'ESP': (8, -18)}


def load_country_data() -> tuple[pd.DataFrame, int]:
    '''Use the original sample, variables, and US normalization.'''
    frame = pd.read_stata(DATA_PATH)
    year = int(frame['year'].max())
    data = frame.loc[
        frame['year'].eq(year), ['countrycode', 'rgdpo', 'pop', 'cn']
    ].dropna().copy()
    data['y_actual'] = data['rgdpo'] / data['pop']
    data['k_per_worker'] = data['cn'] / data['pop']
    data['y_predicted'] = data['k_per_worker'] ** (1 / 3)
    us = data.loc[data['countrycode'].eq('USA')]
    if len(us) != 1:
        raise RuntimeError('Exactly one US observation is required.')
    us = us.iloc[0]
    data['y_actual_rel'] = data['y_actual'] / us['y_actual']
    data['y_predicted_rel'] = data['y_predicted'] / us['y_predicted']
    data['k_rel'] = data['k_per_worker'] / us['k_per_worker']
    return data, year


def new_figure():
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    ax.grid(axis='both')
    ax.set_axisbelow(True)
    return fig, ax


def finish_figure(fig, filename: str, note: str) -> Path:
    fig.text(
        0.01, 0.018, note, ha='left', va='bottom',
        fontsize=8, color='#6B7280',
    )
    fig.subplots_adjust(left=0.11, right=0.98, top=0.96, bottom=0.19)
    path = FIGURE_DIR / filename
    save_figure(fig, path)
    plt.close(fig)
    return path


def data_source(year: int) -> str:
    return (
        'Source: Penn World Table 11.0 (Feenstra, Inklaar, and Timmer), '
        f'{year}. Values are relative to the US.'
    )


def format_capital_output_axes(ax) -> None:
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 1.6)
    ax.set_xticks(np.arange(0, 3.01, 0.5))
    ax.set_yticks(np.arange(0, 1.51, 0.25))
    ax.set_xlabel(r'Capital per person relative to US, $k/k_{\mathrm{US}}$')
    ax.set_ylabel(r'Output per person relative to US, $y/y_{\mathrm{US}}$')


def add_model_curve(ax, label='Model: equal productivity') -> np.ndarray:
    capital = np.linspace(0, 3, 601)
    ax.plot(
        capital, np.cbrt(capital), color=COURSE_BLUE,
        linewidth=2.7, label=label, zorder=2,
    )
    return capital


def add_country_markers(ax, data, x_column, y_column, offsets) -> None:
    for code, style in COUNTRY_STYLES.items():
        row = data.loc[data['countrycode'].eq(code)]
        if row.empty:
            continue
        row = row.iloc[0]
        ax.scatter(
            [row[x_column]], [row[y_column]], s=style['size'],
            marker=style['marker'], color=style['color'],
            edgecolor='white', linewidth=0.8, zorder=4,
        )
        offset = offsets[code]
        ax.annotate(
            style['label'], (row[x_column], row[y_column]),
            xytext=offset, textcoords='offset points',
            ha='left' if offset[0] > 0 else 'right', va='center',
            fontsize=9.5, color=style['color'], fontweight='bold', zorder=5,
        )


def plot_us_benchmark() -> Path:
    fig, ax = new_figure()
    add_model_curve(ax)
    ax.vlines(1, 0, 1, color=TEXT_GREY, linewidth=1, linestyles='--', zorder=1)
    ax.hlines(1, 0, 1, color=TEXT_GREY, linewidth=1, linestyles='--', zorder=1)
    ax.scatter(
        [1], [1], s=COUNTRY_STYLES['USA']['size'], color=COURSE_ORANGE,
        edgecolor='white', linewidth=0.8, zorder=4,
    )
    ax.annotate(
        'US (1, 1)', (1, 1), xytext=CAPITAL_OFFSETS['USA'],
        textcoords='offset points', ha='left', va='center',
        color=COURSE_ORANGE, fontsize=9.5, fontweight='bold', zorder=5,
    )
    format_capital_output_axes(ax)
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    return finish_figure(
        fig, BENCHMARK_FILENAME,
        'Model: common productivity across countries. '
        'Capital and output per person are normalized relative to the US.',
    )


def plot_model_scatter(data: pd.DataFrame, year: int) -> Path:
    fig, ax = new_figure()
    others = data.loc[~data['countrycode'].isin(COUNTRY_STYLES)]
    ax.scatter(
        others['y_actual_rel'], others['y_predicted_rel'],
        s=27, color=POINT_GREY, alpha=0.72, edgecolor='none',
        label='Other countries', zorder=1,
    )
    maximum = data[['y_actual_rel', 'y_predicted_rel']].max().max()
    limit = np.ceil(maximum * 1.05 * 2) / 2
    ax.plot(
        [0, limit], [0, limit], color=TEXT_GREY,
        linewidth=1.4, linestyle='--', label='Perfect prediction', zorder=2,
    )
    add_country_markers(
        ax, data, 'y_actual_rel', 'y_predicted_rel', SCATTER_OFFSETS,
    )
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_xticks(np.arange(0, limit + 0.01, 0.5))
    ax.set_yticks(np.arange(0, limit + 0.01, 0.5))
    ax.set_xlabel(r'Actual output per person relative to US, $y/y_{\mathrm{US}}$')
    ax.set_ylabel(
        'Model-predicted output per person\n'
        r'relative to US, $(k/k_{\mathrm{US}})^{1/3}$'
    )
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    return finish_figure(fig, 'Production_Model_Scatter_Relative_US.pdf', data_source(year))


def plot_capital_output(data: pd.DataFrame, year: int) -> Path:
    fig, ax = new_figure()
    add_model_curve(ax)
    add_country_markers(ax, data, 'k_rel', 'y_actual_rel', CAPITAL_OFFSETS)
    format_capital_output_axes(ax)
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    return finish_figure(fig, 'Solow_K_Y_Curve_Relative_US.pdf', data_source(year))


def plot_country_tfp(data: pd.DataFrame, year: int) -> Path:
    fig, ax = new_figure()
    capital = add_model_curve(ax, 'US productivity (A = 1)')
    for code, line_style in [('PRT', '--'), ('ESP', '-.')]:
        row = data.loc[data['countrycode'].eq(code)]
        if row.empty:
            continue
        row = row.iloc[0]
        productivity = row['y_actual_rel'] / row['k_rel'] ** (1 / 3)
        style = COUNTRY_STYLES[code]
        ax.plot(
            capital, productivity * np.cbrt(capital),
            color=style['color'], linewidth=2.2, linestyle=line_style,
            label=f"{style['label']} (A = {productivity:.2f})", zorder=2,
        )
    add_country_markers(ax, data, 'k_rel', 'y_actual_rel', CAPITAL_OFFSETS)
    format_capital_output_axes(ax)
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    return finish_figure(fig, 'Solow_K_Y_Curve_Country_TFP.pdf', data_source(year))


def main() -> None:
    apply_course_style()
    data, year = load_country_data()
    paths = [
        plot_us_benchmark(),
        plot_model_scatter(data, year),
        plot_capital_output(data, year),
        plot_country_tfp(data, year),
    ]
    print(f'Data year: {year}; countries: {len(data)}')
    for path in paths:
        print(path)


if __name__ == '__main__':
    main()
