import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os 

# --- 1. CONFIGURATION GLOBALE & CHARTE CACEIS ---
st.set_page_config(
    page_title="CACEIS Human Capital Analytics", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Codes couleurs officiels basés sur le logo et la charte
CACEIS_RED = "#D65063"
CACEIS_GREY = "#888B8D"
CACEIS_GREY_BLUE = "#5C768D"
CACEIS_STEEL_BLUE = "#4A6E8C"

st.markdown(f"""
    <style>
    .main h1 {{ color: {CACEIS_STEEL_BLUE}; }}
    div[data-testid="stSidebarNav"] {{ background-color: #f8f9fa; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ height: 50px; font-weight: bold; font-size: 16px; }}
    .stTabs [aria-selected="true"] {{ color: {CACEIS_RED} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTEUR DE DONNÉES ---
@st.cache_data
def load_data():
    file_path = "dashboard_kpi_hr.csv" 
    
    if os.path.exists(file_path):
        # On ajoute sep=";" car le fichier utilise des points-virgules
        df_raw = pd.read_csv(file_path, sep=";")

        # Nettoyage des noms de colonnes pour enlever espaces ou caractères invisibles
        df_raw.columns = df_raw.columns.str.strip()
        
        # Renommage explicite
        df_final = df_raw.rename(columns={
            "year": "Year",
            "hcva": "HCVA (k€)",
            "kti_potentiel": "KTI (%)",
            "re_score": "RE-Score",
            "chhi_index_100": "CHHI Index",
            "lsr": "LSR",
            "lsr_mixite": "LSR Mixity",
            "lsr_inclusion": "LSR Inclusion",
            "lsr_engagement": "LSR Engagement"
        })
        
        # Conversion KTI en % (seulement si la colonne existe après le rename)
        if "KTI (%)" in df_final.columns:
            # On s'assure que les données sont numériques (au cas où le CSV soit mal lu)
            df_final["KTI (%)"] = pd.to_numeric(df_final["KTI (%)"], errors='coerce')
            
            # On multiplie par 100 si c'est un ratio (ex: 0.82)
            if df_final["KTI (%)"].max() <= 1.5: # On prend une marge
                df_final["KTI (%)"] = df_final["KTI (%)"] * 100

        # LSR is computed in LSR_KPI.ipynb for 2024 only.
        # If the central CSV has not been enriched yet, Streamlit still displays the validated KPI.
        lsr_metrics, _ = compute_lsr_metrics()
        lsr_columns = {
            "LSR": lsr_metrics["LSR"],
            "LSR Mixity": lsr_metrics["Mixity"],
            "LSR Inclusion": lsr_metrics["Inclusion"],
            "LSR Engagement": lsr_metrics["Engagement"],
        }
        for col, value in lsr_columns.items():
            if col not in df_final.columns:
                df_final[col] = np.where(df_final["Year"].astype(int).eq(2024), value, 0.0)
        
        return df_final.round(2)
    else:
        st.error(f"Fichier '{file_path}' non trouvé.")
        return pd.DataFrame()

# --- 3. FONCTIONS D'AIDE ---
def get_trend_ui(curr, prev, is_reverse=False, has_prev=True):
    if not has_prev: return ""
    if curr > prev:
        color = "#28a745" if not is_reverse else CACEIS_RED
        return f'<span style="color:{color}; font-size:22px;">▲</span>'
    elif curr < prev:
        color = CACEIS_RED if not is_reverse else "#28a745"
        return f'<span style="color:{color}; font-size:22px;">▼</span>'
    return '<span style="color:gray; font-size:22px;">▬</span>'

def get_bg_color(value, target, is_reverse=False, is_master=False):
    alpha = "0.35" if is_master else "0.15"
    if is_reverse:
        if value < target * 0.8: return f"rgba(40, 167, 69, {alpha})"
        if value < target * 1.2: return f"rgba(255, 193, 7, {alpha})"
        return f"rgba(214, 80, 99, {alpha})"
    else:
        if value > target: return f"rgba(40, 167, 69, {alpha})"
        if value > target * 0.8: return f"rgba(255, 193, 7, {alpha})"
        return f"rgba(214, 80, 99, {alpha})"

@st.cache_data
def compute_lsr_metrics():
    sab_moyen_femmes_fr = 54_753
    sab_moyen_hommes_fr = 60_360
    cadres_encadrants_2024 = {
        "H": (0, 2),
        "I": (10, 25),
        "J": (21, 20),
        "K": (25, 33),
        "HC": (41, 67),
    }
    barometre_fr_pct = 70.0
    barometre_lux_pct = 64.0
    effectif_fr = 2_043
    effectif_lux = 1_882
    fab_life_participations_caceis = 2_984 - 743
    we_care_participations_chiffrees = 1_256
    we_care_lignes_na = 14
    we_care_fallback_par_na = 24
    be_generous_laureats_caceis = 34

    gap_pct = (sab_moyen_hommes_fr - sab_moyen_femmes_fr) / sab_moyen_hommes_fr * 100
    score_paygap = max(0, 100 - abs(gap_pct) * 5)

    total_f_encadrants = sum(f for f, h in cadres_encadrants_2024.values())
    total_h_encadrants = sum(h for f, h in cadres_encadrants_2024.values())
    total_encadrants = total_f_encadrants + total_h_encadrants
    pct_femmes_mgt = total_f_encadrants / total_encadrants * 100
    score_mgt = min(100, pct_femmes_mgt / 40 * 100)
    score_mixity = (score_paygap + score_mgt) / 2

    score_inclusion = (
        barometre_fr_pct * effectif_fr +
        barometre_lux_pct * effectif_lux
    ) / (effectif_fr + effectif_lux)

    we_care_total = we_care_participations_chiffrees + we_care_lignes_na * we_care_fallback_par_na
    total_participations = (
        fab_life_participations_caceis +
        we_care_total +
        be_generous_laureats_caceis
    )
    effectif_total = effectif_fr + effectif_lux
    intensity = total_participations / effectif_total
    score_engagement = min(100, intensity * 50)
    lsr = (score_mixity + score_inclusion + score_engagement) / 3

    sensitivity = []
    for fallback in (0, 12, 24, 36, 48):
        we_care_var = we_care_participations_chiffrees + we_care_lignes_na * fallback
        total_var = fab_life_participations_caceis + we_care_var + be_generous_laureats_caceis
        score_eng_var = min(100, (total_var / effectif_total) * 50)
        lsr_var = (score_mixity + score_inclusion + score_eng_var) / 3
        sensitivity.append({
            "Fallback participants": fallback,
            "We Care total": we_care_var,
            "Engagement": round(score_eng_var, 1),
            "LSR": round(lsr_var, 1),
        })

    metrics = {
        "Year": 2024,
        "LSR": round(lsr, 2),
        "Mixity": round(score_mixity, 2),
        "Inclusion": round(score_inclusion, 2),
        "Engagement": round(score_engagement, 2),
        "Pay gap": round(gap_pct, 2),
        "Women managers": round(pct_femmes_mgt, 2),
        "Engagement intensity": round(intensity, 3),
        "Headcount": effectif_total,
    }
    return metrics, pd.DataFrame(sensitivity)

@st.cache_data
def load_ml_workbook(file_path):
    return {
        "model_selection": pd.read_excel(file_path, sheet_name="model_selection"),
        "clustered_dataset": pd.read_excel(file_path, sheet_name="clustered_dataset"),
        "cluster_summary": pd.read_excel(file_path, sheet_name="cluster_summary"),
        "cluster_interpretation": pd.read_excel(file_path, sheet_name="cluster_interpretation"),
        "entity_cluster_summary": pd.read_excel(file_path, sheet_name="entity_cluster_summary"),
        "year_cluster_summary": pd.read_excel(file_path, sheet_name="year_cluster_summary"),
        "pca_projection": pd.read_excel(file_path, sheet_name="pca_projection"),
    }

@st.cache_data
def load_ml_dataset(file_path):
    return pd.read_csv(file_path)

# Chargement
df = load_data()

# --- 4. NAVIGATION & LOGO ---
logo_path = "CACEIS_Investor_Services_logo.png" 
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)
else:
    st.sidebar.title("WE ARE ONE CACEIS")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Go to:", ["Live Dashboard", "LSR Governance KPI", "Machine Learning", "Interpretation Guide", "2023 RBC Integration"])

# --- 5. PAGE 1 : LIVE DASHBOARD ---
if app_mode == "Live Dashboard":
    st.title("🔝 Human Capital Dashboard (KPIs)")
    
    st.sidebar.markdown("---")
    selected_year = st.sidebar.selectbox("Analysis Year", sorted(df['Year'].unique(), reverse=True))
   
    df_current = df[df['Year'] == selected_year]
    has_previous = selected_year > min(df['Year'])
    if has_previous:
        df_prev = df[df['Year'] == selected_year - 1]

    kpis_config = [
        {"id": "CHHI", "label": "Global Human Capital Score (CHHI)", "col": "CHHI Index", "unit": "%", "target": 80, "rev": False, "is_master": True, "def": "CACEIS Human Capital Health Index (CHHI)", "val": "Global Human Capital Score.", "form": "Weighted average of all other KPIs.", "logic": ">80% (Green) / >64% (Yellow) / <64% (Red)"},
        {"id": "HCVA", "label": "KPI 1: Productivity (HCVA)", "col": "HCVA (k€)", "unit": "k€", "target": 200, "rev": False, "is_master": False, "def": "Human Capital Value Added (HCVA) per FTE", "val": "Financial efficiency of human capital.", "form": "[GNP - (OpEx-Payroll)]/FTE", "logic": ">200k€ (Green) / >160k€ (Yellow) / <160k€ (Red)"},
        {"id": "KTI", "label": "KPI 2: Knowledge (KTI)", "col": "KTI (%)", "unit": "%", "target": 75, "rev": False, "is_master": False, "def": "Knowledge Transfer Index (KTI)", "val": "Training ROI and skill application.", "form": " Σ(Activation Scores) / Nb Responses", "logic": ">75% (Green) / >60% (Yellow) / <60% (Red)"},
        #{"id": "SD", "label": "KPI 3: Risk (Skill Decay)", "col": "Skill Decay (%)", "unit": "%", "target": 15, "rev": True, "is_master": False, "def": "Skill Decay Rate (Obsolescence Index)", "val": "Risk of expertise erosion.", "form": "% without training > 18 months", "logic": "<12% (Green) / <18% (Yellow) / >18% (Red)"},
        {"id": "RE", "label": "KPI 3: Resilience (RE-Score)", "col": "RE-Score", "unit": "/5", "target": 4.0, "rev": False, "is_master": False, "def": "Resilience & Engagement Score (RE-Score)", "val": "Workforce stability and morale.", "form": "Engagement / Absenteeism", "logic": ">4.0 (Green) / >3.2 (Yellow) / <3.2 (Red)"},
        {"id": "LSR", "label": "KPI 4: Governance (LSR)", "col": "LSR", "unit": "%", "target": 75, "rev": False, "is_master": False, "def": "License-to-Operate & Sustainability Resilience", "val": "Social resilience against regulatory, human and reputational risks.", "form": "(Mixity + Inclusion + Engagement) / 3", "logic": ">75% (Green) / >60% (Yellow) / <60% (Red)"},
        #{"id": "SPE", "label": "KPI 5: Strategy (SPE)", "col": "SPE (%)", "unit": "%", "target": 25, "rev": False, "is_master": False, "def": "Strategic Payroll Elasticity (SPE)", "val": "Agility towards future-proof jobs.", "form": "% payroll growth roles", "logic": ">25% (Green) / >20% (Yellow) / <20% (Red)"}
    ]

    st.markdown("---")
    tabs = st.tabs([k["label"] for k in kpis_config])

    for i, tab in enumerate(tabs):
        conf = kpis_config[i]
        with tab:
            st.markdown("<br>", unsafe_allow_html=True)
            col_val, col_graph, col_txt = st.columns([1, 2, 1.2])
            val = df_current[conf["col"]].mean()
            bg = get_bg_color(val, conf["target"], conf["rev"], conf["is_master"])
            trend = ""
            if has_previous:
                trend = get_trend_ui(val, df_prev[conf["col"]].mean(), conf["rev"])

            with col_val:
                border = f"3px solid {CACEIS_STEEL_BLUE}" if conf["is_master"] else "1px solid #ddd"
                st.markdown(f"""
                    <div style="background-color: {bg}; padding: 30px 15px; border-radius: 12px; border: {border}; text-align: center; min-height: 220px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <p style="font-size: 14px; margin-bottom: 10px; color: black; font-weight: bold; text-transform: uppercase;">{conf['label']}</p>
                        <h2 style="margin: 15px 0; color: black; font-size: 42px;">{val:.1f}{conf['unit']}</h2>
                        <div style="margin-top: 20px;">{trend}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                    <div style="padding: 15px 5px; font-size: 13px; line-height: 1.8;">
                        🟢 Target Achieved <br>
                        🟡 Warning<br>
                        🔴 Critical
                    </div>
                """, unsafe_allow_html=True)

            with col_graph:
                # Création du graphique linéaire simple sur l'historique complet (df)
                fig = px.line(
                    df, 
                    x="Year", 
                    y=conf['col'], 
                    markers=True,
                    color_discrete_sequence=[CACEIS_STEEL_BLUE] # Utilisation de la couleur principale
                )
                
                # Restauration de l'épaisseur d'origine (1px) et ajustement des marqueurs
                fig.update_traces(
                    line=dict(width=1), # Ligne fine originale
                    marker=dict(size=6)   # Marqueurs standards
                )
                
                # Ajustements esthétiques d'origine
                fig.update_xaxes(dtick=1)
                fig.update_layout(
                    height=300, 
                    margin=dict(l=20, r=20, t=30, b=20), 
                    template="plotly_white",
                    showlegend=False # Pas besoin de légende pour une seule ligne
                )
                
                st.plotly_chart(fig, use_container_width=True)

            with col_txt:
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 10px; background-color: #f9f9f9; border: 1px solid #eee; height: 100%;">
                    <p><strong>Name:</strong> {conf['def']}</p>
                    <p><strong>Business Value:</strong> {conf['val']}</p>
                    <p><strong>Formula:</strong> <code>{conf['form']}</code></p>
                    <hr style="margin: 10px 0;">
                    <p style="font-size: 12px;"><strong>Target Logic:</strong><br>{conf['logic']}</p>
                </div>""", unsafe_allow_html=True)
                if conf["id"] == "LSR" and selected_year != 2024:
                    st.warning("LSR is currently calculated only for 2024, based on available governance sources.")

    st.markdown("---")
    st.subheader("Global Human Capital Score: Radar & Pillar Breakdown")
    col_radar, col_table = st.columns([2, 1.2])

    with col_radar:
        categories = ['Productivity (HCVA)', 'Knowledge (KTI)', 'Resilience (RE-Score)']
        #categories = ['Productivity (HCVA)', 'Knowledge (KTI)', 'Risk (Skill Decay)', 'Resilience (RE-Score)', 'Strategy (SPE)']
        r_values = [
            df_current['hcva_radar'].values[0],
            df_current['kti_radar'].values[0],
            df_current['re_radar'].values[0]
        ]

        fig_radar = go.Figure()
        # Ligne de cible (Target) fixe à 100%
        fig_radar.add_trace(go.Scatterpolar(r=[100, 100, 100, 100], theta=categories + [categories[0]], fill='toself', fillcolor='rgba(136, 139, 141, 0.05)', line=dict(color=CACEIS_RED, dash='dash'), name='Target Threshold (100%)'))
        # Performance Réelle (peut dépasser 100)
        fig_radar.add_trace(go.Scatterpolar(r=r_values + [r_values[0]], theta=categories + [categories[0]], fill='toself', fillcolor='rgba(136, 139, 141, 0.4)', line=dict(color=CACEIS_GREY, width=3), name='Actual Performance'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 160], tickvals=[0, 50, 100, 150], ticktext=['0%', '50%', 'TARGET', '150%'], tickfont=dict(size=10))), showlegend=True, height=500, margin=dict(t=20, b=20), template="plotly_white")
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_table:
        st.markdown("""
            <style>
                /* Optimisation de la largeur des colonnes pour 3 KPIs */
                [data-testid="stTable"] td:first-child {
                    white-space: nowrap !important;
                    min-width: 60px !important;
                }
                [data-testid="stTable"] td:nth-child(2) {
                    min-width: 160px !important;
                }
                [data-testid="stTable"] th:last-child, 
                [data-testid="stTable"] td:last-child {
                    white-space: nowrap !important;
                    min-width: 100px !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Logique d'impact dynamique (r_values étant déjà sur 100)
        impacts = []
        for v in r_values:
            if v >= 130: impacts.append("🚀 Exceptional")
            elif v >= 100: impacts.append("✅ Achieved")
            elif v >= 80: impacts.append("⚠️ Warning")
            else: impacts.append("🚨 Critical")

        # Construction du DataFrame avec les 3 piliers
        breakdown_df = pd.DataFrame({
            "Pillar": categories, 
            "Achievement": [f"{v:.1f}%" for v in r_values], 
            "Weighting": ["40%", "30%", "30%"], 
            "Status": impacts
        })
        
        # Indexation KPI 1 à 3
        breakdown_df.index = [f"KPI {i+1}" for i in range(len(breakdown_df))]
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("**CHHI (Weighted average of 3 KPIs) Contribution Details**")     
        
        st.table(breakdown_df)
        
        # Note explicative mise à jour
        st.info("""
            **Guide:** **Achievement > 100%**: Objective surpassed (exceeds the dashed line on the radar).  
            * **Status ⚠️ or 🚨**: Indicator performing below strategic target.
        """)


# --- 6. PAGE 2 : LSR GOVERNANCE KPI ---
elif app_mode == "LSR Governance KPI":
    st.title("LSR Governance KPI")
    st.markdown("""
    **LSR** stands for **License-to-Operate & Sustainability Resilience**.
    It is a governance KPI that measures CACEIS' social resilience against
    regulatory, human and reputational risks.

    The KPI is calculated for **2024**, using official governance and HR sources.
    """)

    lsr_metrics, lsr_sensitivity = compute_lsr_metrics()

    score = lsr_metrics["LSR"]
    if score >= 75:
        zone = "Green zone"
        zone_color = "#28a745"
        zone_comment = "Strong social resilience."
    elif score >= 60:
        zone = "Yellow zone"
        zone_color = "#ffc107"
        zone_comment = "Acceptable but requires monitoring and targeted action."
    else:
        zone = "Red zone"
        zone_color = CACEIS_RED
        zone_comment = "Social resilience risk requiring immediate action."

    top_cols = st.columns([1, 1, 1, 1])
    top_cols[0].metric("LSR 2024", f"{score:.1f}/100")
    top_cols[1].metric("Mixity", f"{lsr_metrics['Mixity']:.1f}/100")
    top_cols[2].metric("Inclusion", f"{lsr_metrics['Inclusion']:.1f}/100")
    top_cols[3].metric("Engagement", f"{lsr_metrics['Engagement']:.1f}/100")

    st.markdown(f"""
    <div style="border-left:6px solid {zone_color}; background-color:#f9f9f9; padding:16px; border-radius:8px; margin:12px 0 22px 0;">
        <h4 style="margin:0; color:{CACEIS_STEEL_BLUE};">Board reading: {zone}</h4>
        <p style="margin:8px 0 0 0;">{zone_comment}</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("How the KPI is calculated")
    st.markdown("""
    The LSR score is the average of three dimensions:

    ```
    LSR = (Mixity + Inclusion + Engagement) / 3
    ```
    """)

    components = pd.DataFrame({
        "Component": ["Mixity", "Inclusion", "Engagement", "LSR"],
        "Score": [
            lsr_metrics["Mixity"],
            lsr_metrics["Inclusion"],
            lsr_metrics["Engagement"],
            lsr_metrics["LSR"],
        ],
        "Business meaning": [
            "Gender equity: pay gap and women in management",
            "Feeling of inclusion from France and Luxembourg D&I barometers",
            "Participation intensity in social programmes",
            "Overall governance and social resilience score",
        ],
    })

    col_chart, col_table = st.columns([1.2, 1])
    with col_chart:
        fig_lsr = px.bar(
            components,
            x="Component",
            y="Score",
            text="Score",
            color="Component",
            color_discrete_sequence=[CACEIS_GREY_BLUE, CACEIS_STEEL_BLUE, "#E0A526", CACEIS_RED],
        )
        fig_lsr.add_hline(y=75, line_dash="dash", line_color="#28a745", annotation_text="Green target: 75")
        fig_lsr.add_hline(y=60, line_dash="dash", line_color="#E0A526", annotation_text="Yellow threshold: 60")
        fig_lsr.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_lsr.update_layout(
            template="plotly_white",
            height=430,
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis_title="Score (/100)",
            showlegend=False,
        )
        fig_lsr.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_lsr, use_container_width=True)

    with col_table:
        st.dataframe(components, use_container_width=True, hide_index=True)
        st.markdown("""
        **Simple interpretation**

        Mixity is close to target, inclusion is acceptable, but engagement is the main weakness.
        The final LSR score is therefore in the yellow zone.
        """)

    st.subheader("Key drivers")
    driver_cols = st.columns(3)
    driver_cols[0].metric("Pay gap", f"{lsr_metrics['Pay gap']:.1f}%")
    driver_cols[1].metric("Women managers", f"{lsr_metrics['Women managers']:.1f}%")
    driver_cols[2].metric("Engagement intensity", f"{lsr_metrics['Engagement intensity']:.2f} participation / employee")

    st.subheader("Sensitivity check")
    st.markdown("""
    The only explicit assumption is the fallback used for We Care rows marked as `n/a`.
    The sensitivity test shows that the final conclusion remains stable.
    """)
    fig_sensitivity = px.line(
        lsr_sensitivity,
        x="Fallback participants",
        y="LSR",
        markers=True,
        color_discrete_sequence=[CACEIS_STEEL_BLUE],
    )
    fig_sensitivity.add_hrect(y0=60, y1=75, fillcolor="#E0A526", opacity=0.12, line_width=0)
    fig_sensitivity.add_hrect(y0=75, y1=100, fillcolor="#28a745", opacity=0.10, line_width=0)
    fig_sensitivity.add_vline(x=24, line_dash="dash", line_color=CACEIS_RED, annotation_text="Retained fallback")
    fig_sensitivity.update_layout(
        template="plotly_white",
        height=360,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis_title="LSR score (/100)",
    )
    fig_sensitivity.update_yaxes(range=[55, 75])
    st.plotly_chart(fig_sensitivity, use_container_width=True)

    st.caption("Source notebook: LSR_KPI.ipynb. The KPI is displayed without requiring private source documents in GitHub.")


