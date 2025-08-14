import re
import pdfplumber

def extract_lines(pdf_path, x_tol=2, y_tol=2):
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text(x_tolerance=x_tol, y_tolerance=y_tol) or ""
            for ln in txt.splitlines():
                ln = (ln.replace("\u00A0", " ")
                        .replace("CO₂e", "CO2e")
                        .replace("–", "-"))
                ln = re.sub(r"\s+", " ", ln).strip()
                if ln:
                    lines.append(ln)
    return lines

def to_float(num_str, unit="t"):
    s = num_str.strip().replace(" ", "")
    if "," in s and "." in s:
        last = max(s.rfind(","), s.rfind("."))
        s = s.replace(".", "").replace(",", ".") if s[last] == "," else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", "") if (s.count(",")==1 and len(s.split(",")[-1])==3) else s.replace(",", ".")
    if sum(ch.isdigit() for ch in s) > 9:
        return None
    try:
        val = float(s)
    except ValueError:
        return None

    unit = (unit or "t").lower()
    if unit.startswith("k") and "g" not in unit:
        val *= 1_000
    if "mn" in unit and "kg" not in unit:
        val *= 1_000_000
    if "kg" in unit:
        val /= 1_000
    return val

NUM = r"(-?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|-?\d+(?:[.,]\d+)?)"

def first_number_after(text: str, label_pat: str):
    m = re.search(label_pat + r"\s+" + NUM, text, flags=re.I)
    return m.group(1) if m else None
