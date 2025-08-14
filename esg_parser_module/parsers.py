import re
from typing import List, Dict
from .utils import to_float, first_number_after
from .config import PATTERNS, ROW_PATTERNS_OWNOPS, ROW_PATTERNS_PROPRIETARY

def scan_metrics_by_lines(lines: List[str]) -> Dict[str, float]:
    hits = {}
    n = len(lines)
    for i in range(n):
        window = lines[i] + (" " + lines[i+1] if i+1 < n else "")

        for m in PATTERNS["scope2_location"].finditer(window):
            v = to_float(m.group("val"), m.group("unit") or "t")
            if v is not None:
                hits["scope2_location_t"] = v
        for m in PATTERNS["scope2_market"].finditer(window):
            v = to_float(m.group("val"), m.group("unit") or "t")
            if v is not None:
                hits["scope2_market_t"] = v
                hits["scope2_co2e_t"] = v

        for m in PATTERNS["scope"].finditer(window):
            scope = m.group("scope")
            v = to_float(m.group("val"), m.group("unit") or "t")
            if v is None:
                continue
            key = f"scope{scope}_co2e_t"
            if key == "scope2_co2e_t" and "scope2_co2e_t" in hits:
                continue
            hits[key] = v

        for m in PATTERNS["total"].finditer(window):
            v = to_float(m.group("val"), m.group("unit") or "t")
            if v and 0 < v < 1e9:
                hits.setdefault("total_co2e_t", v)

        for pat_key in ["inv_int_mn", "inv_int_bn", "inv_int_kg_mn"]:
            m = PATTERNS[pat_key].search(window)
            if m:
                val = to_float(m.group("val"), "t" if "kg" not in pat_key else "kg")
                if val:
                    if pat_key == "inv_int_bn":
                        val /= 1000.0
                    hits["investments_intensity_t_per_eur_mn"] = val

    if "scope2_co2e_t" not in hits:
        if "scope2_market_t" in hits:
            hits["scope2_co2e_t"] = hits["scope2_market_t"]
        elif "scope2_location_t" in hits:
            hits["scope2_co2e_t"] = hits["scope2_location_t"]

    s12 = sum(hits.get(k, 0) for k in ["scope1_co2e_t","scope2_co2e_t"])
    if hits.get("total_co2e_t", 0) < s12:
        hits.pop("total_co2e_t", None)

    return hits

def current_section_tracker(lines: List[str]) -> List[str]:
    section = ""
    tags = []
    for ln in lines:
        low = ln.lower()
        if "proprietary investments ghg emissions" in low:
            section = "proprietary"
        elif "own operations" in low:
            section = "ownops"
        if "tables of the sustainability statement" in low:
            section = ""
        tags.append(section)
    return tags

def parse_supplement_ownops(lines: List[str]) -> Dict[str, float]:
    hits: Dict[str, float] = {}
    tags = current_section_tracker(lines)

    for i, ln in enumerate(lines):
        sec = tags[i]
        row_next = ln + " " + (lines[i+1] if i + 1 < len(lines) else "")

        if sec == "ownops":
            for key, pat in ROW_PATTERNS_OWNOPS.items():
                if re.search(pat, ln, flags=re.I) or re.search(pat, row_next, flags=re.I):
                    val_str = first_number_after(row_next if re.search(pat, row_next, re.I) else ln, pat)
                    if val_str:
                        val = to_float(val_str, "t")
                        if val is not None:
                            hits[key] = val

        elif sec == "proprietary":
            for key, pat in ROW_PATTERNS_PROPRIETARY.items():
                if re.search(pat, ln, flags=re.I) or re.search(pat, row_next, flags=re.I):
                    mnum = re.search(pat + r".*?" + r"(-?\d+(?:[.,]\d+)?)", row_next, flags=re.I)
                    if mnum:
                        val = to_float(mnum.group(1), "t")
                        if val is not None:
                            hits[key] = val

    if "ownops_scope2_market_t" in hits and "ownops_scope2_t" not in hits:
        hits["ownops_scope2_t"] = hits["ownops_scope2_market_t"]

    return hits
