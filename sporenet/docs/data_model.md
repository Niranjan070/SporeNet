# SporeNet Data Model & Alignment Specification

This document details the data architecture, temporal alignment methodology, inoculum decay model, and proxy risk labeling rules for SporeNet.

---

## 📌 Critical Temporal Join Rule

> **CRITICAL ARCHITECTURAL REQUIREMENT:**  
> **The join key between spore trap samples and continuous microclimate telemetry is ALWAYS `exposure_start` and `exposure_end` from the `samples` table. NEVER use `lab_capture_date` or image creation timestamps for temporal joining.**  
>  
> *Rationale:* Microscopic spore imaging is conducted offline in a laboratory 1–3 days after field trap retrieval. Joining on `lab_capture_date` would introduce severe temporal misalignment between weather conditions during field spore accumulation and lab image processing.

---

## 📊 Database Schema Definitions

### 1. `samples` Table
Stores metadata and quantitative spore counts derived from weekly field air-trap slides.

| Field Name | Type | Example | Description & Purpose |
| :--- | :--- | :--- | :--- |
| `sample_id` | STRING (PK) | `S-2026-07-28-03` | Unique identifier for each physical trap sample |
| `field_id` | STRING | `F01` | Agricultural plot identifier for spatial matching |
| `trap_id` | STRING | `TRAP-A` | Physical volumetric spore trap identifier |
| `exposure_start` | DATETIME | `2026-07-21 09:00:00` | Start timestamp of field air sampling window |
| `exposure_end` | DATETIME | `2026-07-28 09:00:00` | End timestamp of field air sampling window |
| `image_path` | STRING | `data/raw/images/S-2026-07-28-03.tif` | File path to high-res brightfield slide capture |
| `spore_magnaporthe_oryzae` | INTEGER | `42` | Primary target count (Rice Blast) |
| `spore_alternaria` | INTEGER | `5` | Background count: *Alternaria* spp. |
| `spore_bipolaris` | INTEGER | `3` | Background count: *Bipolaris* spp. |
| `spore_curvularia` | INTEGER | `8` | Background count: *Curvularia* spp. |
| `spore_curvularia_eragrostidis` | INTEGER | `2` | Background count: *Curvularia eragrostidis* |
| `spore_exserohilum` | INTEGER | `1` | Background count: *Exserohilum* spp. |
| `spore_fusarium` | INTEGER | `12` | Background count: *Fusarium* macroconidia |
| `spore_fusarium_microconidie` | INTEGER | `4` | Background count: *Fusarium* microconidia |
| `spore_mycelium` | INTEGER | `7` | Background count: Vegetative hyphae fragments |
| `lab_capture_date` | DATE | `2026-07-30` | Stored for lab audit log (**NEVER used for joining**) |
| `officer_id` | STRING | `OFC-001` | Identifier of field technician who retrieved slide |

---

### 2. `weather` Table
Stores 24/7 continuous microclimate sensor telemetry logged at 5–15 minute intervals by Raspberry Pi edge nodes.

| Field Name | Type | Example | Description & Purpose |
| :--- | :--- | :--- | :--- |
| `timestamp` | DATETIME | `2026-07-28 09:15:00` | Measurement timestamp (UTC/Local) |
| `field_id` | STRING | `F01` | Agricultural plot identifier |
| `trap_id` | STRING | `TRAP-A` | Nearest spore trap identifier |
| `temp_c` | FLOAT | `27.4` | Ambient air temperature in °C |
| `humidity_pct` | FLOAT | `84.2` | Relative humidity percentage (RH %) |
| `wind_kmh` | FLOAT | `12.1` | Wind speed in km/h |
| `rainfall_mm` | FLOAT | `3.2` | Cumulative rainfall during sample interval in mm |

---

### 3. `aligned_features` Table
Output of the temporal alignment function combining spore counts, look-back historical weather, look-forward weather forecasts, diversity metrics, and inoculum decay state.

