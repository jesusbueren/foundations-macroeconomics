# Production model data

`pwt110.dta` is the original Penn World Table 11.0 file supplied with the course
materials. It is copied unchanged.

The plotting script selects the latest year in this file and uses `countrycode`,
`rgdpo`, `pop`, and `cn` to construct output and capital per person, normalized
relative to the United States. The import does not update the data or regenerate
the existing figures.
