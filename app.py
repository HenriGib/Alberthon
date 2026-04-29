from pathlib import Path
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

OUTPUT_DIR = Path("outputs")
REPORTING_YEARS = {2023, 2024, 2025}

CACEIS_RED = "#D65063"
CACEIS_GREY = "#888B8D"
CACEIS_GREY_BLUE = "#5C768D"
CACEIS_STEEL_BLUE = "#4A6E8C"
NEUTRAL_BG = "rgba(136, 139, 141, 0.10)"

KPI_CONFIG = [
    {
        "id": "CHHI",
        "label": "Global Human Capital Score (CHHI)",
        "col": "CHHI Index",
        "unit": "%",
        "target": 80,
        "rev": False,
        "is_master": True,
        "def": "CACEIS Human Capital Health Index (CHHI)",
        "val": "Global Human Capital Score built from available KPI pillars.",
        "form": "Weighted target achievement with available-weight rebalancing",
        "logic": ">80% (Green) / >64% (Yellow) / <64% (Red)",
    },
    {
        "id": "HCVA",
        "label": "KPI 1: Productivity (HCVA)",
        "col": "HCVA (kEUR)",
        "unit": " kEUR",
        "target": 145,
        "rev": False,
        "is_master": False,
        "def": "Human Capital Value Added (HCVA) per FTE",
        "val": "Financial efficiency of human capital.",
        "form": "PNB / FTE",
        "logic": ">145 kEUR (Green) / >116 kEUR (Yellow) / <116 kEUR (Red)",
    },
    {
        "id": "KTI",
        "label": "KPI 2: Knowledge (KTI)",
        "col": "KTI (%)",
        "unit": "%",
        "target": 75,
        "rev": False,
        "is_master": False,
        "def": "Knowledge Transfer Index (KTI)",
        "val": "Training ROI and skill application.",
        "form": "Average of application scores after training",
        "logic": ">75% (Green) / >60% (Yellow) / <60% (Red)",
    },
    {
        "id": "SD",
        "label": "KPI 3: Risk (Skill Decay)",
        "col": "Skill Decay (%)",
        "unit": "%",
        "target": 15,
        "rev": True,
        "is_master": False,
        "def": "Skill Decay Rate",
        "val": "Share of employees whose last training is older than 12 months, measured at year end.",
        "form": "% without training > 12 months as of 31/12/Y",
        "logic": "<12% (Green) / <18% (Yellow) / >18% (Red)",
    },
    {
        "id": "RE",
        "label": "KPI 4: Resilience (RE-Score)",
        "col": "RE-Score",
        "unit": " /5",
        "target": 4.0,
        "rev": False,
        "is_master": False,
        "def": "Resilience and Engagement Score",
        "val": "Bounded /5 score combining engagement and absenteeism.",
        "form": "(engagement / 20) / (1 + absenteeism rate)",
        "logic": ">4.0 (Green) / >3.2 (Yellow) / <3.2 (Red)",
    },
    {
        "id": "SPE",
        "label": "KPI 5: Strategy (SPE)",
        "col": "SPE (%)",
        "unit": "%",
        "target": 25,
        "rev": False,
        "is_master": False,
        "def": "Strategic Payroll Elasticity",
        "val": "Share of strategic training hours.",
        "form": "strategic hours / total training hours",
        "logic": ">25% (Green) / >20% (Yellow) / <20% (Red)",
    },
]

PILLARS = [
    ("Productivity (HCVA)", "HCVA (kEUR)", 145, False, 0.30),
    ("Knowledge (KTI)", "KTI (%)", 75, False, 0.20),
    ("Risk (Skill Decay)", "Skill Decay (%)", 15, True, 0.20),
    ("Resilience (RE-Score)", "RE-Score", 4.0, False, 0.15),
    ("Strategy (SPE)", "SPE (%)", 25, False, 0.15),
]