| Field Name | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `sample_id` | STRING (FK) | `S-2026-07-28-03` | Primary key link to `samples` |
| `field_id` | STRING | `F01` | Plot location identifier |
| `exposure_start` | DATETIME | `2026-07-21 09:00:00` | Look-back weather window start |
| `exposure_end` | DATETIME | `2026-07-28 09:00:00` | Look-back weather window end / Forecast start |
| `spore_magnaporthe_oryzae` | INTEGER | `42` | *M. oryzae* spore count |
| `spore_alternaria` | INTEGER | `5` | *Alternaria* count |
| `spore_bipolaris` | INTEGER | `3` | *Bipolaris* count |
| `spore_curvularia` | INTEGER | `8` | *Curvularia* count |
| `spore_curvularia_eragrostidis` | INTEGER | `2` | *C. eragrostidis* count |
| `spore_exserohilum` | INTEGER | `1` | *Exserohilum* count |
| `spore_fusarium` | INTEGER | `12` | *Fusarium* count |
| `spore_fusarium_microconidie` | INTEGER | `4` | *Fusarium microconidie* count |
| `spore_mycelium` | INTEGER | `7` | *Mycelium* count |
| `total_spores` | INTEGER | `84` | Sum of all 9 spore species counts |
| `diversity_index` | FLOAT | `1.72` | Shannon entropy ($H = -\sum p_i \ln p_i$) of spore vector |
| `lb_mean_temp` | FLOAT | `25.8` | Mean temperature (°C) in look-back window |
| `lb_mean_humidity` | FLOAT | `86.4` | Mean relative humidity (%) in look-back window |
| `lb_wet_hours` | FLOAT | `64.5` | Total hours with RH > 80% during look-back window |
| `lb_rain_sum` | FLOAT | `24.8` | Cumulative rainfall (mm) during look-back window |
| `lb_blast_risk_days` | INTEGER | `4` | Days meeting Rice Blast infection rules (24–28°C AND RH > 90%) |
| `lf_fc_wet_hours` | FLOAT | `58.0` | Forecasted wet hours (RH > 80%) in look-forward 7 days |
| `lf_fc_rain_prob` | FLOAT | `0.65` | Forecasted rainfall probability (0–1.0) in look-forward window |
| `lf_fc_blast_risk_days` | INTEGER | `3` | Forecasted blast risk days in look-forward 7 days |
| `inoculum_state_prev` | FLOAT | `18.5` | Exponentially decayed inoculum state from previous week |
| `proxy_risk_label` | STRING | `High` | Derived disease risk level: `Low`, `Medium`, `High`, `Critical` |

---

## ⏱️ Temporal Alignment & Windowing Logic

For each weekly slide sample $S_t$:
1. **Look-back Window ($W_{LB}$):** $[S_t.\text{exposure\_start}, S_t.\text{exposure\_end}]$
   - Spans 7 days (168 hours) of continuous 10-minute weather readings.
   - Aggregates historical microclimate conditions during spore dispersion and trap exposure.
2. **Look-forward Window ($W_{LF}$):** $[S_t.\text{exposure\_end}, S_t.\text{exposure\_end} + 7 \text{ days}]$
   - Spans 7 days of short-term weather forecast telemetry.
   - Evaluates upcoming microclimate conditions conducive to spore germination and appressorium formation.

---

## 📉 Inoculum Decay Dynamics

Aerobiological inoculum viability decays exponentially between sampling intervals due to UV degradation, desiccation, and wash-off:

$$\text{state}_t = \text{state}_{t-1} \times \exp(-k) + \text{count}_{t,\text{magnaporthe\_oryzae}}$$

Where:
- $k = 0.3$ default decay constant (half-life $\approx 2.31$ weeks).
- $\text{state}_0 = 0.0$ at initial setup.
- Hold-last-value fallback is used for missing sampling points in MVP.

---

## 🧬 Pathogenicity Weights & Proxy Label Derivation

In the absence of field-reported disease outcomes, a domain-grounded **Proxy Risk Label** is calculated using a **Two-Factor Rule with Veto Power**:

1. **Inoculum Bucket** (Primary Target: `magnaporthe_oryzae`, Class 0):
   - **High:** `primary_spore_count` $\ge 20$
   - **Medium:** $5 \le$ `primary_spore_count` $< 20$
   - **Low:** `primary_spore_count` $< 5$

2. **Weather Bucket** (Look-Forward Forecast Window):
   - **High:** `lf_fc_blast_risk_days` $\ge 3$ AND `lf_fc_wet_hours` $\ge 36$
   - **Medium:** `lf_fc_blast_risk_days` $\ge 1$ OR `lf_fc_wet_hours` $\ge 24$
   - **Low:** Otherwise

3. **Veto Rules & Rule Matrix:**
   - **Veto 1:** If Inoculum is **Low** $\rightarrow$ Risk is **`Low`** (no inoculum = no infection).
   - **Veto 2:** If Weather is **Low** $\rightarrow$ Risk is **`Low`** (dry/hostile forecast = no infection).
   - **Inoculum High + Weather High** $\rightarrow$ **`Critical`**
   - **Inoculum High + Weather Medium** $\rightarrow$ **`High`**
   - **Inoculum Medium + Weather High** $\rightarrow$ **`High`**
   - **Inoculum Medium + Weather Medium** $\rightarrow$ **`Medium`**

