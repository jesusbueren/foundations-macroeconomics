# Data for the welfare motivation

The plotting script downloads the source data when it runs. Downloaded files are
stored in `data/cache/`, which Git ignores. The generated PDF figures are
committed so that the slides compile without rerunning Python.

## World Bank indicators

- GDP per capita, PPP (constant 2021 international dollars): `NY.GDP.PCAP.PP.KD`
- Life expectancy at birth (years): `SP.DYN.LE00.IN`
- Under-five mortality (per 1,000 live births): `SH.DYN.MORT`
- Household final consumption, PPP (constant 2021 international dollars):
  `NE.CON.PRVT.PP.KD`
- Population: `SP.POP.TOTL`

The script uses the latest common observation from 2022--2025 for each country.
Data come from the [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)
and are licensed under [CC BY 4.0](https://datacatalog.worldbank.org/public-licenses).

## Life evaluation

Life evaluation is from the
[World Happiness Report 2026 data](https://www.worldhappiness.report/data-sharing/),
Figure 2.1. The 2025 observation is the average life evaluation over 2023--2025
on a 0--10 scale. The script joins it to recent World Bank GDP per capita.

## Production composition

The production-approach figures use these World Bank indicators:

- Agriculture, forestry, and fishing, value added (% of GDP):
  `NV.AGR.TOTL.ZS`
- Industry, including construction, value added (% of GDP):
  `NV.IND.TOTL.ZS`
- Manufacturing, value added (% of GDP): `NV.IND.MANF.ZS`
- Services, value added (% of GDP): `NV.SRV.TOTL.ZS`
- GDP per capita, PPP (constant 2021 international dollars):
  `NY.GDP.PCAP.PP.KD`

For the four-country comparison, the script selects the latest year shared by
Portugal, the United States, Germany, and France. For the global relationships,
it selects each country's latest year in which GDP per capita and the relevant
sector share are both available. Industry includes construction. Net taxes on
products are not shown: agriculture, industry, and services are normalized to
100% of total sector value added.

## Income composition

The income-approach figures use the European Commission's
[AMECO database](https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database/download-annual-data-set-macro-economic-database-ameco_en),
Spring 2026 release. The cross-country composition figure uses 2024 data and
divides market-price GDP into adjusted labor income, capital income, and net
production taxes. Capital income is calculated as the residual after labor
income and net production taxes.

The trend figure plots the adjusted wage share for the
total economy as a percentage of GDP at factor cost (`ALCD2`). Factor cost
excludes net taxes on production, making the series comparable to the familiar
two-thirds labor-share benchmark. The adjustment imputes labor income to
self-employed workers. The figure uses annual data through 2024 and displays a
three-year moving average; forecast observations are excluded.

## Expenditure composition

The expenditure-approach figure uses these World Bank indicators:

- Household final consumption expenditure (% of GDP): `NE.CON.PRVT.ZS`
- General government final consumption expenditure (% of GDP):
  `NE.CON.GOVT.ZS`
- Gross capital formation (% of GDP): `NE.GDI.TOTL.ZS`
- External balance on goods and services (% of GDP): `NE.RSB.GNFS.ZS`

The figure compares Portugal, the United States, Germany, and France in the
latest year shared by all four countries and indicators. Net exports are the
external balance: exports minus imports. The source data may include small
statistical discrepancies, so the four components need not sum exactly to
100%.

## U.S. nominal and real GDP

The U.S. GDP figure uses quarterly FRED series published by the U.S. Bureau of
Economic Analysis:

- Current-dollar GDP: `GDP`
- Real GDP in chained 2017 dollars: `GDPC1`
- NBER recession indicator: `USRECQ`

The plotted values are seasonally adjusted annual rates. The chart begins in
1950 and updates to the latest quarter shared by all three series.

## Portugal nominal GDP, real GDP, and oil prices

The Portugal figure uses these FRED series:

- Eurostat current-price GDP for Portugal, seasonally adjusted:
  `CPMNACSCAB1GQPT`
- Eurostat real GDP for Portugal in chained 2010 euros, seasonally adjusted:
  `CLVMNACSCAB1GQPT`
- U.S. Energy Information Administration Brent crude oil price:
  `DCOILBRENTEU`

Nominal and real GDP are indexed to 2025 Q1 = 100, which makes their growth
rates comparable despite their different original units. Daily oil prices are
converted to monthly averages; the latest month may be incomplete. The
separate panels align the timing of the series without treating the
relationship as a causal estimate.

## Portugal, Angola, and the US: market exchange rates and PPP

The cross-country comparison uses these World Bank indicators:

- GDP per capita in current US dollars: NY.GDP.PCAP.CD
- GDP per capita at PPP in current international dollars: NY.GDP.PCAP.PP.CD
- GDP per capita at PPP in constant 2021 international dollars:
  NY.GDP.PCAP.PP.KD

The level comparison uses 2024 data for Portugal, Angola, and the United States.
The US has the same value at market exchange rates and at PPP. The time-series
figure compares Portugal and Angola beginning in 1990. Market-rate and PPP
values use different units, so the chart labels them separately.
