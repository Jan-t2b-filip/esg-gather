#!/usr/bin/env python3
"""
ESG baseline training (Singularity/PBS friendly)

- Input:  data/processed/esg_long.csv (long formát metrik)
- Output: out/model.joblib, out/metrics.json
- ClearML: zapne se automaticky, pokud je CLEARML=1 a/nebo jsou dostupné
           proměnné CLEARML_API_* (nebo ~/.clearml/clearml.conf).
"""

import os, json, pathlib, warnings, argparse
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

def clearml_enabled() -> bool:
    if os.environ.get("CLEARML", "0") == "1":
        return True
    # pokud jsou k dispozici přihlašovací údaje, také povol
    if os.environ.get("CLEARML_API_ACCESS_KEY") and os.environ.get("CLEARML_API_SECRET_KEY"):
        return True
    # fallback na lokální config
    return os.path.exists(os.path.expanduser("~/.clearml/clearml.conf"))

def init_clearml():
    try:
        from clearml import Task
        project = os.environ.get("CLEARML_PROJECT", "esg-gather")
        task_name = os.environ.get("CLEARML_TASK_NAME", "ESG baseline Ridge")
        task = Task.init(project_name=project, task_name=task_name, output_uri=False)
        return task
    except Exception as e:
        warnings.warn(f"ClearML init failed: {e}")
        return None

def load_data(csv_path: str, min_year: int = 2023) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if "year" not in df.columns:
        warnings.warn("Sloupec 'year' chybí – nastavím všem year=2024 (fallback).")
        df["year"] = 2024
    return df[df["year"] >= min_year].copy()

def wide_from_long(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    if "metric_std" in df.columns:
        wide = df.pivot_table(index=["source_pdf","year"], columns="metric_std",
                              values="value", aggfunc="first")
    else:
        metric_cols = [c for c in df.columns if c not in ("source_pdf","year")]
        wide = df.set_index(["source_pdf","year"])[metric_cols]
    wide = wide.replace([np.inf, -np.inf], np.nan).dropna(axis=1, how="all").fillna(0.0)
    if wide.shape[1] == 0:
        raise ValueError("Po pivotu nemám žádné feature sloupce – zkontroluj vstupní CSV.")
    candidates = [c for c in ["ownops_total_market_t","ownops_total_location_t","propinv_total_t"] if c in wide.columns]
    target = candidates[0] if candidates else wide.columns[0]
    return wide, target

def train_model(wide: pd.DataFrame, target: str, test_size: float = 0.25, seed: int = 42):
    y = wide[target].astype(float).values
    X = wide.drop(columns=[target]).astype(float).values

    if X.shape[0] < 4 or len(np.unique(y)) < 2:
        warnings.warn("Málo dat – použiju train==test pro průchod pipeline.")
        test_size = 0.0

    if test_size > 0:
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size, random_state=seed)
    else:
        X_tr, y_tr = X, y
        X_te, y_te = X, y

    model = Ridge(alpha=1.0)
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    mae = float(mean_absolute_error(y_te, pred))
    r2  = float(r2_score(y_te, pred))
    return model, {"target": target, "mae": mae, "r2": r2, "n": int(X.shape[0]), "p": int(X.shape[1])}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.environ.get("ESG_DATA", "data/processed/esg_long.csv"))
    ap.add_argument("--out",  default=os.environ.get("ESG_OUT", "out"))
    ap.add_argument("--min-year", type=int, default=int(os.environ.get("ESG_MIN_YEAR", "2023")))
    ap.add_argument("--seed", type=int, default=int(os.environ.get("SEED", "42")))
    args = ap.parse_args()

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_data(args.data, args.min_year)
    wide, target = wide_from_long(df)
    model, metrics = train_model(wide, target, seed=args.seed)

    # uložit artefakty
    import joblib
    joblib.dump(model, out_dir / "model.joblib")
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # ClearML (pokud povoleno)
    if clearml_enabled():
        task = init_clearml()
        if task:
            logger = task.get_logger()
            logger.report_text(f"Metrics: {metrics}")
            try:
                logger.upload_artifact("model", str(out_dir / "model.joblib"))
            except Exception as e:
                warnings.warn(f"ClearML upload_artifact failed: {e}")
            task.mark_completed()

    print("OK", metrics)

if __name__ == "__main__":
    main()