### Species Pathogenicity Weight Matrix ($w_i$)

| Class ID | Species | Weight ($w_i$) | Agronomic Justification |
| :---: | :--- | :---: | :--- |
| 0 | `magnaporthe_oryzae` | **1.00** | Primary target pathogen; causative agent of Rice Blast (high epidemic potential) |
| 1 | `alternaria` | **0.00** | Benign background class (used as context feature only) |
| 2 | `bipolaris` | **0.00** | Benign background class (used as context feature only) |
| 3 | `curvularia` | **0.00** | Benign background class (used as context feature only) |
| 4 | `curvularia_eragrostidis` | **0.00** | Benign background class (used as context feature only) |
| 5 | `exserohilum` | **0.00** | Benign background class (used as context feature only) |
| 6 | `fusarium` | **0.00** | Benign background class (used as context feature only) |
| 7 | `fusarium_microconidie` | **0.00** | Benign background class (used as context feature only) |
| 8 | `mycelium` | **0.00** | Benign background class (used as context feature only) |

---

## 🧮 Worked Alignment Example

### Inputs:
- **Sample Metadata:** `S-2026-07-28-03`, `exposure_start` = `2026-07-21 09:00`, `exposure_end` = `2026-07-28 09:00`
- **Spore Counts:** `M. oryzae`=42, `Alternaria`=5, `Bipolaris`=3, `Curvularia`=8, `C. eragrostidis`=2, `Exserohilum`=1, `Fusarium`=12, `Fusarium micro`=4, `Mycelium`=7.
- **Previous Inoculum State ($\text{state}_{t-1}$):** `15.0`
- **Weather Telemetry (168 hours):** Mean Temp = `26.2°C`, Mean RH = `88.5%`, Wet Hours = `72.0`, Rain Sum = `35.4 mm`, Blast Risk Days = `4`.
- **Forecast Telemetry (7 days):** Forecast Wet Hours = `60.0`, Rain Prob = `0.70`, Blast Risk Days = `3`.

### Computations:
1. **Total Spores:** $42 + 5 + 3 + 8 + 2 + 1 + 12 + 4 + 7 = 84$
2. **Diversity Index ($H$):** $-\sum (p_i \ln p_i) \approx 1.72$
3. **Inoculum Decay:** $\text{state}_t = 15.0 \times \exp(-0.3) + 42 = (15.0 \times 0.7408) + 42 = 11.11 + 42 = 53.11$
4. **Weighted Spore Score ($S_{\text{weighted}}$):**  
   $(42 \times 1.0) + (5 \times 0.45) + (3 \times 0.50) + (8 \times 0.35) + (2 \times 0.30) + (1 \times 0.40) + (12 \times 0.70) + (4 \times 0.50) + (7 \times 0.25) = 42 + 2.25 + 1.5 + 2.8 + 0.6 + 0.4 + 8.4 + 2.0 + 1.75 = 61.7$
5. **Weather Risk Factor ($W$):** $(4 / 7.0) + (72.0 / 168.0) = 0.571 + 0.429 = 1.00$
6. **Proxy Risk Score ($R$):** $61.7 \times (1.0 + 1.00) = 123.4$
7. **Proxy Risk Label:** **`Critical`** ($R \ge 120.0$)

---

### Output Row (`aligned_features`):

```json
{
  "sample_id": "S-2026-07-28-03",
  "field_id": "F01",
  "exposure_start": "2026-07-21 09:00:00",
  "exposure_end": "2026-07-28 09:00:00",
  "spore_magnaporthe_oryzae": 42,
  "spore_alternaria": 5,
  "spore_bipolaris": 3,
  "spore_curvularia": 8,
  "spore_curvularia_eragrostidis": 2,
  "spore_exserohilum": 1,
  "spore_fusarium": 12,
  "spore_fusarium_microconidie": 4,
  "spore_mycelium": 7,
  "total_spores": 84,
  "diversity_index": 1.72,
  "lb_mean_temp": 26.2,
  "lb_mean_humidity": 88.5,
  "lb_wet_hours": 72.0,
  "lb_rain_sum": 35.4,
  "lb_blast_risk_days": 4,
  "lf_fc_wet_hours": 60.0,
  "lf_fc_rain_prob": 0.70,
  "lf_fc_blast_risk_days": 3,
  "inoculum_state_prev": 15.0,
  "proxy_risk_label": "Critical"
}
```
