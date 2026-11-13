# Chapter 5: Consumption and Saving

Imported from `5-ConsumptionSaving` in the original course materials.

- `slides/consumption-saving.tex`: the 36-frame chapter (37 PDF pages including
  the overlay), using the shared course theme in
  `common/foundationsmacro-beamer.sty` and the same 10pt, 16:9 format as the
  preceding chapters.
- `slides/consumption-saving.pdf`: the compiled slides.
- `slides/figures/c-y.png`: the supplied consumption and income figure.

The import preserves the original slide text, equations, order, diagrams, and
figure asset while adapting the presentation style and resizing three diagrams
to fit the slide height. The original overlay and convention of displaying
leisure as `\ell` are retained. Temporary build files are excluded.

## Build the slides

From `05-consumption-saving/slides/`, run:

```powershell
latexmk -pdf consumption-saving.tex
```

The supplied figure and the diagrams embedded in the LaTeX source allow the
slides to compile without fetching data or running plotting scripts.
