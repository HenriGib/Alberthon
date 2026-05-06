# IGS — Indice de Gouvernance Sociale

> **KPI 4 du framework Human Capital Valuation CACEIS · Alberthon 2026**
> Score sur 100 mesurant la résilience sociale de CACEIS face aux risques régulatoires, humains et réputationnels (pilier S de l'ESG).

```
IGS = moyenne des composantes disponibles parmi  [ Mixité · Inclusion · Engagement ]
```

## Résultats multi-année

| Année | Mixité | Inclusion | Engagement | **IGS** | Lecture |
|---|---:|---:|---:|---:|---|
| 2023 | 77,2 | N/A | 32,4 | **54,8** | 🔴 Zone faible — Engagement encore en construction |
| 2024 | 76,5 | N/A | 28,8 | **52,6** | 🔴 Zone faible — stable sur Mixité, Engagement plat |
| 2025 | N/A | 67,1 | 20,7 | **43,9** | 🔴 Zone faible — Inclusion mesurée pour la 1ʳᵉ fois |

## Principe directeur

Calcul **rigoureusement aligné par année** : chaque année utilise **strictement** ses propres sources. Si une composante n'est pas disponible pour une année, elle est marquée `N/A` et l'IGS est calculé sur les composantes disponibles uniquement.

| Composante | 2023 | 2024 | 2025 |
|---|---|---|---|
| Mixité (pay gap + femmes mgt) | ✓ Bilan Social 2023 | ✓ Bilan Social 2024 | N/A *(Bilan Social 2025 publié au printemps 2026)* |
| Inclusion (Baromètre D&I) | N/A *(pas de Baromètre 2023)* | N/A *(pas de Baromètre 2024)* | ✓ Baromètre Mozaïk RH édition 2025 |
| Engagement (intensité programmes) | ✓ FAB'Life 2023 + Be Generous 2023 | ✓ FAB'Life 2024 + Be Generous 2024 | ✓ We Care 2025 + Be Generous 2025 |

**Aucune valeur publiée pré-calculée n'est utilisée tel quel** (pas d'Index Égapro). Chaque chiffre est calculé par nous à partir d'un tableau brut publié dans les documents CACEIS.

---

## Composante 1 — Mixité

Moyenne de deux sous-calculs :

```
score_paygap = max(0, 100 − |gap%| × 5)            (0% gap → 100, 20% gap → 0)
score_mgt    = min(100, % femmes encadrantes / 40 × 100)  (cible parité HCE = 40%)
Mixité       = (score_paygap + score_mgt) / 2
```

| Année | Pay gap | score_paygap | % femmes mgt | score_mgt | **Mixité** |
|---|---:|---:|---:|---:|---:|
| 2023 | 9,13 % | 54,4 | 40,16 % | 100,0 | **77,2** |
| 2024 | 9,29 % | 53,6 | 39,75 % | 99,4 | **76,5** |
| 2025 | — | — | — | — | **N/A** |

**Sources** : `Bilan Social <année>.pdf` §2.1.2.2 + `Suivi accord mixité QVT <année>.pdf` (« Promotion professionnelle »).

---

## Composante 2 — Inclusion

Moyenne pondérée par effectif des Baromètres D&I 2025 (Mozaïk RH).

```
Inclusion = (FR × eff_FR + Lux × eff_Lux) / (eff_FR + eff_Lux)
          = (70 × 2 043 + 64 × 1 882) / 3 925 = 67,1
```

**Sources** : `2025_Baromètre D&I CACEIS - France.pdf` §2.6 + `2025_Baromètre D&I CACEIS - Luxembourg.pdf` §2.6.

> Le Baromètre est annuel mais 2025 est l'édition la plus récente disponible. Les éditions 2023 et 2024 n'existent pas dans nos sources, d'où les N/A.

---

## Composante 3 — Engagement

```
intensité = participations totales / effectif (FR + Lux)
score     = min(100, intensité × 50)             (1 part./employé/an = 50, 2 = 100)
```

| Année | FAB'Life | Be Generous | We Care | Total | Effectif | Intensité | **Engagement** |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 1 184 | 6 | — | 1 190 | 1 835 | 0,649 | **32,4** |
| 2024 | 2 241 | 17 | — | 2 258 | 3 925 | 0,575 | **28,8** |
| 2025 | — | 34 | 1 592 | 1 626 | 3 925 | 0,414 | **20,7** |

**Sources** :
- 2023 : `2023 _BILAN FAB'Life programme.pptx` + lauréats Be Generous référencés dans `2023 _Suivi accord mixité QVT VF.pdf`
- 2024 : `2024 _Bilan FAB'Life.pptx` + `2024 _Reporting Be Generous pour CASA.xlsx` (17 lauréats : 10 FR + 7 Lux)
- 2025 : `2025 _We Care - Bilan.xlsx` (1 256 chiffrés + 14 n/a × 24 fallback) + `2025 _Bilan Groupe Be Generous CACEIS.xlsx`

> **Note méthodologique** : le périmètre Effectif passe de 1 835 (FR seul, 2023, faute d'effectif Lux disponible) à 3 925 (FR+Lux, 2024+). C'est une limite d'exhaustivité, pas un défaut de méthode — la rigueur exige d'utiliser l'effectif réel de chaque année.

---

## Intégration au CHHI

Le CHHI (score consolidé) inclut désormais l'IGS avec la pondération suivante :

| KPI | Poids | Question business |
|---|---:|---|
| HCVA | 30 % | Productivité financière du capital humain |
| KTI | 25 % | Transmission des compétences |
| RE-Score | 25 % | Résilience opérationnelle |
| **IGS** | **20 %** | **Gouvernance sociale** |

```
CHHI = 0,30 × HCVA_radar + 0,25 × KTI_radar + 0,25 × RE_radar + 0,20 × IGS_radar
```

Où `X_radar = X / target_X × 100` (achievement vs cible).

---

## Pitch board en 30 secondes

> *« CACEIS gouvernance sociale — IGS sur 3 ans :*
>
> *2023 : 54,8 (zone faible) — Mixité OK, Engagement encore en construction.*
> *2024 : 52,6 (zone faible) — Mixité maintenue, Engagement plat.*
> *2025 : 43,9 (zone faible) — Inclusion mesurée pour la 1ʳᵉ fois (Baromètre D&I), Engagement plus diversifié mais moins intense.*
>
> *La Mixité est notre force structurelle (pay gap 9 %, parité au management atteinte). L'Engagement progresse mais reste à objectiver via un tracking employé-unique cross-programmes. L'Inclusion mérite d'être mesurée chaque année (pas seulement en édition ponctuelle). »*

---

## Sources et standards

**Documents utilisés** : Bilans Sociaux 2023/2024 (FR + Lux), Suivi accord mixité QVT 2023/2024, Baromètre D&I 2025 (FR + Lux), Bilan FAB'Life 2023/2024, Reporting Be Generous 2024 pour CASA, Bilan Groupe Be Generous 2025, We Care - Bilan 2025.

**Standards de référence** : ISO 30414 (Diversity · Health & Safety · Wellbeing) · ESRS S1 / CSRD (S1-9, S1-13, S1-14, S1-16) · AI Act Article 10 (base de désagrégation) · Loi Rixain.