# --- 7. PAGE 3 : MACHINE LEARNING ---
elif app_mode == "Machine Learning":
    st.title("Machine Learning: Monthly HR Segmentation")

    st.markdown("""
    This page presents the unsupervised Machine Learning analysis built on the monthly HR panel.
    The model does not predict an official target and therefore does not produce an accuracy score.
    It uses KMeans clustering to segment monthly entity situations into business profiles.
    """)

    st.info("""
    The ML datasets are confidential and are not stored in GitHub. To use this tab after cloning the repository,
    place the files on your computer and provide their local paths below.
    """)

    st.sidebar.markdown("---")
    st.sidebar.subheader("ML local files")
    ml_results_path = st.sidebar.text_input(
        "ML results Excel path",
        value="outputs/ml_monthly_model_results.xlsx",
        help="Local path to the Excel file generated by ml_notebook.ipynb."
    )
    ml_dataset_path = st.sidebar.text_input(
        "ML-ready CSV path (optional)",
        value="outputs/monthly_entity_panel_ml_ready.csv",
        help="Optional local path to the ML-ready monthly dataset."
    )

    if not os.path.exists(ml_results_path):
        st.warning(f"ML results file not found: `{ml_results_path}`")
        st.markdown("""
        Expected file:
        ```
        outputs/ml_monthly_model_results.xlsx
        ```

        This file is generated by:
        ```
        ml_notebook.ipynb
        ```

        The notebook uses the local confidential dataset:
        ```
        outputs/monthly_entity_panel_ml_ready.csv
        ```

        For confidentiality reasons, these files should stay local and should not be pushed to GitHub.
        """)
    else:
        try:
            ml_results = load_ml_workbook(ml_results_path)
        except Exception as exc:
            st.error(f"Unable to load ML workbook: {exc}")
            st.stop()

        model_selection = ml_results["model_selection"]
        clustered_dataset = ml_results["clustered_dataset"]
        cluster_summary = ml_results["cluster_summary"]
        cluster_interpretation = ml_results["cluster_interpretation"]
        entity_cluster_summary = ml_results["entity_cluster_summary"]
        year_cluster_summary = ml_results["year_cluster_summary"]
        pca_projection = ml_results["pca_projection"]

        best_row = model_selection.sort_values("silhouette_score", ascending=False).iloc[0]
        best_k = int(best_row["k"])
        best_score = float(best_row["silhouette_score"])

        cluster_names = {
            0: "Healthy and dynamic",
            1: "Moderate HR pressure",
            2: "Fragile transformation profile",
            3: "Stable but low transformation",
        }
        cluster_descriptions = {
            0: "Low absenteeism, strong knowledge transfer and balanced strategic training.",
            1: "Higher absenteeism, but knowledge transfer and training indicators remain acceptable.",
            2: "Higher absenteeism, weaker knowledge transfer and stronger skill obsolescence signal.",
            3: "Low absenteeism, but weaker knowledge transfer and lower strategic training exposure.",
        }
        cluster_actions = {
            0: "Maintain current practices and use this profile as a benchmark.",
            1: "Monitor workload and absence drivers before the situation deteriorates.",
            2: "Prioritise HR attention: investigate absence causes and reinforce knowledge transfer.",
            3: "Keep operational stability, but accelerate strategic upskilling.",
        }

        cluster_summary = cluster_summary.copy()
        cluster_summary["profile"] = cluster_summary["cluster"].map(cluster_names).fillna("Cluster profile")
        clustered_dataset = clustered_dataset.copy()
        clustered_dataset["profile"] = clustered_dataset["cluster"].map(cluster_names).fillna("Cluster profile")
        pca_projection = pca_projection.copy()
        pca_projection["profile"] = pca_projection["cluster"].map(cluster_names).fillna("Cluster profile")

        metric_cols = st.columns(4)
        metric_cols[0].metric("Situations analysed", len(clustered_dataset))
        metric_cols[1].metric("Entities", clustered_dataset["entity"].nunique())
        metric_cols[2].metric("HR profiles found", best_k)
        metric_cols[3].metric("Separation quality", f"{best_score:.2f}")

        st.markdown("""
        ### What the model tells us

        The model groups monthly HR situations into **4 recurring profiles**.  
        Each point is one **entity-month**, for example *CACEIS Bank in March 2024*.

        The model compares each month using four business indicators:

        | Indicator | Meaning |
        | :--- | :--- |
        | `absence_rate` | Level of analytical absenteeism, excluding holidays and non-followed absences |
        | `KTI` | Knowledge Transfer Index: are employees reusing what they learned in training? |
        | `pct_decay` | Share of employees with potentially ageing skills |
        | `strategic_share` | Share of training hours linked to strategic topics |
        """)

        st.markdown("""
        **How to read the score.** The separation quality is moderate, not perfect.
        This is expected because HR data is real and gradual: months can look similar.
        The output should be read as **business segmentation**, not as a prediction model.
        """)

        tab_overview, tab_profiles, tab_details = st.tabs([
            "Executive View",
            "Profiles and Actions",
            "Technical Details"
        ])

        with tab_overview:
            st.subheader("Immediate Reading")
            st.markdown("""
            The clustering does not say whether an entity is good or bad overall.
            It identifies the **type of HR situation observed in each month**:
            healthy, under pressure, fragile, or stable but insufficiently transformed.
            """)

            card_cols = st.columns(4)
            for idx, cluster_id in enumerate(sorted(cluster_summary["cluster"].dropna().unique())):
                cluster_id = int(cluster_id)
                n_rows = int(cluster_summary.loc[cluster_summary["cluster"] == cluster_id, "n"].iloc[0])
                card_cols[idx % 4].markdown(f"""
                <div style="border:1px solid #ddd; border-radius:12px; padding:16px; min-height:230px; background-color:#f9f9f9;">
                    <p style="font-size:13px; color:{CACEIS_GREY}; margin-bottom:4px;">Cluster {cluster_id}</p>
                    <h4 style="color:{CACEIS_STEEL_BLUE}; margin-top:0;">{cluster_names.get(cluster_id, "Cluster profile")}</h4>
                    <p style="font-size:26px; font-weight:bold; margin:8px 0;">{n_rows} months</p>
                    <p style="font-size:13px;">{cluster_descriptions.get(cluster_id, "")}</p>
                    <p style="font-size:13px;"><strong>Business action:</strong> {cluster_actions.get(cluster_id, "")}</p>
                </div>
                """, unsafe_allow_html=True)

            st.subheader("Where are the profiles located?")
            fig_entity = px.bar(
                entity_cluster_summary,
                x="entity",
                y="n_rows",
                color=entity_cluster_summary["cluster"].astype(str),
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_entity.update_layout(
                template="plotly_white",
                height=360,
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis_title="Entity",
                yaxis_title="Number of entity-months",
                legend_title="Cluster",
            )
            st.plotly_chart(fig_entity, use_container_width=True)

            st.caption("A higher bar means that the entity spent more months in that HR profile.")

        with tab_profiles:
            st.subheader("Profile Comparison")

            display_summary = cluster_summary[[
                "cluster", "profile", "n", "absence_rate", "KTI", "pct_decay", "strategic_share"
            ]].copy()
            for col in ["absence_rate", "KTI", "pct_decay", "strategic_share"]:
                display_summary[col] = (display_summary[col] * 100).round(1).astype(str) + "%"
            display_summary = display_summary.rename(columns={
                "cluster": "Cluster",
                "profile": "Business profile",
                "n": "Number of months",
                "absence_rate": "Absenteeism",
                "KTI": "Knowledge transfer",
                "pct_decay": "Skill decay",
                "strategic_share": "Strategic training",
            })
            st.dataframe(display_summary, use_container_width=True, hide_index=True)

            st.markdown("""
            The table above should be read horizontally: each cluster is a typical monthly HR situation.
            For example, a cluster can combine low absenteeism with weak strategic training, which means
            the situation is stable today but may require more transformation effort.
            """)

            profile_long = cluster_summary.melt(
                id_vars=["cluster", "profile", "n"],
                value_vars=["absence_rate", "KTI", "pct_decay", "strategic_share"],
                var_name="indicator",
                value_name="value",
            )
            profile_long["value"] = profile_long["value"] * 100
            profile_long["indicator"] = profile_long["indicator"].replace({
                "absence_rate": "Absenteeism",
                "KTI": "Knowledge transfer",
                "pct_decay": "Skill decay",
                "strategic_share": "Strategic training",
            })
            fig_profiles = px.bar(
                profile_long,
                x="indicator",
                y="value",
                color="profile",
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_profiles.update_layout(
                template="plotly_white",
                height=420,
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis_title="Business indicator",
                yaxis_title="Average value (%)",
                legend_title="Business profile",
            )
            st.plotly_chart(fig_profiles, use_container_width=True)

            st.subheader("Recommended Business Reading")
            for cluster_id in sorted(cluster_summary["cluster"].dropna().unique()):
                cluster_id = int(cluster_id)
                st.markdown(f"""
                **Cluster {cluster_id} - {cluster_names.get(cluster_id, "Cluster profile")}**  
                {cluster_descriptions.get(cluster_id, "")}  
                **Recommended action:** {cluster_actions.get(cluster_id, "")}
                """)

        with tab_details:
            col_scores, col_pca = st.columns([1, 1.4])

            with col_scores:
                st.subheader("Why 4 clusters?")
                fig_scores = px.line(
                    model_selection.sort_values("k"),
                    x="k",
                    y="silhouette_score",
                    markers=True,
                    color_discrete_sequence=[CACEIS_STEEL_BLUE],
                )
                fig_scores.update_layout(
                    template="plotly_white",
                    height=340,
                    margin=dict(l=20, r=20, t=30, b=20),
                    yaxis_title="Silhouette score",
                    xaxis_title="Number of clusters",
                )
                st.plotly_chart(fig_scores, use_container_width=True)

            with col_pca:
                st.subheader("2D Map of Monthly Situations")
                fig_pca = px.scatter(
                    pca_projection,
                    x="pc1",
                    y="pc2",
                    color="profile",
                    hover_data=["month", "entity", "cluster"],
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                fig_pca.update_layout(
                    template="plotly_white",
                    height=340,
                    margin=dict(l=20, r=20, t=30, b=20),
                    legend_title="Business profile",
                )
                st.plotly_chart(fig_pca, use_container_width=True)

            st.subheader("Cluster Distribution by Year")
            fig_year = px.bar(
                year_cluster_summary,
                x="year",
                y="n_rows",
                color=year_cluster_summary["cluster"].astype(str),
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_year.update_layout(
                template="plotly_white",
                height=340,
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis_title="Year",
                yaxis_title="Number of entity-months",
                legend_title="Cluster",
            )
            st.plotly_chart(fig_year, use_container_width=True)

            st.subheader("Entity-Month Results")
            display_clustered = clustered_dataset[[
                "month", "year", "entity", "profile", "cluster",
                "absence_rate", "KTI", "pct_decay", "strategic_share"
            ]].copy()
            st.dataframe(display_clustered, use_container_width=True, hide_index=True)

            if os.path.exists(ml_dataset_path):
                st.subheader("ML-ready Dataset Preview")
                ml_dataset = load_ml_dataset(ml_dataset_path)
                st.caption("This local file is used by the notebook to compute the clusters.")
                st.dataframe(ml_dataset.head(30), use_container_width=True)
            else:
                st.caption("Optional ML-ready CSV not found. The cluster results above are still available from the Excel workbook.")


# --- 7. PAGE 3 : KPI Interpretation ---
elif app_mode == "Interpretation Guide":
    st.title("Interpretation Guide")
    st.markdown("""
    ### 📊 Strategic Interpretation
    
    | Level | Status & Action |
    | :--- | :--- |
    | <h5 style="color:#28a745; margin:0;">🟢 Target Achieved</h5> | <ul><li><strong>Status:</strong> Asset Appreciation. High competitive advantage.</li><li><strong>Action:</strong> Maintain investments and share best practices.</li></ul> |
    | <h5 style="color:#ffc107; margin:0;">🟡 Warning</h5> | <ul><li><strong>Status:</strong> Stagnation. Early signs of structural weakness.</li><li><strong>Action:</strong> Perform "Deep-Dive" analysis on declining components.</li></ul> |
    | <h5 style="color:#D65063; margin:0;">🔴 Critical</h5> | <ul><li><strong>Status:</strong> Asset Depreciation. Risk of operational loss.</li><li><strong>Action:</strong> Immediate intervention required.</li></ul> |

    <br>
    
    ### 📈 Trend Analysis (▲/▼)
    * **Performance KPIs:** Green if increasing/ Red if decreasing.
    * **Risk KPIs (Skill Decay):** Green if decreasing/ Red if increasing.
    
    ### 🎯 Radar & Breakdown Interpretation
    * **Dashed Line (1.0):** Represents the strategic objective (Target).
    * **Contribution Table:** Details the impact of each pillar on the global CHHI score. A pillar with the ⚠️ icon indicates it is performing below target and negatively contributing to the Global Human Capital Score (CHHI).
    
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("Data Governance: GDPR Compliant. | WE ARE ONE CACEIS")

# --- 8. PAGE 4 : RBC INTEGRATION AUDIT ---
elif app_mode == "2023 RBC Integration":
    st.title("🏢 RBC Integration 2023")
    
    st.warning("""
        **Contextual Note on the data quality:** The 2023 figures are impacted by the acquisition of RBC Investor Services' European activities. 
    """) 

    st.markdown("""
        ### Resilience & Engagement Score (RE-Score) : Absenteeism 
        In 2023, 52% of absences are categorized as "Non-followed" due to legacy system mapping. 
        The Resilience Score (KPI 4) and the Total Weighted Aggregate should be interpreted with caution. 
        """)
