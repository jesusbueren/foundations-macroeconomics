# Chapter 3: Economic Growth

Imported from `3-Growth` in the original course materials.

- `slides/Growth.tex`: the original 53-slide chapter, using the shared course
  theme in `common/foundationsmacro-beamer.sty` and the same 10pt, 16:9 format
  as the preceding chapters.
- `slides/Growth.pdf`: the compiled slides.
- `slides/figures/`: the supplied figures, including alternative versions.
- `code/`: the supplied Python plotting scripts, with repository-relative paths.
- `data/mpd2023_web.xlsx`: the supplied Maddison Project Database workbook.
- `references/`: the supplied innovation lecture in PDF and PowerPoint formats.

The initial import preserved the original slide text, equations, order, and
figure assets while adapting the presentation style and file paths. Subsequent
course edits correct the capital-output charts to domestic 2021 prices, as
described below, and restrict the labor-share chart to observed data.
Interactive HTML files and temporary build files are excluded.

## Build the slides

From `03-growth/slides/`, run:

```powershell
latexmk -pdf Growth.tex
```

The supplied figures allow the slides to compile without running Python or
fetching data.

## Plotting code

The supplied plot designs are retained. The capital-output calculation includes
the domestic-price adjustment described below. To regenerate the Maddison and
Penn World Table figures, run from the repository root:

```powershell
.venv/Scripts/python.exe 03-growth/code/portugal_growth_plot.py --no-show
```

The script uses the local Maddison workbook and the existing PWT 11.0 file at
`02-production-model/data/pwt110.dta`. It also retrieves Afghanistan investment
data from the World Bank when regenerating the investment chart.

Both capital-output charts use `rnna / rgdpna` multiplied by each country's
`pl_n / pl_gdpo` in the benchmark year 2021. The fixed benchmark factor expresses
the ratio at domestic 2021 prices while preserving its growth over time. The
chart labels and source notes identify this valuation.

The labor-share chart uses the official observation flags in
`data/pwt110_labor_share_flags.csv`. Only observations classified by PWT as
observed are plotted; assumed-constant, interpolated, extrapolated, and missing
values are left blank.

The GDP-per-capita figure since 1865 compares Portugal with the US, Poland,
Germany, Korea, and Afghanistan. Poland replaces Spain using the same supplied
Maddison data and line formatting. Lines break across missing annual values,
and isolated available years are shown as points. Series are not extended
beyond their available years. Other supplied charts are unchanged.

`code/convergence.py` retrieves World Bank WDI data online and requires the
additional packages `wbgapi` and `seaborn`. Running it regenerates the OECD and
world convergence charts and may reflect revisions to the online data. It is
not run during the import.
