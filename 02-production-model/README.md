# Chapter 2: A Model of Production

Imported from `2-ProductionModel` in the original course materials.

- `slides/Production.tex`: the original slide content, using the shared course
  theme in `common/foundationsmacro-beamer.sty` and the same 10pt, 16:9 format as
  Chapter 1.
- `slides/Production.pdf`: the compiled slides.
- `slides/figures/`: the production-model charts and the supplied figure assets.
- `code/model_vs_data.py`: generates all four production-model charts using the
  shared course plot style and the original data calculations.
- `data/pwt110.dta`: the original Penn World Table data file.

The initial import preserved the original materials. The slide source and
generated model figures include subsequent course edits. Interactive HTML
exercises are excluded.

## Build the slides

From `02-production-model/slides/`, run:

```powershell
latexmk -pdf Production.tex
```

The committed figure PDFs allow the slides to compile without running Python.

## Plotting code

From the repository root, run:

```powershell
.venv/Scripts/python.exe 02-production-model/code/model_vs_data.py
```

This regenerates the US benchmark, model-versus-data scatter, capital-output
comparison, and country-specific TFP comparison. They share fonts, dimensions,
gridlines, margins, and country colors. The three capital-output charts also
share axis limits. All countries remain in the scatterplot; labels highlight
the US, Portugal, and Spain. Other imported figures remain supplied assets.

The US-only benchmark figure is generated separately, using the shared course
plot style:

```powershell
.venv/Scripts/python.exe 02-production-model/code/make_us_benchmark_figure.py
```

It shows the theoretical relation between capital and output per person relative
to the US under equal productivity, with only the US marked at `(1, 1)`.
