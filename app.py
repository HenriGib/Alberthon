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
    file_path = "chhi_dashboard_dataset.csv"
    
    if os.path.exists(file_path):
        # On lit le CSV (vérifiez si c'est une virgule ou un point-virgule)
        df_raw = pd.read_csv(file_path)
        
        # 1. Agrégation par année (Moyenne globale CACEIS)
        # On ignore les colonnes 'Legal Entity' et 'Direction' pour tout grouper
        df_grouped = df_raw.groupby("Year").agg({
            "HCVA": "mean",
            "KTI": "mean",
            "Skill Decay": "mean",
            "RE-Score": "mean",
            "SPE": "mean",
            "CHHI Index": "mean"
        }).reset_index()

        # 2. Ajustement des échelles (Basé sur votre exemple)
        # Votre SPE est à 0.0053 -> on le passe en % (0.53%)
        df_grouped["SPE"] = df_grouped["SPE"] * 100
        
        # Votre KTI est à 0.5 -> on le passe en % (50%)
        df_grouped["KTI"] = df_grouped["KTI"] * 100

        # Votre Skill Decay est à 0.0 -> on le laisse ou multiplie par 100
        df_grouped["Skill Decay"] = df_grouped["Skill Decay"] * 100

        df_grouped["RE-Score"] = df_grouped["RE-Score"] / 4

        # 3. Renommage des colonnes pour le Dashboard
        df_final = df_grouped.rename(columns={
            "Year": "Year",
            "HCVA": "HCVA (k€)",
            "KTI": "KTI (%)",
            "Skill Decay": "Skill Decay (%)",
            "RE-Score": "RE-Score",
            "SPE": "SPE (%)",
            "CHHI Index": "CHHI Index"
        })
        
        return df_final
    else:
        st.error(f"Fichier '{file_path}' non trouvé.")
        return pd.DataFrame()

df = load_data()

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

# --- 4. NAVIGATION & LOGO ---
logo_path = "CACEIS_Investor_Services_logo.png" 
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)
else:
    st.sidebar.title("WE ARE ONE CACEIS")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Go to:", ["Live Dashboard", "Interpretation Guide", "2023 RBC Integration"])

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
        {"id": "CHHI", "label": "Global Human Capital Score (CHHI)", "col": "CHHI Index", "unit": "%", "target": 80, "rev": False, "is_master": True, "def": "CACEIS Human Capital Health Index (CHHI)", "val": "Global Human Capital Score.", "form": "Weighted average of 5 KPIs.", "logic": ">80% (Green) / >64% (Yellow) / <64% (Red)"},
        {"id": "HCVA", "label": "KPI 1: Productivity (HCVA)", "col": "HCVA (k€)", "unit": "k€", "target": 145, "rev": False, "is_master": False, "def": "Human Capital Value Added (HCVA) per FTE", "val": "Financial efficiency of human capital.", "form": "[GNP - (OpEx-Payroll)]/FTE", "logic": ">145k€ (Green) / >116k€ (Yellow) / <116k€ (Red)"},
        {"id": "KTI", "label": "KPI 2: Knowledge (KTI)", "col": "KTI (%)", "unit": "%", "target": 75, "rev": False, "is_master": False, "def": "Knowledge Transfer Index (KTI)", "val": "Training ROI and skill application.", "form": "Reviews / Manager Assessment", "logic": ">75% (Green) / >60% (Yellow) / <60% (Red)"},
        {"id": "SD", "label": "KPI 3: Risk (Skill Decay)", "col": "Skill Decay (%)", "unit": "%", "target": 15, "rev": True, "is_master": False, "def": "Skill Decay Rate (Obsolescence Index)", "val": "Risk of expertise erosion.", "form": "% without training > 18 months", "logic": "<12% (Green) / <18% (Yellow) / >18% (Red)"},
        {"id": "RE", "label": "KPI 4: Resilience (RE-Score)", "col": "RE-Score", "unit": "/5", "target": 4.0, "rev": False, "is_master": False, "def": "Resilience & Engagement Score (RE-Score)", "val": "Workforce stability and morale.", "form": "Engagement / Absenteeism", "logic": ">4.0 (Green) / >3.2 (Yellow) / <3.2 (Red)"},
        {"id": "SPE", "label": "KPI 5: Strategy (SPE)", "col": "SPE (%)", "unit": "%", "target": 25, "rev": False, "is_master": False, "def": "Strategic Payroll Elasticity (SPE)", "val": "Agility towards future-proof jobs.", "form": "% payroll growth roles", "logic": ">25% (Green) / >20% (Yellow) / <20% (Red)"}
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

    st.markdown("---")
    st.subheader("Global Human Capital Score: Radar & Pillar Breakdown")
    col_radar, col_table = st.columns([2, 1.2])

    with col_radar:
        categories = ['Productivity (HCVA)', 'Knowledge (KTI)', 'Risk (Skill Decay)', 'Resilience (RE-Score)', 'Strategy (SPE)']
        r_hcva = df_current['HCVA (k€)'].mean() / 145
        r_kti = (df_current['KTI (%)'].mean() / 100) / 0.75
        r_risk = 12 / df_current['Skill Decay (%)'].mean() 
        r_re = df_current['RE-Score'].mean() / 4.0
        r_spe = (df_current['SPE (%)'].mean() / 100) / 0.25
        r_values = [r_hcva, r_kti, r_risk, r_re, r_spe]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=[1.0]*5 + [1.0], theta=categories + [categories[0]], fill='toself', fillcolor='rgba(136, 139, 141, 0.05)', line=dict(color=CACEIS_RED, dash='dash'), name='Target Threshold'))
        fig_radar.add_trace(go.Scatterpolar(r=r_values + [r_values[0]], theta=categories + [categories[0]], fill='toself', fillcolor='rgba(136, 139, 141, 0.4)', line=dict(color=CACEIS_GREY, width=3), name='Actual Performance'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1.5])), showlegend=True, height=450, margin=dict(t=20, b=20), template="plotly_white")
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_table:
        st.markdown("""
            <style>
                /* Colonne KPI (Index) */
                [data-testid="stTable"] td:first-child {
                    white-space: nowrap !important;
                    min-width: 70px !important;
                }
                /* Colonne Weighting */
                [data-testid="stTable"] th:nth-child(4), 
                [data-testid="stTable"] td:nth-child(3) {
                    white-space: nowrap !important;
                    min-width: 100px !important;
                }
                /* Colonne Impact */
                [data-testid="stTable"] th:last-child, 
                [data-testid="stTable"] td:last-child {
                    white-space: nowrap !important;
                    min-width: 80px !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        breakdown_df = pd.DataFrame({"Pillar": categories, "Target Achievement": [f"{v*100:.1f}%" for v in r_values], "Weighting": ["30%", "20%", "20%", "15%", "15%"], "Impact": ["✅" if v >= 1.0 else "⚠️" for v in r_values]})
        breakdown_df.index = [f"KPI {i+1}" for i in range(len(breakdown_df))]
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("**CHHI (Weighted average of 5 KPIs) Contribution Details**")     
        st.table(breakdown_df)
        st.info("⚠️ indicates it is performing below target and negatively contributing to the Global Human Capital Score (CHHI)")

# --- 6. PAGE 2 : KPI Interpretation ---
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

# --- 7. PAGE 3 : RBC INTEGRATION AUDIT ---
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
