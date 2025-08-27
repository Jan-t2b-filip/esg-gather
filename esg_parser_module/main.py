from pathlib import Path
import pandas as pd
from .utils import extract_lines
from .parsers import scan_metrics_by_lines, parse_supplement_ownops

from pathlib import Path
import pandas as pd
from .utils import extract_lines
from .parsers import scan_metrics_by_lines, parse_supplement_ownops

# Cesty k PDF souborům
P1 = Path("data/raw/Allianz_Group_Sustainability_Report_2023-web.pdf")
P2 = Path("data/raw/en-allianz-group-annual-report-2024.pdf")
P3 = Path("data/raw/en-allianz-group-non-financial-supplement-2024.pdf")

# Výstupní cesta (relativní k projektu)
OUT_CSV = Path("data/processed/esg_metrics.csv")


def main():
    records = []

    # Sustainability 2023 a Annual 2024
    for pdf in [P1, P2]:
        if pdf.exists():
            lines = extract_lines(pdf)
            base = scan_metrics_by_lines(lines)
            base["source_pdf"] = pdf.name
            records.append(base)

    # Supplement 2024
    if P3.exists():
        lines = extract_lines(P3)
        extra = parse_supplement_ownops(lines)
        extra["source_pdf"] = P3.name
        records.append(extra)

    # Uložení výsledků
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(OUT_CSV, index=False)
    print(f"Saved: {OUT_CSV}")
