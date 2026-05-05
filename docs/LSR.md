# LSR — License-to-Operate & Sustainability Resilience

> 8ᵉ KPI du framework Human Capital Valuation CACEIS · Alberthon 2026
> Score sur 100 mesurant la **résilience sociale** de CACEIS face aux risques régulatoires, humains et réputationnels (gouvernance / ESG-S).

```
LSR = (Mixité + Inclusion + Engagement) / 3
```

## Résultat 2024

| Score | Valeur | Lecture |
|---|---:|---|
| Mixité | **76,5** | Quasi-cible. Levier = pay gap résiduel 9,3 %. |
| Inclusion | **67,1** | Zone bonne (Mozaïk RH). |
| Engagement | **49,3** | Plancher. ~1 participation/employé/an. |
| **LSR** | **64,3 / 100** | 🟡 Zone jaune |

## Principe directeur

Chaque chiffre est **calculé par nous** à partir d'un tableau brut publié dans les documents CACEIS officiels. **Aucun score externe pré-calculé** (Index Égapro, etc.) n'est utilisé tel quel — tout est reproductible depuis les données sources.

Une seule hypothèse explicite : le fallback des 14 lignes `n/a` du fichier We Care est rempli avec **24 participants par défaut**, valeur minimale moyenne par type d'action observée dans le fichier (= moyenne du type *Ateliers*). La sensibilité testée montre un écart de moins de 3 points entre les scénarios extrêmes → conclusion robuste.

---

## Composante 1 — Mixité (76,5)

### 1.1 Pay gap

Source : `Bilan Social 2024.pdf` §2.1.2.2

| | Femmes | Hommes |
|---|---:|---:|
| SAB moyen pondéré | 54 753 € | 60 360 € |

```
gap = (60 360 − 54 753) / 60 360 = 9,29 %
score_paygap = max(0, 100 − 9,29 × 5) = 53,6
```

### 1.2 % femmes au management

Source : `Suivi accord mixité diversité QVT 2024 vDef.pdf` (« Promotion professionnelle »)

| Classification | F | H | Total |
|---|---:|---:|---:|
| H | 0 | 2 | 2 |
| I | 10 | 25 | 35 |
| J | 21 | 20 | 41 |
| K | 25 | 33 | 58 |
| HC | 41 | 67 | 108 |
| **Total** | **97** | **147** | **244** |

```
% femmes encadrantes = 97 / 244 = 39,75 %
score_mgt = min(100, 39,75 / 40 × 100) = 99,4
```

```
Mixité = (53,6 + 99,4) / 2 = 76,5
```

---

## Composante 2 — Inclusion (67,1)

Moyenne pondérée par effectif des Baromètres D&I 2025 (Mozaïk RH).

| Pays | Score | Effectif |
|---|---:|---:|
| France | 70 % | 2 043 |
| Luxembourg | 64 % | 1 882 |

```
Inclusion = (70 × 2 043 + 64 × 1 882) / 3 925 = 67,1
```

---

## Composante 3 — Engagement (49,3)

**Intensité** = participations totales aux programmes sociaux ÷ effectif. Pas d'hypothèse sur l'unicité des employés — le ratio est un fait calculable.

| Programme | Participations | Source |
|---|---:|---|
| FAB'Life (CACEIS pur, hors CASA) | 2 241 | `Bilan FAB'Life 2024.pptx` slide 31 |
| We Care chiffrés | 1 256 | `We Care - Bilan 2025.xlsx` sheet `Data` |
| We Care fallback (14 n/a × 24) | + 336 | (Communications, E-learning, Charte…) |
| Be Generous (lauréats CACEIS) | 34 | `Bilan Groupe Be Generous CACEIS 2025.xlsx` |
| **Total** | **3 867** | |

```
intensité = 3 867 / 3 925 = 0,985 participation/employé/an
score = min(100, 0,985 × 50) = 49,3
```

> **Quick-win HR** : un tracking employé-unique cross-programmes ferait passer ce score d'une intensité brute à un vrai taux de couverture (60-70 % réaliste).

---

## LSR final

```
LSR = (76,5 + 67,1 + 49,3) / 3 = 64,3 / 100   🟡 Zone jaune
```

## Sensibilité au fallback `n/a`

| Fallback | We Care total | LSR |
|---:|---:|---:|
| 0 | 1 256 | 62,9 |
| 12 | 1 424 | 63,6 |
| **24 (retenu)** | **1 592** | **64,3** |
| 36 | 1 760 | 65,0 |
| 48 | 1 928 | 65,7 |

LSR varie de moins de 3 points entre les scénarios extrêmes.

## Pitch board en 30 secondes

> *« CACEIS score 64/100 sur sa résilience sociale. Mixité quasi-cible (76 — la parité au management est atteinte à 39,75 %, le pay gap résiduel de 9,3 % est notre vrai levier). Inclusion en zone bonne (67). Engagement à 49 — c'est notre plancher : ~1 participation par employé par an. Quick-win HR : tracker les employés uniques pour passer d'une intensité à un vrai taux d'engagement. »*

## Sources

- `Bilan Social 2024.pdf` §2.1.2.2 — pay gap
- `Suivi accord mixité diversité QVT 2024 vDef.pdf` — % femmes encadrantes
- `Baromètre D&I CACEIS - France.pdf` §2.6 + `- Luxembourg.pdf` §2.6 — inclusion
- `Bilan Social 2024.pdf` + `Bilan Social 2024 Luxembourg.pdf` §1.1.1 — effectifs
- `Bilan FAB'Life 2024.pptx` slide 31 — FAB'Life
- `We Care - Bilan 2025.xlsx` sheet Data — We Care
- `Bilan Groupe Be Generous CACEIS 2025.xlsx` sheet Lauréats — Be Generous

## Standards

- ISO 30414 (Diversity · Health & Safety · Wellbeing)
- ESRS S1 (CSRD) — S1-9, S1-13, S1-14, S1-16
- AI Act Article 10 — base de désagrégation pour audits de biais
- Loi Rixain (sans usage de l'Index Égapro lui-même, non reproductible avec les données disponibles)
