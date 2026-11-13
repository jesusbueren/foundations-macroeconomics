# Growth data

`mpd2023_web.xlsx` is the original Maddison Project Database 2023 workbook
supplied with the chapter. It is copied without modification.

Penn World Table 11.0 calculations use the existing, unchanged file
`../../02-production-model/data/pwt110.dta`, avoiding a duplicate dataset.

The capital-output charts use
`(rnna / rgdpna) * (pl_n / pl_gdpo in 2021)` for each country. PWT anchors the
capital and GDP volume series using separate PPP conversions in the benchmark
year. The benchmark relative-price factor puts the ratio at domestic 2021
prices. Holding that factor fixed retains the national constant-price growth
rates; this is not a ratio at current domestic prices.

The convergence script retrieves World Bank World Development Indicators
(`NY.GDP.PCAP.KD`) for 1960 and 2023. The supplied convergence figures are
preserved; no online data are refreshed as part of this import.

The investment plotting function also retrieves Afghanistan gross capital
formation (`NE.GDI.TOTL.ZS`) from the World Bank when run.

`pwt110_labor_share_flags.csv` contains the official `i_labsh2` flags for the
four countries in the labor-share figure, extracted from PWT 11.0's labor
detail file on 2026-11-12. Source:
https://dataverse.nl/api/access/datafile/554028 (dataset DOI: 10.34894/FABVLR).
PWT is attributed to Feenstra, Inklaar and Timmer (2015), under CC BY 4.0.
The labor-share values in the detail file were checked against the existing
PWT dataset and match.

The graph includes only `i_labsh2 = 1` (observed data). It excludes `0`
(assumed constant or interpolated) and `2` (extrapolated mixed-income share),
as well as missing or invalid values. Missing years remain gaps rather than
being connected by a line. Observed coverage is 1950-2023 for the US,
1991-2023 for Germany, and 1995-2023 for Portugal and Spain.
