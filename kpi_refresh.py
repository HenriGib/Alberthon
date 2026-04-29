from __future__ import annotations

from pathlib import Path
import unicodedata

import numpy as np
import pandas as pd

OUTPUT_COLUMNS = [
    "KPI",
    "year",
    "entity",
    "direction",
    "HCVA",
    "n",
    "KTI",
    "pct_decay",
    "total_absence_days",
    "nb_employees",
    "absence_rate",
    "engagement_score",
    "RE_score",
    "strategic_hours",
    "total_hours",
    "nb_formations",
    "strategic_share",
]

DASHBOARD_OUTPUTS = {
    "yearly": Path("outputs/kpi_yearly.csv"),
    "by_entity": Path("outputs/kpi_by_entity.csv"),
    "by_direction": Path("outputs/kpi_by_direction.csv"),
}

REPORTING_YEARS = [2023, 2024, 2025]
SKILL_DECAY_MONTHS = 12

DIMENSIONS = {
    "yearly": ["year"],
    "by_entity": ["year", "entity"],
    "by_direction": ["year", "direction"],
}

TRAINING_FILE = Path("Training_Records_Unnamed.xlsx")
ABSENCE_FILE = Path("20260121 - Absentéisme_-_détail_affectation_-_Bilan_social 2025.xlsx")


def normalize_column_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.strip().lower().replace(" ", "_")
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]
    return df


def normalize_employee_code(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)


def build_kpi_views(
    df: pd.DataFrame,
    *,
    kpi_name: str,
    value_col: str,
    agg: str = "mean",
    count_col: str | None = None,
    value_name: str = "value",
) -> dict[str, pd.DataFrame]:
    views: dict[str, pd.DataFrame] = {}
    for view_name, group_cols in DIMENSIONS.items():
        grouped = (
            df.dropna(subset=["year"])
            .groupby(group_cols, dropna=False)
            .agg(value=(value_col, agg), n=(count_col or value_col, "count"))
            .reset_index()
        )
        grouped.insert(0, "KPI", kpi_name)
        grouped = grouped.rename(columns={"value": value_name})
        if pd.api.types.is_numeric_dtype(grouped[value_name]):
            grouped[value_name] = grouped[value_name].round(4)
        views[view_name] = grouped
    return views


def align_to_output_schema(df: pd.DataFrame, view_name: str) -> pd.DataFrame:
    out = df.copy()
    if view_name == "yearly":
        out["entity"] = np.nan
        out["direction"] = np.nan
    elif view_name == "by_entity":
        out["direction"] = np.nan
    elif view_name == "by_direction":
        out["entity"] = np.nan
    for column in OUTPUT_COLUMNS:
        if column not in out.columns:
            out[column] = np.nan
    return out[OUTPUT_COLUMNS]


def load_training_data(path: Path = TRAINING_FILE) -> pd.DataFrame:
    df = pd.read_excel(path)
    df = normalize_columns(df)
    df = df.rename(columns={
        "employee_code": "employee_code",
        "entity": "entity",
        "direction": "direction",
        "seesion_start_date": "session_start_date",
    })
    df["employee_code"] = normalize_employee_code(df["employee_code"])
    df["entity"] = df["entity"].fillna("Non renseigne").astype(str).str.strip()
    df["direction"] = df["direction"].fillna("Non renseigne").astype(str).str.strip()
    df["session_start_date"] = pd.to_datetime(df["session_start_date"], errors="coerce", dayfirst=True)
    df["year"] = df["session_start_date"].dt.year
    return df


def load_absence_data(path: Path = ABSENCE_FILE) -> pd.DataFrame:
    df = pd.read_excel(path)
    df = normalize_columns(df)
    df = df.rename(columns={
        "employee_code": "employee_code",
        "societe": "entity",
        "organisation_1": "direction",
        "date_absence": "date_absence",
        "regroupement_jour_absences": "absence_group",
        "jours_ouvres_absence": "jours_ouvres_absence",
    })
    df["employee_code"] = normalize_employee_code(df["employee_code"])
    df["entity"] = df["entity"].fillna("Non renseigne").astype(str).str.strip()
    df["direction"] = df["direction"].fillna("Non renseigne").astype(str).str.strip()
    df["date_absence"] = pd.to_datetime(df["date_absence"], errors="coerce", dayfirst=True)
    df["year"] = df["date_absence"].dt.year
    if "absence_group" in df.columns:
        df = df[~df["absence_group"].astype(str).str.lower().str.contains("cong", na=False)].copy()
    return df


