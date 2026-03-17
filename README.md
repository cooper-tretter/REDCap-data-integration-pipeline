# REDCap Data Integration Pipeline — How-To Guide

This guide walks you through everything you need to enter, extract, and process data using the PATH Lab's REDCap integration pipeline. It also covers how to make changes to the pipeline if needed.

**Prefer a point-and-click interface?** See [Web Interface (No Command Line)](#web-interface-no-command-line) below.

## Table of Contents

1. [Web Interface (No Command Line)](#web-interface-no-command-line)
2. [Setup](#1-setup)
3. [Directory Structure](#2-directory-structure)
4. [End-to-End Workflow: From REDCap Export to Analysis-Ready Data](#3-end-to-end-workflow-from-redcap-export-to-analysis-ready-data)
5. [Generating Individual Participant Reports](#4-generating-individual-participant-reports)
6. [Generating Clinic Quarterly Reports](#5-generating-clinic-quarterly-reports)
7. [Understanding the Output](#6-understanding-the-output)
8. [How to Make Changes](#7-how-to-make-changes)
9. [Measures Reference](#8-measures-reference)
10. [Troubleshooting](#9-troubleshooting)

---

## Web Interface (No Command Line)

If you prefer a point-and-click interface, the pipeline includes a web app. After setup, run:

```bash
streamlit run app.py
```

This opens a browser window where you can:
- **Tab 1 — Data Integration:** Upload a REDCap export, click "Run Integration", and download the results
- **Tab 2 — Individual Reports:** Select a participant and timepoint, click "Generate Report", and download the PDF
- **Tab 3 — Clinic Reports:** Select a clinic and report type, click "Generate", and download the PDF

No other command-line knowledge needed after this initial launch.

---

## 1. Setup

### Install Python

You need Python 3.7 or later. Check your version:
```bash
python --version
```

### Install Dependencies

From the project root directory:
```bash
pip install -r requirements.txt
```

This installs: `pandas`, `numpy`, `openpyxl` (for Excel files), and `matplotlib` (for PDF reports).

### Clone the Repository

```bash
git clone https://github.com/cooper-tretter/REDCap-data-integration-pipeline.git
cd RWSEStudy
```

---

## 2. Directory Structure

```
RWSEStudy/
├── scripts/
│   ├── integrate.py                    # Main integration script
│   ├── generate_sample_data.py         # Generate synthetic test data
│   ├── generate_individual_report.py   # Individual participant PDF reports
│   └── generate_clinic_report.py       # Clinic quarterly PDF reports
├── data/
│   ├── sample_data.xlsx                # Synthetic REDCap export (120 participants)
│   ├── insights.xlsx                   # Integration output (11 analytical tabs)
│   ├── insights.csv                    # Integration output (main data tab, CSV)
│   └── data_dictionary_codebook.xlsx   # REDCap codebook (all 72 instruments)
├── reports/                            # Example PDF reports
├── documentation/                      # Protocol, data structure docs, meeting notes
├── requirements.txt
└── README.md                           # This file
```

---

## 3. End-to-End Workflow: From REDCap Export to Analysis-Ready Data

### Step 1: Export Data from REDCap

1. Log in to REDCap
2. Go to **Data Exports, Reports, and Stats**
3. Export as **Excel / CSV (raw data)**
4. Save the file (e.g., `redcap_export.xlsx`)

### Step 2: Run the Integration Script

**Using sample data (to test the pipeline):**
```bash
python scripts/integrate.py
```
This uses `data/sample_data.xlsx` by default and outputs to `data/`.

**Using real data:**
```bash
python scripts/integrate.py /path/to/redcap_export.xlsx
```

**Specifying an output directory:**
```bash
python scripts/integrate.py /path/to/redcap_export.xlsx /path/to/output_dir
```

### Step 3: Review the Output

The script produces two files in the output directory:
- **`insights.xlsx`** — Excel workbook with 11 analytical tabs (see [Understanding the Output](#6-understanding-the-output))
- **`insights.csv`** — CSV of the main data tab (for use in R, SPSS, etc.)

### What the Integration Script Does

1. **Reads** the long-format REDCap export (multiple rows per participant, one per timepoint)
2. **Maps timepoints** to descriptive labels: `bl` (baseline), `3d` (3 days), `1mo`, `3mo`, `6mo`, `12mo`
3. **Consolidates rescheduled sessions** — participants with `_r` timepoints in REDCap get their data merged into the standard columns
4. **Pivots** to wide format (one row per participant, with columns like `phq9_total_bl`, `phq9_total_1mo`, etc.)
5. **Calculates scores** — total scores, severity classifications, response/remission flags
6. **Orders columns** so short-form items appear before long-form items (e.g., AUDIT-C questions 1-3 before AUDIT questions 4-10)
7. **Generates analytical tabs** — summary statistics, demographics, data completeness, per-measure analyses

---

## 4. Generating Individual Participant Reports

These are personalized PDF progress reports for participants at follow-up timepoints (1mo, 3mo, 6mo, 12mo).

### Generate Example Reports

```bash
python scripts/generate_individual_report.py
```

This creates example PDFs in the `reports/` directory using sample data.

### Generate a Report for a Specific Participant

In Python:
```python
from scripts.generate_individual_report import generate_individual_report
import pandas as pd

df = pd.read_csv('data/insights.csv')

generate_individual_report(
    df=df,
    participant_id=31,          # record_id
    timepoint='3mo',            # '1mo', '3mo', '6mo', or '12mo'
    output_path='reports/participant_31_3mo.pdf',
    clinic_name='Example Clinic'
)
```

### What's in an Individual Report

- **Score trajectories** for PHQ-9, GAD-7, and WHO-5 with color-coded severity bands
- **Change from baseline** showing absolute and percentage improvement
- **Notable Improvements** — specific questions where the participant showed significant positive change (e.g., "Feeling tired or having little energy: 3 → 0 out of 3")

---

## 5. Generating Clinic Quarterly Reports

These are aggregate reports for clinics, available as Q2 (mid-year) or Q4 (annual).

### Generate Example Reports

```bash
python scripts/generate_clinic_report.py
```

This creates example Q2 and Q4 PDFs in the `reports/` directory.

### Generate a Report for a Specific Clinic

In Python:
```python
from scripts.generate_clinic_report import generate_clinic_report
import pandas as pd

df = pd.read_csv('data/insights.csv')

# Filter to a specific clinic's participants
clinic_df = df[df['clinic'] == 'Clinic Name']

generate_clinic_report(
    df=clinic_df,
    clinic_name='Clinic Name',
    report_type='Q2',              # 'Q2' (mid-year) or 'Q4' (annual)
    output_path='reports/clinic_Q2.pdf',
    study_df=df                    # Full dataset for study-wide comparisons
)
```

### What's in a Clinic Report

- **Key metrics** — total participants, response rates, remission rates
- **Comparison to study-wide averages** — how this clinic compares to the full study
- **Score trajectories over time** with 95% confidence bands
- **MEQ-4 mystical experience distribution**

---

## 6. Understanding the Output

### Output Tabs in `insights.xlsx`

| Tab | Contents |
|-----|----------|
| **Main Data** | Full wide-format dataset — one row per participant, all scores at all timepoints |
| **Summary** | Key demographics + first/last scores + change from baseline |
| **Demographics** | Sample characteristics |
| **Data Completeness** | Completion rates by questionnaire and timepoint |
| **PHQ9 Summary/Outcomes** | Depression scores, severity, response & remission rates |
| **GAD7 Summary/Outcomes** | Anxiety scores, severity, response & remission rates |
| **WHO5 Summary/Outcomes** | Wellbeing scores over time |
| **MEQ Analysis** | Mystical experience scores and classification |
| **Acute Experience** | EBI, PIQ, CEQ scores from the dosing session |
| **Calculations** | Score definitions, formulas, and methods used |

### Column Naming Convention

Columns follow the pattern: `{measure}_{item_or_total}_{timepoint}`

Examples:
- `phq9_total_bl` — PHQ-9 total score at baseline
- `gad7_3_6mo` — GAD-7 question 3 at 6 months
- `meq4_total_3d` — MEQ-4 total score at 3 days post-treatment

### Timepoint Labels

| Label | When | What's Collected |
|-------|------|-----------------|
| `bl` | Baseline (pre-treatment) | PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C, Expectancy, + others |
| `3d` | 3 days post-treatment | MEQ-4, EBI, CEQ, PIQ (dosing session measures) |
| `1mo` | 1 month | PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C, + others |
| `3mo` | 3 months | PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C, + others |
| `6mo` | 6 months | PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C, + others |
| `12mo` | 12 months | PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C, + others |

---

## 7. How to Make Changes

### Adding a New Questionnaire

1. Open `scripts/integrate.py`
2. Find the `QUESTIONNAIRES` dictionary (around line 66)
3. Add a new entry following the existing pattern:
   ```python
   'new_measure': {
       'items': 10,                    # Number of items
       'item_range': (0, 4),           # Min and max for each item
       'total_range': (0, 40),         # Min and max for total score
       'timepoints': [1, 3, 4, 5, 6], # Which timepoints (1=bl, 2=3d, 3=1mo, 4=3mo, 5=6mo, 6=12mo)
       'scoring': 'sum',              # 'sum', 'mean', 'sum_x4', or 'single'
   },
   ```
4. Run the integration script to verify

### Changing Timepoints for a Questionnaire

1. Open `scripts/integrate.py`
2. Find the questionnaire in the `QUESTIONNAIRES` dictionary
3. Modify its `'timepoints'` list (1=bl, 2=3d, 3=1mo, 4=3mo, 5=6mo, 6=12mo)

### Modifying Report Content

- **Individual reports:** Edit `scripts/generate_individual_report.py`
  - Severity bands are defined near the top of the file (around lines 45-64)
  - The `create_score_chart()` function controls the trajectory plots
  - The `find_notable_item_changes()` function controls which improvements are highlighted
- **Clinic reports:** Edit `scripts/generate_clinic_report.py`
  - `calculate_clinic_metrics()` controls which metrics are computed
  - `create_bar_comparison()` controls the study-wide comparison charts
  - `create_score_trajectory()` controls the trajectory plots with confidence bands

### Changing Report Styling

Both report scripts use PATH Lab brand colors defined at the top of each file. To change colors, modify the color constants (primary blue `#394F79`, dark `#253D6C`, sage `#7E846F`, cream `#FFEFDD`).

### Testing Changes with Sample Data

You can regenerate synthetic test data at any time:
```bash
python scripts/generate_sample_data.py
```

Then run the integration and report scripts against it to verify your changes.

---

## 8. Measures Reference

| Measure | Description | Scoring | Range | Timepoints |
|---------|-------------|---------|-------|------------|
| PHQ-9 | Depression severity | Sum of 9 items (0-3 each) | 0–27 | bl, 1mo, 3mo, 6mo, 12mo |
| GAD-7 | Anxiety severity | Sum of 7 items (0-3 each) | 0–21 | bl, 1mo, 3mo, 6mo, 12mo |
| WHO-5 | Wellbeing index | Sum of 5 items (0-5 each) × 4 | 0–100 | bl, 1mo, 3mo, 6mo, 12mo |
| PsyFlex | Psychological flexibility | Sum of 6 items (1-5 each) | 6–30 | bl, 1mo, 3mo, 6mo, 12mo |
| AUDIT-C | Alcohol use (short) | Sum of 3 items (0-4 each) | 0–12 | bl, 1mo, 3mo, 6mo, 12mo |
| MEQ-4 | Mystical experience | Mean of 4 items (0-5 each) | 0–5 | 3d only |
| EBI | Emotional breakthrough | Sum of 6 items (0-5 each) | 0–30 | 3d only |
| CEQ-7 | Challenging experience | Sum of 7 items (0-5 each) | 0–35 | 3d only |
| PIQ | Psychological insight | Sum of 23 items (1-5 each) | 23–115 | 3d only |
| Expectancy | Treatment expectancy | Single item | 0–10 | bl only |

### Severity Classifications

**PHQ-9:** 0-4 None-minimal, 5-9 Mild, 10-14 Moderate, 15-19 Moderately Severe, 20-27 Severe

**GAD-7:** 0-4 Minimal, 5-9 Mild, 10-14 Moderate, 15-21 Severe

**MEQ-4:** Complete mystical experience ≥ 3.5

---

## 9. Troubleshooting

**"No module named 'pandas'"** — Run `pip install -r requirements.txt`

**Empty output / missing columns** — Make sure your REDCap export includes all instruments and all events. The script expects the raw (not labeled) export format.

**Rescheduled sessions showing as separate rows** — This is expected in the input. The integration script automatically consolidates `_r` timepoint data into the standard columns. Check the `dosing_rescheduled` column in the output to see which participants were affected.

**Report PDF is blank or has missing charts** — Ensure you've run the integration script first so that `data/insights.csv` exists with calculated scores.

---

*PATH Lab — Real World Safety and Effectiveness Study of Psilocybin Therapy*
