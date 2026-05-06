# Alberthon Caceis PROJECT 


# Human Capital Analytics Dashboard

Interactive dashboard to monitor **Human Capital performance** using strategic KPIs, built with **Python, Pandas and Streamlit**.

# Project Overview :

This project aims to analyze and visualize **Human Resources performance** through a set of key indicators:

* Productivity
* Knowledge & training impact
* Skill obsolescence risk
* Workforce resilience
* Strategic alignment

It includes:

* a **data preprocessing pipeline**
* a **KPI calculation layer**
* an **interactive dashboard**


# Architecture :

```bash
.
├── Preprocessing.ipynb        # Data cleaning & KPI computation
├── app.py                    # Streamlit dashboard
├── outputs/
│   ├── kpi_yearly.csv
│   ├── kpi_by_entity.csv
│   └── kpi_by_direction.csv
└── README.md
```

# Tech Stack :

* Python
* Pandas / NumPy
* Streamlit
* Plotly


# OUR KPIs

1. HCVA — Human Capital Value Added

Measures workforce productivity.

```
HCVA = PNB / FTE
```

2. KTI — Knowledge Transfer Index

Measures how well training is applied in practice.

```
Yes = 1 | Partial = 0.5 | No = 0
KTI = average score
```

3. Skill Decay

Measures skill obsolescence risk.

```
% employees without training > 18 months
```

4. RE-Score — Resilience & Engagement

Measures workforce stability.

```
RE = Engagement Score / Absenteeism Rate
```

5. SPE — Strategic Payroll Elasticity

Measures alignment with strategic skills.

```
% of strategic training hours
```

6. CHHI — Human Capital Health Index

Global performance index based on weighted KPIs:

* HCVA → 30%
* KTI → 20%
* Skill Decay → 20%
* RE-Score → 15%
* SPE → 15%

7. LSR — License-to-Operate & Sustainability Resilience

Measures social resilience: regulatory, human, and reputational risk exposure
of the workforce (governance / ESG-S pillar).

```
LSR = (Mixité + Inclusion + Engagement) / 3
```

* Mixité     — pay gap + % women in management (Bilan Social + Suivi accord mixité)
* Inclusion  — Baromètre D&I FR + Lux (weighted by headcount)
* Engagement — participations FAB'Life + We Care + Be Generous / headcount

LSR Score	Meaning
< 60		At Risk → Material exposure to regulatory / reputational risk
60 – 75		Yellow zone → Acceptable but improvable, action plan required
> 75		Green zone → Strong social asset, low exposure

LSR 2024 = 64.3/100 (yellow zone). Full methodology in `docs/LSR.md`,
notebook in `LSR_KPI.ipynb`.

Data Pipeline

1. Raw data is processed in `Preprocessing.ipynb`
2. KPI datasets are generated:

   * by year
   * by legal entity
   * by direction
3. Results are exported as CSV files
4. The dashboard reads and visualizes these datasets

Dashboard Features

* Year selection
* Filtering by legal entity
* KPI monitoring with thresholds
* Trend visualization (line charts)
* Radar chart (global performance)
* KPI interpretation panel

# How to Run

1. Install dependencies

```bash
pip install pandas numpy streamlit plotly
```

2. Run preprocessing

Open and run:
Preprocessing.ipynb


3. Launch dashboard

bash
streamlit run app.py


Then open:
http://localhost:8501