def compute_skill_decay_views(df_training: pd.DataFrame) -> dict[str, pd.DataFrame]:
    snapshots: list[pd.DataFrame] = []
    years = REPORTING_YEARS
    for year in years:
        cutoff = pd.Timestamp(year=year, month=12, day=31)
        snapshot = (
            df_training[df_training["session_start_date"] <= cutoff]
            .sort_values("session_start_date")
            .dropna(subset=["employee_code"])
            .drop_duplicates("employee_code", keep="last")
            [["employee_code", "session_start_date", "entity", "direction"]]
            .copy()
        )
        snapshot["year"] = year
        snapshot["months_since_training"] = (
            (cutoff - snapshot["session_start_date"]).dt.days / 30.44
        )
        snapshot["skill_decay_flag"] = snapshot["months_since_training"] > SKILL_DECAY_MONTHS
        snapshots.append(snapshot)

    historical = pd.concat(snapshots, ignore_index=True)
    return build_kpi_views(
        historical,
        kpi_name="Skill Decay",
        value_col="skill_decay_flag",
        agg="mean",
        count_col="employee_code",
        value_name="pct_decay",
    )


def compute_re_score_views(
    df_abs: pd.DataFrame,
    *,
    engagement_components: tuple[float, float, float] = (70, 77, 78),
    working_days: int = 218,
) -> dict[str, pd.DataFrame]:
    engagement_score = float(np.mean(engagement_components))

    def compute(group_cols: list[str]) -> pd.DataFrame:
        out = (
            df_abs.dropna(subset=["year"])
            .groupby(group_cols, dropna=False)
            .agg(
                total_absence_days=("jours_ouvres_absence", "sum"),
                nb_employees=("employee_code", "nunique"),
            )
            .reset_index()
        )
        out["absence_rate"] = out["total_absence_days"] / (out["nb_employees"] * working_days)
        out["engagement_score"] = engagement_score
        # Score borne /5 : l'engagement tire le score vers le haut, l'absenteisme le penalise.
        out["RE_score"] = (out["engagement_score"] / 20.0) / (1.0 + out["absence_rate"])
        out.insert(0, "KPI", "RE-Score")
        return out.round({"total_absence_days": 2, "absence_rate": 4, "engagement_score": 2, "RE_score": 2})

    return {view_name: compute(group_cols) for view_name, group_cols in DIMENSIONS.items()}


def replace_kpis_in_output(output_path: Path, replacement_frames: list[pd.DataFrame]) -> None:
    existing = pd.read_csv(output_path)
    if "year" in existing.columns:
        existing["year"] = pd.to_numeric(existing["year"], errors="coerce")
        existing = existing[existing["year"].isin(REPORTING_YEARS)].copy()
    to_replace = {df["KPI"].iloc[0] for df in replacement_frames if not df.empty}
    updated = existing[~existing["KPI"].isin(to_replace)].copy()
    merged = pd.concat([updated, *replacement_frames], ignore_index=True, sort=False)
    merged["year_sort"] = pd.to_numeric(merged["year"], errors="coerce")
    merged = merged.sort_values(
        by=["KPI", "year_sort", "entity", "direction"],
        na_position="last",
        kind="stable",
    ).drop(columns=["year_sort"])
    merged.to_csv(output_path, index=False)


def refresh_outputs() -> dict[str, dict[str, pd.DataFrame]]:
    training = load_training_data()
    absences = load_absence_data()
    training = training[training["year"].isin(REPORTING_YEARS)].copy()
    absences = absences[absences["year"].isin(REPORTING_YEARS)].copy()

    skill_decay_views = compute_skill_decay_views(training)
    re_views = compute_re_score_views(absences)

    for view_name, output_path in DASHBOARD_OUTPUTS.items():
        replace_kpis_in_output(
            output_path,
            [
                align_to_output_schema(skill_decay_views[view_name], view_name),
                align_to_output_schema(re_views[view_name], view_name),
            ],
        )

    return {"skill_decay": skill_decay_views, "re_score": re_views}


if __name__ == "__main__":
    refresh_outputs()
    print("Outputs refreshed:")
    for path in DASHBOARD_OUTPUTS.values():
        print(f"- {path}")