st.set_page_config(page_title="CACEIS Human Capital Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    f"""
    <style>
    .main h1 {{ color: {CACEIS_STEEL_BLUE}; }}
    div[data-testid="stSidebarNav"] {{ background-color: #f8f9fa; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ height: 50px; font-weight: bold; font-size: 16px; }}
    .stTabs [aria-selected="true"] {{ color: {CACEIS_RED} !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_dashboard_frames() -> dict[str, pd.DataFrame]:
    yearly = pd.read_csv(OUTPUT_DIR / "kpi_yearly.csv")
    by_entity = pd.read_csv(OUTPUT_DIR / "kpi_by_entity.csv")

    if "year" in yearly.columns:
        yearly["year"] = pd.to_numeric(yearly["year"], errors="coerce").astype("Int64")
        yearly = yearly[yearly["year"].isin(REPORTING_YEARS)].copy()
    if "year" in by_entity.columns:
        by_entity["year"] = pd.to_numeric(by_entity["year"], errors="coerce").astype("Int64")
        by_entity = by_entity[by_entity["year"].isin(REPORTING_YEARS)].copy()

    def extract_metric(frame: pd.DataFrame, kpi_name: str, value_col: str, keys: list[str], out_col: str) -> pd.DataFrame:
        cols = keys + [value_col]
        metric = frame[frame["KPI"] == kpi_name][cols].copy()
        metric = metric.rename(columns={value_col: out_col})
        return metric.drop_duplicates(keys)

    overall = yearly[["year"]].dropna().drop_duplicates().sort_values("year")
    overall["Legal Entity"] = "CACEIS Average"
    overall = overall.merge(extract_metric(yearly, "HCVA", "HCVA", ["year"], "HCVA (kEUR)"), on="year", how="left")
    overall = overall.merge(extract_metric(yearly, "KTI", "KTI", ["year"], "KTI raw"), on="year", how="left")
    overall = overall.merge(extract_metric(yearly, "Skill Decay", "pct_decay", ["year"], "Skill Decay raw"), on="year", how="left")
    overall = overall.merge(extract_metric(yearly, "RE-Score", "RE_score", ["year"], "RE-Score"), on="year", how="left")
    overall = overall.merge(extract_metric(yearly, "SPE Strategic Share", "strategic_share", ["year"], "SPE raw"), on="year", how="left")

    entity_base = by_entity[["year", "entity"]].dropna(subset=["year", "entity"]).drop_duplicates()
    entity_base = entity_base[~entity_base["entity"].astype(str).str.startswith("Toutes", na=False)].copy()
    entity_base = entity_base.rename(columns={"entity": "Legal Entity"})
    entity_base = entity_base.merge(extract_metric(by_entity, "KTI", "KTI", ["year", "entity"], "KTI raw"), left_on=["year", "Legal Entity"], right_on=["year", "entity"], how="left").drop(columns=["entity"])
    entity_base = entity_base.merge(extract_metric(by_entity, "Skill Decay", "pct_decay", ["year", "entity"], "Skill Decay raw"), left_on=["year", "Legal Entity"], right_on=["year", "entity"], how="left").drop(columns=["entity"])
    entity_base = entity_base.merge(extract_metric(by_entity, "RE-Score", "RE_score", ["year", "entity"], "RE-Score"), left_on=["year", "Legal Entity"], right_on=["year", "entity"], how="left").drop(columns=["entity"])
    entity_base = entity_base.merge(extract_metric(by_entity, "SPE Strategic Share", "strategic_share", ["year", "entity"], "SPE raw"), left_on=["year", "Legal Entity"], right_on=["year", "entity"], how="left").drop(columns=["entity"])
    entity_base = entity_base.merge(extract_metric(yearly, "HCVA", "HCVA", ["year"], "HCVA (kEUR)"), on="year", how="left")

    dashboard = pd.concat([overall, entity_base], ignore_index=True, sort=False)
    dashboard["KTI (%)"] = dashboard["KTI raw"] * 100.0
    dashboard["Skill Decay (%)"] = dashboard["Skill Decay raw"] * 100.0
    dashboard["SPE (%)"] = dashboard["SPE raw"] * 100.0
    dashboard = dashboard.drop(columns=["KTI raw", "Skill Decay raw", "SPE raw"])
    dashboard["CHHI Index"] = dashboard.apply(
        lambda row: compute_chhi(
            {
                "HCVA (kEUR)": row.get("HCVA (kEUR)"),
                "KTI (%)": row.get("KTI (%)"),
                "Skill Decay (%)": row.get("Skill Decay (%)"),
                "RE-Score": row.get("RE-Score"),
                "SPE (%)": row.get("SPE (%)"),
            }
        ),
        axis=1,
    )

    breakdown = yearly[["year", "KPI", "engagement_score", "absence_rate", "total_absence_days", "nb_employees"]].copy()
    return {"dashboard": dashboard, "yearly": yearly, "by_entity": by_entity, "breakdown": breakdown}


def achievement(value: float, target: float, reverse: bool, cap: float | None = None) -> float:
    if pd.isna(value):
        return np.nan
    if reverse:
        if value <= 0:
            score = 1.5
        else:
            score = target / value
    else:
        score = value / target
    if cap is not None:
        score = min(score, cap)
    return float(score)


def compute_chhi(values: dict[str, float]) -> float:
    weights = []
    scores = []
    for _, col, target, reverse, weight in PILLARS:
        pillar_score = achievement(values.get(col), target, reverse, cap=1.0)
        if not pd.isna(pillar_score):
            weights.append(weight)
            scores.append(pillar_score * weight)
    if not weights:
        return np.nan
    return 100.0 * sum(scores) / sum(weights)


def summarize(df_subset: pd.DataFrame) -> dict[str, float]:
    values = {
        "HCVA (kEUR)": df_subset["HCVA (kEUR)"].mean(),
        "KTI (%)": df_subset["KTI (%)"].mean(),
        "Skill Decay (%)": df_subset["Skill Decay (%)"].mean(),
        "RE-Score": df_subset["RE-Score"].mean(),
        "SPE (%)": df_subset["SPE (%)"].mean(),
    }
    values["CHHI Index"] = compute_chhi(values)
    return values


def get_trend_ui(curr: float, prev: float, is_reverse: bool = False) -> str:
    if pd.isna(curr) or pd.isna(prev):
        return ""
    if curr > prev:
        color = "#28a745" if not is_reverse else CACEIS_RED
        return f'<span style="color:{color}; font-size:22px;">▲</span>'
    if curr < prev:
        color = CACEIS_RED if not is_reverse else "#28a745"
        return f'<span style="color:{color}; font-size:22px;">▼</span>'
    return '<span style="color:gray; font-size:22px;">=</span>'


def get_bg_color(value: float, target: float, is_reverse: bool = False, is_master: bool = False) -> str:
    if pd.isna(value):
        return NEUTRAL_BG
    alpha = "0.35" if is_master else "0.15"
    if is_reverse:
        if value < target * 0.8:
            return f"rgba(40, 167, 69, {alpha})"
        if value < target * 1.2:
            return f"rgba(255, 193, 7, {alpha})"
        return f"rgba(214, 80, 99, {alpha})"
    if value > target:
        return f"rgba(40, 167, 69, {alpha})"
    if value > target * 0.8:
        return f"rgba(255, 193, 7, {alpha})"
    return f"rgba(214, 80, 99, {alpha})"


def format_metric(value: float, unit: str) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.1f}{unit}"


frames = load_dashboard_frames()
dashboard_df = frames["dashboard"]
yearly_df = frames["yearly"]

logo_path = "CACEIS_Investor_Services_logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)
else:
    st.sidebar.title("WE ARE ONE CACEIS")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Go to:", ["Live Dashboard", "Interpretation Guide", "2023 RBC Integration"])

if app_mode == "Live Dashboard":
    st.title("Human Capital Dashboard (KPIs)")

    st.sidebar.markdown("---")
    years = sorted(dashboard_df["year"].dropna().astype(int).unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("Analysis Year", years)
    entity_options = sorted([e for e in dashboard_df["Legal Entity"].dropna().unique().tolist() if e != "CACEIS Average"])
    selected_entities = st.sidebar.multiselect("Legal entity Scope", options=["Select All"] + entity_options, default=["Select All"])

    if "Select All" in selected_entities or not selected_entities:
        df_current = dashboard_df[(dashboard_df["year"] == selected_year) & (dashboard_df["Legal Entity"] == "CACEIS Average")]
        df_prev = dashboard_df[(dashboard_df["year"] == selected_year - 1) & (dashboard_df["Legal Entity"] == "CACEIS Average")]
        plot_entities = ["CACEIS Average"]
    else:
        df_current = dashboard_df[(dashboard_df["year"] == selected_year) & (dashboard_df["Legal Entity"].isin(selected_entities))]
        df_prev = dashboard_df[(dashboard_df["year"] == selected_year - 1) & (dashboard_df["Legal Entity"].isin(selected_entities))]
        plot_entities = selected_entities + ["CACEIS Average"]

    current_values = summarize(df_current)
    previous_values = summarize(df_prev) if not df_prev.empty else {}

    if df_current.empty:
        st.warning("No KPI data available for this scope.")
        st.stop()

    if pd.isna(current_values["RE-Score"]):
        st.info("RE-Score is missing for this scope because no absence data is available for the selected year in the source export.")

    st.markdown("---")
    tabs = st.tabs([k["label"] for k in KPI_CONFIG])

    for i, tab in enumerate(tabs):
        conf = KPI_CONFIG[i]
        with tab:
            st.markdown("<br>", unsafe_allow_html=True)
            col_val, col_graph, col_txt = st.columns([1, 2, 1.2])
            val = current_values.get(conf["col"], np.nan)
            prev_val = previous_values.get(conf["col"], np.nan)
            bg = get_bg_color(val, conf["target"], conf["rev"], conf["is_master"])
            trend = get_trend_ui(val, prev_val, conf["rev"])

            with col_val:
                border = f"3px solid {CACEIS_STEEL_BLUE}" if conf["is_master"] else "1px solid #ddd"
                st.markdown(
                    f"""
                    <div style="background-color: {bg}; padding: 30px 15px; border-radius: 12px; border: {border}; text-align: center; min-height: 220px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <p style="font-size: 14px; margin-bottom: 10px; color: black; font-weight: bold; text-transform: uppercase;">{conf['label']}</p>
                        <h2 style="margin: 15px 0; color: black; font-size: 42px;">{format_metric(val, conf['unit'])}</h2>
                        <div style="margin-top: 20px;">{trend}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption("Green: target reached | Yellow: watch | Red: critical")

            with col_graph:
                df_plot = dashboard_df[dashboard_df["Legal Entity"].isin(plot_entities)].copy()
                fig = px.line(
                    df_plot,
                    x="year",
                    y=conf["col"],
                    color="Legal Entity",
                    markers=True,
                    color_discrete_sequence=[CACEIS_STEEL_BLUE, CACEIS_RED, CACEIS_GREY, CACEIS_GREY_BLUE],
                )
                fig.update_xaxes(dtick=1)
                fig.update_traces(
                    patch={"line": {"color": "black", "width": 3, "dash": "dash"}},
                    selector={"name": "CACEIS Average"},
                )
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20), template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            with col_txt:
                st.markdown(
                    f"""
                    <div style="padding: 10px; border-radius: 10px; background-color: #f9f9f9; border: 1px solid #eee; height: 100%;">
                        <p><strong>Name:</strong> {conf['def']}</p>
                        <p><strong>Business Value:</strong> {conf['val']}</p>
                        <p><strong>Formula:</strong> <code>{conf['form']}</code></p>
                        <hr style="margin: 10px 0;">
                        <p style="font-size: 12px;"><strong>Target Logic:</strong><br>{conf['logic']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.subheader("Global Human Capital Score: Radar and Pillar Breakdown")
    col_radar, col_table = st.columns([2, 1.2])

    with col_radar:
        categories = [pillar[0] for pillar in PILLARS]
        r_values = [achievement(current_values.get(col), target, reverse, cap=1.5) for _, col, target, reverse, _ in PILLARS]
        r_values = [0 if pd.isna(v) else v for v in r_values]
        fig_radar = go.Figure()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=[1.0] * len(categories) + [1.0],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(136, 139, 141, 0.05)",
                line=dict(color=CACEIS_RED, dash="dash"),
                name="Target Threshold",
            )
        )
        fig_radar.add_trace(
            go.Scatterpolar(
                r=r_values + [r_values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(136, 139, 141, 0.4)",
                line=dict(color=CACEIS_GREY, width=3),
                name="Actual Performance",
            )
        )
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1.5])),
            showlegend=True,
            height=450,
            margin=dict(t=20, b=20),
            template="plotly_white",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_table:
        breakdown_df = pd.DataFrame(
            {
                "Pillar": categories,
                "Target Achievement": [f"{value * 100:.1f}%" if not pd.isna(value) else "n/a" for value in r_values],
                "Weighting": [f"{int(weight * 100)}%" for *_, weight in PILLARS],
                "Impact": ["OK" if value >= 1.0 else "Watch" for value in r_values],
            }
        )
        breakdown_df.index = [f"KPI {i + 1}" for i in range(len(breakdown_df))]
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("**CHHI contribution details**")
        st.table(breakdown_df)
        st.info("Missing source data removes the pillar from the CHHI weighting for the selected scope.")

elif app_mode == "Interpretation Guide":
    st.title("Interpretation Guide")
    st.markdown(
        """
        ### Strategic Interpretation

        | Level | Status and Action |
        | :--- | :--- |
        | <h5 style="color:#28a745; margin:0;">Target Achieved</h5> | <ul><li><strong>Status:</strong> Asset appreciation.</li><li><strong>Action:</strong> Maintain investments and share best practices.</li></ul> |
        | <h5 style="color:#ffc107; margin:0;">Warning</h5> | <ul><li><strong>Status:</strong> Early signs of weakness.</li><li><strong>Action:</strong> Run a focused deep dive on the declining pillar.</li></ul> |
        | <h5 style="color:#D65063; margin:0;">Critical</h5> | <ul><li><strong>Status:</strong> Operational or capability risk.</li><li><strong>Action:</strong> Immediate intervention required.</li></ul> |

        ### Trend Analysis
        * Performance KPIs: Green if increasing, red if decreasing.
        * Risk KPI (Skill Decay): Green if decreasing, red if increasing.

        ### Data Definitions
        * Skill Decay is measured at 31/12 of each year with a 12-month inactivity threshold.
        * RE-Score is normalized on a /5 scale to stay comparable with dashboard targets.
        * CHHI is computed only from available pillars and rebalances missing KPI weights.
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("Data Governance: GDPR compliant | WE ARE ONE CACEIS")

else:
    st.title("2023 RBC Integration")
    st.warning(
        """
        Contextual note on data quality: 2023 figures may be impacted by the integration of RBC Investor Services' European activities.
        """
    )
    st.markdown(
        """
        ### Resilience and Engagement Score (RE-Score)
        Historical interpretation must remain cautious when source systems are incomplete or partially remapped.
        The dashboard now reads KPI exports directly from the notebook pipeline, but missing absence data still propagates to missing RE-Score values.
        """
    )
