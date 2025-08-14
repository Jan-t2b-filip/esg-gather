import re

RE_CO2E = r"CO\s*2\s*e"

PATTERNS = {
    "scope": re.compile(
        rf"\bScope\s*(?P<scope>[123])\b.*?"
        rf"(?P<val>\d{{1,3}}(?:[.,\s]\d{{3}})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\s*"
        rf"(?P<unit>(?:mn\s*)?t|kt|t|kg)?\s*{RE_CO2E}",
        re.I,
    ),
    "scope2_market": re.compile(
        rf"\bScope\s*2\b.*?\bmarket[-\s]*based\b.*?"
        rf"(?P<val>\d{{1,3}}(?:[.,\s]\d{{3}})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\s*"
        rf"(?P<unit>(?:mn\s*)?t|kt|t|kg)?\s*{RE_CO2E}",
        re.I,
    ),
    "scope2_location": re.compile(
        rf"\bScope\s*2\b.*?\blocation[-\s]*based\b.*?"
        rf"(?P<val>\d{{1,3}}(?:[.,\s]\d{{3}})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\s*"
        rf"(?P<unit>(?:mn\s*)?t|kt|t|kg)?\s*{RE_CO2E}",
        re.I,
    ),
    "total": re.compile(
        rf"\b(?:Total|Celkem)\b.*?\b(?:GHG|greenhouse gas|emise)\b.*?"
        rf"(?P<val>\d{{1,3}}(?:[.,\s]\d{{3}})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\s*"
        rf"(?P<unit>(?:mn\s*)?t|kt|t|kg)?\s*{RE_CO2E}",
        re.I,
    ),
    "inv_int_mn": re.compile(
        rf"(?:t\s*CO2e|CO2e\s*\(t\))\s*(?:/|per)\s*(?:€|EUR)\s*(?:mn|m)\b.*?"
        rf"(?P<val>\d+(?:[.,]\d+)?)",
        re.I,
    ),
    "inv_int_bn": re.compile(
        rf"(?:t\s*CO2e|CO2e\s*\(t\))\s*(?:/|per)\s*(?:€|EUR)\s*bn\b.*?"
        rf"(?P<val>\d+(?:[.,]\d+)?)",
        re.I,
    ),
    "inv_int_kg_mn": re.compile(
        rf"(?:kg\s*CO2e)\s*(?:/|per)\s*(?:€|EUR)\s*(?:mn|m)\b.*?"
        rf"(?P<val>\d+(?:[.,]\d+)?)",
        re.I,
    ),
}

ROW_PATTERNS_OWNOPS = {
    "ownops_scope1_t": r"Gross\s+Scope\s*1\s+GHG\s+emissions(?!.*per\s+employee)",
    "ownops_scope2_location_t": r"Gross\s+location[-\s]*based\s+Scope\s*2\s+GHG\s+emissions(?!.*per\s+employee)",
    "ownops_scope2_market_t": r"Gross\s+market[-\s]*based\s+Scope\s*2\s+GHG\s+emissions(?!.*per\s+employee)",
    "ownops_scope3_t": r"Scope\s*3\s+GHG\s+emissions(?!.*per\s+employee)",
    "ownops_total_location_t": r"Total\s+own\s+operations\s+GHG\s+emissions\s*\(location[-\s]*based\)(?!.*per\s+employee)",
    "ownops_total_market_t": r"Total\s+own\s+operations\s+GHG\s+emissions\s*\(market[-\s]*based\)(?!.*per\s+employee)",
}

ROW_PATTERNS_PROPRIETARY = {
    "propinv_total_t": r"Proprietary\s+investments\s+GHG\s+emissions\s*\(Scope\s*1-3\)\s*-\s*TOTAL",
}
