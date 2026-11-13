from pathlib import Path
import argparse
import json
from urllib.parse import urlencode
from urllib.request import urlopen

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd

START_YEAR = 1865
PWT_PRICE_YEAR = 2021
WB_INVESTMENT_INDICATOR = "NE.GDI.TOTL.ZS"


def load_country_gdppc(
    excel_path: Path, country_name: str, sheet_name: str = "GDPpc"
) -> pd.DataFrame:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    year_col = df.columns[0]
    country_col = country_name

    if country_col not in df.columns:
        raise ValueError(
            f"Column '{country_col}' not found in sheet '{sheet_name}'. "
            f"Available columns include: {list(df.columns)[:10]} ..."
        )

    country_data = df[[year_col, country_col]].copy()
    country_data.columns = ["Year", "GDPpc"]

    country_data["Year"] = pd.to_numeric(country_data["Year"], errors="coerce")
    country_data["GDPpc"] = pd.to_numeric(country_data["GDPpc"], errors="coerce")

    country_data = country_data.dropna().sort_values("Year")

    return country_data


def save_log_gdppc_fit_plot(
    portugal_gdppc: pd.DataFrame,
    us_gdppc: pd.DataFrame,
    output_path: Path,
    show_plot: bool = False,
) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12.8, 7.2))

    pt = portugal_gdppc[(portugal_gdppc["Year"] >= START_YEAR) & (portugal_gdppc["GDPpc"] > 0)].copy()
    us = us_gdppc[(us_gdppc["Year"] >= START_YEAR) & (us_gdppc["GDPpc"] > 0)].copy()

    pt["LogGDPpc"] = np.log(pt["GDPpc"])
    us["LogGDPpc"] = np.log(us["GDPpc"])

    pt_slope, pt_intercept = np.polyfit(pt["Year"], pt["LogGDPpc"], 1)
    us_slope, us_intercept = np.polyfit(us["Year"], us["LogGDPpc"], 1)

    pt_fit = pt_intercept + pt_slope * pt["Year"]
    us_fit = us_intercept + us_slope * us["Year"]

    ax.plot(
        pt["Year"],
        pt["LogGDPpc"],
        color="#0B3C6D",
        linewidth=3.0,
        label="Portugal (log GDP per capita)",
    )
    ax.plot(
        pt["Year"],
        pt_fit,
        color="#0B3C6D",
        linewidth=2.2,
        linestyle="--",
        alpha=0.9,
        label=f"Portugal linear fit (slope={pt_slope:.4f})",
    )

    ax.plot(
        us["Year"],
        us["LogGDPpc"],
        color="#A93226",
        linewidth=3.0,
        label="United States (log GDP per capita)",
    )
    ax.plot(
        us["Year"],
        us_fit,
        color="#A93226",
        linewidth=2.2,
        linestyle="--",
        alpha=0.9,
        label=f"United States linear fit (slope={us_slope:.4f})",
    )

    ax.set_xlabel("Year", fontsize=17)
    ax.set_ylabel("log(GDP per capita)", fontsize=17)

    ax.legend(frameon=False, fontsize=13, loc="upper left")
    ax.grid(alpha=0.28, linestyle="--", linewidth=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")
    ax.tick_params(colors="#333333", labelsize=14)
    ax.margins(x=0.01)

    fig.text(
        0.01,
        0.01,
        "Source: Maddison Project Database 2023 (Bolt and van Zanden et al.), GDPpc sheet.",
        ha="left",
        fontsize=12,
        color="#333333",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(output_path, dpi=220)
    if show_plot:
        plt.show()
    plt.close(fig)


def annual_gdppc_with_gaps(data: pd.DataFrame) -> pd.DataFrame:
    """Keep missing annual observations as NaN, without filling either endpoint."""
    series = data[["Year", "GDPpc"]].dropna(subset=["Year"]).copy()
    if series.empty:
        return series
    series["Year"] = series["Year"].astype(int)
    series.loc[~series["GDPpc"].gt(0), "GDPpc"] = np.nan
    series = series.set_index("Year", verify_integrity=True).sort_index()
    years = pd.Index(range(series.index.min(), series.index.max() + 1), name="Year")
    return series.reindex(years).reset_index()


def save_gdppc_plot(
    portugal_data: pd.DataFrame,
    us_data: pd.DataFrame,
    poland_data: pd.DataFrame,
    germany_data: pd.DataFrame,
    korea_data: pd.DataFrame,
    afghanistan_data: pd.DataFrame,
    output_path: Path,
    title: str,
    show_plot: bool = False,
) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12.8, 7.2))

    portugal_data, us_data, poland_data, germany_data, korea_data, afghanistan_data = (
        annual_gdppc_with_gaps(data)
        for data in (
            portugal_data, us_data, poland_data, germany_data,
            korea_data, afghanistan_data,
        )
    )

    ax.plot(
        portugal_data["Year"],
        portugal_data["GDPpc"],
        color="#0B3C6D",
        linewidth=3.6,
        label="Portugal",
        zorder=5,
    )
    ax.plot(
        us_data["Year"],
        us_data["GDPpc"],
        color="#A93226",
        linewidth=2.6,
        linestyle="--",
        label="United States",
        alpha=0.95,
    )
    ax.plot(
        poland_data["Year"],
        poland_data["GDPpc"],
        color="#2E8B57",
        linewidth=2.4,
        linestyle="-.",
        label="Poland",
        alpha=0.9,
    )
    ax.plot(
        germany_data["Year"],
        germany_data["GDPpc"],
        color="#7D3C98",
        linewidth=2.4,
        linestyle=":",
        label="Germany",
        alpha=0.9,
    )
    ax.plot(
        korea_data["Year"],
        korea_data["GDPpc"],
        color="#E67E22",
        linewidth=2.4,
        linestyle=(0, (5, 2)),
        label="Korea",
        alpha=0.9,
    )
    ax.plot(
        afghanistan_data["Year"],
        afghanistan_data["GDPpc"],
        color="#5D6D7E",
        linewidth=2.3,
        linestyle=(0, (1, 2)),
        label="Afghanistan",
        alpha=0.95,
    )

    # A single available year between gaps needs a point: a line alone is invisible.
    for data, color in (
        (portugal_data, "#0B3C6D"), (us_data, "#A93226"),
        (poland_data, "#2E8B57"), (germany_data, "#7D3C98"),
        (korea_data, "#E67E22"), (afghanistan_data, "#5D6D7E"),
    ):
        available = data["GDPpc"].notna()
        isolated = (
            available
            & ~available.shift(1, fill_value=False)
            & ~available.shift(-1, fill_value=False)
        )
        ax.scatter(
            data.loc[isolated, "Year"], data.loc[isolated, "GDPpc"],
            color=color, s=15, zorder=6,
        )

    if title:
        ax.set_title(title, fontsize=22, fontweight="bold", loc="left", pad=14)
    ax.set_xlabel("Year", fontsize=17)
    ax.set_ylabel("GDP per capita (2011$)", fontsize=17)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))

    ax.legend(frameon=False, ncol=2, loc="upper left", fontsize=15)
    ax.grid(alpha=0.28, linestyle="--", linewidth=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")
    ax.tick_params(colors="#333333", labelsize=14)
    ax.margins(x=0.01)

    fig.text(
        0.01,
        0.01,
        "Source: Maddison Project Database 2023 (Bolt and van Zanden et al.). Missing years left blank.",
        ha="left",
        fontsize=12,
        color="#333333",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(output_path, dpi=220)
    if show_plot:
        plt.show()
    plt.close(fig)


def capital_output_at_domestic_prices(
    df: pd.DataFrame, countries: list[str]
) -> pd.DataFrame:
    """Value the ratio at domestic 2021 prices, retaining national volume growth.

    PWT anchors rnna and rgdpna to separately PPP-converted benchmark levels.
    Undo their relative benchmark conversion with (pl_n/pl_gdpo) in 2021.
    Keep this factor fixed over time to preserve the constant-price series.
    """
    required_cols = {"countrycode", "year", "rnna", "rgdpna", "pl_n", "pl_gdpo"}
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in PWT data: {sorted(missing)}")

    ky = df[df["countrycode"].isin(countries)].copy()
    benchmark = ky[ky["year"] == PWT_PRICE_YEAR].set_index(
        "countrycode", verify_integrity=True
    ).reindex(countries)
    price_levels = benchmark[["pl_n", "pl_gdpo"]].astype(float)
    invalid = price_levels.isna().any(axis=1) | (price_levels <= 0).any(axis=1)
    if invalid.any():
        raise ValueError(
            f"Missing or invalid {PWT_PRICE_YEAR} benchmark prices for: "
            f"{price_levels.index[invalid].tolist()}"
        )
    price_factors = price_levels["pl_n"] / price_levels["pl_gdpo"]
    ky = ky[(ky["rnna"] > 0) & (ky["rgdpna"] > 0)].copy()
    ky["KY"] = (
        ky["rnna"].astype(float) / ky["rgdpna"].astype(float)
        * ky["countrycode"].map(price_factors)
    )
    return ky.sort_values(["countrycode", "year"])


def save_ky_ratio_plot_from_pwt(
    pwt_file: Path, output_path: Path, show_plot: bool = False
) -> None:
    df = pd.read_stata(pwt_file)
    ky = capital_output_at_domestic_prices(df, ["USA", "PRT", "DEU", "ESP"])

    us = ky[ky["countrycode"] == "USA"]
    pt = ky[ky["countrycode"] == "PRT"]
    de = ky[ky["countrycode"] == "DEU"]
    es = ky[ky["countrycode"] == "ESP"]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12.8, 7.2))

    ax.plot(
        us["year"],
        us["KY"],
        color="#A93226",
        linewidth=3.0,
        linestyle="--",
        label="United States",
    )
    ax.plot(
        pt["year"],
        pt["KY"],
        color="#0B3C6D",
        linewidth=3.2,
        label="Portugal",
        zorder=5,
    )
    ax.plot(
        de["year"],
        de["KY"],
        color="#7D3C98",
        linewidth=2.8,
        linestyle=":",
        label="Germany",
        alpha=0.95,
    )
    ax.plot(
        es["year"],
        es["KY"],
        color="#2E8B57",
        linewidth=2.8,
        linestyle="-.",
        label="Spain",
        alpha=0.95,
    )

    ax.set_xlabel("Year", fontsize=17)
    ax.set_ylabel("Capital stock / annual GDP", fontsize=17)
    ax.set_ylim(0, 6)
    ax.legend(frameon=False, fontsize=13, ncol=2, loc="best")

    ax.grid(alpha=0.28, linestyle="--", linewidth=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")
    ax.tick_params(colors="#333333", labelsize=14)
    ax.margins(x=0.01)

    fig.text(
        0.01,
        0.01,
        "Source: Penn World Table 11.0. Capital and GDP valued at domestic 2021 prices.",
        ha="left",
        fontsize=12,
        color="#333333",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(output_path, dpi=220)
    if show_plot:
        plt.show()
    plt.close(fig)


def save_ky_ratio_us_only_plot_from_pwt(
    pwt_file: Path, output_path: Path, show_plot: bool = False
) -> None:
    df = pd.read_stata(pwt_file)

    us = capital_output_at_domestic_prices(df, ["USA"])

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12.8, 7.2))

    ax.plot(
        us["year"],
        us["KY"],
        color="#A93226",
        linewidth=3.2,
        label="United States",
    )

    ax.set_xlabel("Year", fontsize=17)
    ax.set_ylabel("Capital stock / annual GDP", fontsize=17)
    ax.set_ylim(0, 6)
    ax.legend(frameon=False, fontsize=15, loc="best")

    ax.grid(alpha=0.28, linestyle="--", linewidth=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")
    ax.tick_params(colors="#333333", labelsize=14)
    ax.margins(x=0.01)

    fig.text(
        0.01,
        0.01,
        "Source: Penn World Table 11.0. Capital and GDP valued at domestic 2021 prices.",
        ha="left",
        fontsize=12,
        color="#333333",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(output_path, dpi=220)
    if show_plot:
        plt.show()
    plt.close(fig)


def observed_labor_share_data(
    df: pd.DataFrame, flags: pd.DataFrame, countries: list[str]
) -> pd.DataFrame:
    """Leave gaps for missing or non-observed labor shares using PWT flags."""
    required_cols = {"countrycode", "year", "labsh"}
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in PWT data: {sorted(missing)}")

    ls = df.loc[
        df["countrycode"].isin(countries) & (df["year"] >= START_YEAR),
        ["countrycode", "year", "labsh"],
    ].copy()
    ls = ls.merge(
        flags[["countrycode", "year", "i_labsh2"]],
        on=["countrycode", "year"], how="left", validate="one_to_one",
    )
    # 1 = observed; 0 = constant/interpolated; 2 = extrapolated mixed-income share.
    observed = ls["i_labsh2"].eq(1) & ls["labsh"].between(0, 1)
    ls.loc[~observed, "labsh"] = np.nan
    # Retain missing years explicitly so matplotlib never bridges an unknown gap.
    if ls.empty:
        return ls
    annual_index = pd.MultiIndex.from_product(
        [countries, range(int(ls["year"].min()), int(ls["year"].max()) + 1)],
        names=["countrycode", "year"],
    )
    return ls.set_index(["countrycode", "year"]).reindex(annual_index).reset_index()


def save_labor_share_plot_from_pwt(
    pwt_file: Path, output_path: Path, show_plot: bool = False
) -> None:
    df = pd.read_stata(pwt_file)
    flags_path = Path(__file__).resolve().parents[1] / "data" / "pwt110_labor_share_flags.csv"
    flags = pd.read_csv(flags_path)
    ls = observed_labor_share_data(df, flags, ["USA", "PRT", "DEU", "ESP"])

    us = ls[ls["countrycode"] == "USA"]
    pt = ls[ls["countrycode"] == "PRT"]
    de = ls[ls["countrycode"] == "DEU"]
    es = ls[ls["countrycode"] == "ESP"]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12.8, 7.2))

    ax.plot(us["year"], us["labsh"], color="#A93226", linewidth=3.0, linestyle="--", label="United States")
    ax.plot(pt["year"], pt["labsh"], color="#0B3C6D", linewidth=3.2, label="Portugal", zorder=5)
    ax.plot(de["year"], de["labsh"], color="#7D3C98", linewidth=2.8, linestyle=":", label="Germany", alpha=0.95)
    ax.plot(es["year"], es["labsh"], color="#2E8B57", linewidth=2.8, linestyle="-.", label="Spain", alpha=0.95)

    ax.set_xlabel("Year", fontsize=17)
    ax.set_ylabel("Labor share (labsh)", fontsize=17)
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, fontsize=13, ncol=2, loc="best")

    ax.grid(alpha=0.28, linestyle="--", linewidth=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")
    ax.tick_params(colors="#333333", labelsize=14)
    ax.margins(x=0.01)

    fig.text(
        0.01,
        0.01,
        "Source: Penn World Table 11.0. Observed labor shares only; no interpolation or extrapolation.",
        ha="left",
        fontsize=12,
        color="#333333",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(output_path, dpi=220)
    if show_plot:
        plt.show()
    plt.close(fig)


def save_investment_rate_plot_from_pwt(
    pwt_file: Path, output_path: Path, start_year: int = 1950, show_plot: bool = False
) -> None:
    df = pd.read_stata(pwt_file)

    required_cols = {"countrycode", "year", "csh_i"}
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in PWT data: {sorted(missing)}")

    inv = df[df["countrycode"].isin(["USA", "KOR"])].copy()
    inv = inv[(inv["year"] >= start_year) & inv["csh_i"].notna()]
    inv["inv_rate"] = 100 * inv["csh_i"]
    inv = inv.sort_values(["countrycode", "year"])

    us = inv[inv["countrycode"] == "USA"]
    korea = inv[inv["countrycode"] == "KOR"]

    afg_wb = pd.DataFrame()
    try:
        afg_wb = fetch_world_bank_indicator(
            countries=["AFG"],
            indicator=WB_INVESTMENT_INDICATOR,
            start_year=start_year,
        )
        afg_wb = afg_wb[afg_wb["value"].notna()].copy()
    except Exception as error:
        print(f"Could not fetch Afghanistan WB investment data: {error}")

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12.8, 7.2))

    ax.plot(
        us["year"],
        us["inv_rate"],
        color="#A93226",
        linewidth=3.0,
        linestyle="--",
        label="United States",
    )
    ax.plot(
        korea["year"],
        korea["inv_rate"],
        color="#E67E22",
        linewidth=3.0,
        linestyle="-",
        label="Korea",
    )
    if not afg_wb.empty:
        ax.plot(
            afg_wb["year"],
            afg_wb["value"],
            color="#5D6D7E",
            linewidth=2.8,
            linestyle=(0, (1, 2)),
            label="Afghanistan (WB)",
        )
    ax.set_xlabel("Year", fontsize=17)
    ax.set_ylabel("Investment rate (% of GDP)", fontsize=17)
    ax.legend(frameon=False, fontsize=15, loc="best")

    ax.grid(alpha=0.28, linestyle="--", linewidth=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")
    ax.tick_params(colors="#333333", labelsize=14)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}"))
    ax.margins(x=0.01)

    fig.text(
        0.01,
        0.01,
        "Source: Penn World Table 11.0 (pwt110.dta). Variable: csh_i (% share of investment in GDP).",
        ha="left",
        fontsize=12,
        color="#333333",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(output_path, dpi=220)
    if show_plot:
        plt.show()
    plt.close(fig)


def fetch_world_bank_indicator(
    countries: list[str], indicator: str, start_year: int
) -> pd.DataFrame:
    endpoint = (
        f"https://api.worldbank.org/v2/country/{';'.join(countries)}/indicator/{indicator}"
    )
    params = {
        "date": f"{start_year}:2025",
        "format": "json",
        "per_page": 20000,
    }
    with urlopen(f"{endpoint}?{urlencode(params)}") as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("Unexpected World Bank API response format.")

    raw = pd.DataFrame(payload[1])
    if raw.empty:
        raise ValueError("No data returned from World Bank API.")

    raw["year"] = pd.to_numeric(raw["date"], errors="coerce")
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
    raw["iso3"] = raw["countryiso3code"]
    raw["country_name"] = raw["country"].apply(
        lambda x: x.get("value") if isinstance(x, dict) else x
    )

    out = raw[["iso3", "country_name", "year", "value"]].dropna(subset=["year"])
    out = out[out["year"] >= start_year].sort_values(["iso3", "year"])
    return out


def save_investment_rate_plot_from_wb(
    output_path: Path, start_year: int = 1950, show_plot: bool = False
) -> None:
    wb_countries = ["USA", "KOR", "AFG"]
    country_labels = {
        "USA": "United States",
        "KOR": "Korea",
        "AFG": "Afghanistan",
    }

    inv = fetch_world_bank_indicator(
        countries=wb_countries,
        indicator=WB_INVESTMENT_INDICATOR,
        start_year=start_year,
    )
    inv = inv[inv["value"].notna()].copy()

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12.8, 7.2))

    styles = {
        "USA": {"color": "#A93226", "linewidth": 3.0, "linestyle": "--"},
        "KOR": {"color": "#E67E22", "linewidth": 3.0, "linestyle": "-"},
        "AFG": {"color": "#5D6D7E", "linewidth": 2.8, "linestyle": (0, (1, 2))},
    }

    for iso3 in wb_countries:
        series = inv[inv["iso3"] == iso3]
        if series.empty:
            continue
        ax.plot(
            series["year"],
            series["value"],
            label=country_labels[iso3],
            alpha=0.95,
            **styles[iso3],
        )

    ax.set_xlabel("Year", fontsize=17)
    ax.set_ylabel("Investment rate (% of GDP)", fontsize=17)
    ax.set_title("Gross Capital Formation (% of GDP)", fontsize=22, fontweight="bold", loc="left", pad=14)
    ax.legend(frameon=False, fontsize=15, loc="best")

    ax.grid(alpha=0.28, linestyle="--", linewidth=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#888888")
    ax.spines["bottom"].set_color("#888888")
    ax.tick_params(colors="#333333", labelsize=14)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}"))
    ax.margins(x=0.01)

    fig.text(
        0.01,
        0.01,
        "Source: World Bank WDI, indicator NE.GDI.TOTL.ZS (Gross capital formation, % of GDP).",
        ha="left",
        fontsize=12,
        color="#333333",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(output_path, dpi=220)
    if show_plot:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot Portugal GDP per capita (level) from Maddison data."
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not display plot windows (save PNG files only).",
    )
    args = parser.parse_args()
    show_plots = not args.no_show

    chapter_dir = Path(__file__).resolve().parents[1]
    base_dir = chapter_dir / "slides" / "figures"
    excel_file = chapter_dir / "data" / "mpd2023_web.xlsx"

    pt = load_country_gdppc(excel_file, country_name="Portugal", sheet_name="GDPpc")
    us = load_country_gdppc(
        excel_file, country_name="United States", sheet_name="GDPpc"
    )
    poland = load_country_gdppc(excel_file, country_name="Poland", sheet_name="GDPpc")
    germany = load_country_gdppc(
        excel_file, country_name="Germany", sheet_name="GDPpc"
    )
    korea = load_country_gdppc(
        excel_file, country_name="Republic of Korea", sheet_name="GDPpc"
    )
    afghanistan = load_country_gdppc(
        excel_file, country_name="Afghanistan", sheet_name="GDPpc"
    )

    pt_1865 = pt[pt["Year"] >= START_YEAR].copy()
    us_1865 = us[us["Year"] >= START_YEAR].copy()
    poland_1865 = poland[poland["Year"] >= START_YEAR].copy()
    germany_1865 = germany[germany["Year"] >= START_YEAR].copy()
    korea_1865 = korea[korea["Year"] >= START_YEAR].copy()
    afghanistan_1865 = afghanistan[afghanistan["Year"] >= START_YEAR].copy()
    out_1865 = base_dir / "portugal_gdppc_1865.png"
    save_gdppc_plot(
        pt_1865,
        us_1865,
        poland_1865,
        germany_1865,
        korea_1865,
        afghanistan_1865,
        out_1865,
        "",
        show_plot=show_plots,
    )

    out_log_gdppc = base_dir / "portugal_us_log_gdppc_1865.png"
    save_log_gdppc_fit_plot(
        pt,
        us,
        out_log_gdppc,
        show_plot=show_plots,
    )

    pwt_file = chapter_dir.parent / "02-production-model" / "data" / "pwt110.dta"
    out_ky = base_dir / "ky_ratio_us_portugal_pwt110.png"
    save_ky_ratio_plot_from_pwt(
        pwt_file,
        out_ky,
        show_plot=show_plots,
    )

    out_ky_us = base_dir / "ky_ratio_us_pwt110.png"
    save_ky_ratio_us_only_plot_from_pwt(
        pwt_file,
        out_ky_us,
        show_plot=show_plots,
    )

    out_labor_share = base_dir / "labor_share_us_portugal_germany_spain_pwt110.png"
    save_labor_share_plot_from_pwt(
        pwt_file,
        out_labor_share,
        show_plot=show_plots,
    )

    out_investment_rate = base_dir / "investment_rate_us_korea_pwt110.png"
    save_investment_rate_plot_from_pwt(
        pwt_file,
        out_investment_rate,
        start_year=1950,
        show_plot=show_plots,
    )

    print(f"Saved: {out_1865}")
    print(f"Saved: {out_log_gdppc}")
    print(f"Saved: {out_ky}")
    print(f"Saved: {out_ky_us}")
    print(f"Saved: {out_labor_share}")
    print(f"Saved: {out_investment_rate}")
    print(
        f"Range ({START_YEAR}+ figure): {int(pt_1865['Year'].min())}-{int(pt_1865['Year'].max())} "
        f"| observations: {len(pt_1865)}"
    )
