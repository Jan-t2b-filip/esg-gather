from pathlib import Path
import pandas as pd
from .utils import extract_lines
from .parsers import scan_metrics_by_lines, parse_supplement_ownops

def main():
    p1 = Path("/storage/.../Allianz_Group_Sustainability_Report_2023-web.pdf")
    p2 = Path("/storage/.../en-allianz-group-annual-report-2024.pdf")
    p3 = Path("/storage/.../en-allianz-group-non-financial-supplement-2024.pdf")

    records = []

    for pdf in [p1, p2]:
        if pdf.exists():
            lines = extract_lines(pdf)
            data = scan_metrics_by_lines(lines)
            data["source_pdf"] = pdf.name
            records.append(data)

    if p3.exists():
        lines = extract_lines(p3)
        data = parse_supplement_ownops(lines)
        data["source_pdf"] = p3.name
        records.append(data)

    df = pd.DataFrame(records)
    out_csv = Path("/storage/.../esg_metrics.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Saved: {out_csv}")

if __name__ == "__main__":
    main()
