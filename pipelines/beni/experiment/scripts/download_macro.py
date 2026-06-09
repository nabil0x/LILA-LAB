from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "macro"
OUT.mkdir(parents=True, exist_ok=True)

HEADERS = {"Accept": "text/csv"}
TIMEOUT = 120


def fetch_csv(url: str, name: str) -> Path:
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    path = OUT / f"{name}.csv"
    path.write_bytes(r.content)
    size_kb = len(r.content) / 1024
    print(f"  {name}: {size_kb:.0f} KB -> {path}")
    return path


def main() -> None:
    print("[1/4] BIS - BDT/USD end-of-period (monthly, 2014-2025)")
    fetch_csv(
        "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/M.BD.BDT.E"
        "?format=csv&startPeriod=2014-01&endPeriod=2025-12",
        "fx_bdt_usd_bis_eop_monthly",
    )

    print("[2/4] IMF - CPI level (BGD, all-items, monthly, 2014-2025)")
    fetch_csv(
        "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/CPI/5.0.0/"
        "BGD.CPI._T.IX.M?startPeriod=2014-01&endPeriod=2025-12",
        "cpi_imf_bgd_index_monthly",
    )

    print("[3/4] IMF - XDC/USD end-of-period (monthly, 2014-2025)")
    fetch_csv(
        "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/ER/4.0.1/"
        "BGD.XDC_USD.EOP_RT.M?startPeriod=2014-01&endPeriod=2025-12",
        "fx_bdt_usd_imf_eop_monthly",
    )

    print("[4/4] World Bank - reserves (annual fallback, 2014-2024)")
    r = requests.get(
        "http://api.worldbank.org/v2/country/BGD/indicator/FI.RES.TOTL.CD"
        "?date=2014:2024&format=json&per_page=200",
        timeout=TIMEOUT,
    )
    data = r.json()[1]
    reserves = pd.DataFrame(
        [{"year": int(d["date"]), "reserves_usd": d["value"]} for d in data]
    )
    path = OUT / "reserves_wb_annual.csv"
    reserves.to_csv(path, index=False)
    print(f"  reserves_wb_annual: {len(reserves)} years -> {path}")

    print("\nDone. Files in", OUT)
    for f in sorted(OUT.iterdir()):
        print(f"  {f.name}  ({f.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
