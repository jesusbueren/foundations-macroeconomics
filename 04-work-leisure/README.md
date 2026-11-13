# Chapter 4: Work and Leisure

Imported from `4-WorkLeisure` in the original course materials.

- `slides/WorkLeisure.tex`: the chapter source, using the shared course theme
  in `common/foundationsmacro-beamer.sty`
  and the same 10pt, 16:9 format
  as the preceding chapters.
- `slides/WorkLeisure.pdf`: the compiled slides.
- `slides/figures/`: the two supplied empirical figures.

The initial import preserved the original slide text, equations, order, and figure
assets while adapting the presentation style and sizing the empirical figures
to fit their columns. The original convention of displaying leisure as `\ell`
is retained. Interactive HTML files
and temporary build files are excluded.

The chapter ends with six slides on higher productivity under inelastic,
upward-sloping, and downward-sloping labor supply. TikZ diagrams show the labor
demand shift, equilibrium wages, and employment. The output comparison includes
both possible outcomes when labor supply slopes downward and states the slope
condition assumed in that diagram. Capital, preferences, and nonlabor income
are held fixed throughout this comparison.

## Build the slides

From `04-work-leisure/slides/`, run:

```powershell
latexmk -pdf WorkLeisure.tex
```

The supplied figures and the diagrams embedded in the LaTeX source allow the
slides to compile without fetching data or running plotting scripts.
