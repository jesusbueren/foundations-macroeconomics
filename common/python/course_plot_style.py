'''Shared visual style for Foundations of Macroeconomics figures.'''

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl


COURSE_BLUE = '#14346E'
COURSE_ORANGE = '#D95F02'
PEER_BLUE = '#5578A9'
POINT_GREY = '#B8C0CC'
GRID_GREY = '#D9DEE7'
TEXT_GREY = '#4B5563'


def apply_course_style() -> None:
    '''Apply the common typography, colors, and axes style.'''
    mpl.rcParams.update(
        {
            'font.family': 'DejaVu Sans',
            'font.size': 11,
            'axes.labelsize': 12,
            'axes.labelcolor': '#111827',
            'axes.edgecolor': '#9CA3AF',
            'axes.linewidth': 0.8,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'xtick.color': TEXT_GREY,
            'ytick.color': TEXT_GREY,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'grid.color': GRID_GREY,
            'grid.linewidth': 0.7,
            'grid.alpha': 0.75,
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'savefig.facecolor': 'white',
            'pdf.fonttype': 42,
            'ps.fonttype': 42,
        }
    )


def save_figure(fig: mpl.figure.Figure, path: Path) -> None:
    '''Save a vector PDF with deterministic metadata.'''
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        path,
        metadata={
            'Creator': 'Foundations of Macroeconomics figure pipeline',
            'CreationDate': None,
            'ModDate': None,
        },
    )
