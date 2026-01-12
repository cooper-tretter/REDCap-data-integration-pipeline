# REDCap Data Integration Pipeline

Transform messy REDCap exports into clean, analysis-ready datasets for the PATH Lab psychedelic therapy study.

## Directory Structure

```
RWSEStudy/
├── scripts/
│   ├── integrate.py            # Main integration script
│   └── generate_sample_data.py # Generate synthetic test data
├── data/
│   ├── sample_data.xlsx        # Synthetic REDCap export (120 participants, long format)
│   ├── insights.xlsx           # Integration output with 11 analytical tabs
│   ├── insights.csv            # Integration output (main data tab only)
│   └── data_dictionary_codebook.xlsx  # REDCap codebook with all 72 instruments
├── documentation/              # Protocol, data structure reports, meeting notes
├── requirements.txt            # Python dependencies
└── README.md
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Sample Data (Optional)
```bash
python scripts/generate_sample_data.py
```

### 3. Run Integration
```bash
python scripts/integrate.py data/sample_data.xlsx
```

This creates `insights.xlsx` with multiple analytical tabs.

## Key Features

### Timepoint Labels (Per Protocol)

| Label | Timepoint | Description |
|-------|-----------|-------------|
| `bl` | Baseline | Pre-intervention (within 2 weeks before treatment) |
| `3d` | 3 days | Acute (3 days post-treatment) |
| `1mo` | 1 month | Subacute follow-up |
| `3mo` | 3 months | Long-term follow-up |
| `6mo` | 6 months | Long-term follow-up |
| `12mo` | 12 months | Long-term follow-up |

### Questionnaire-Timepoint Mapping

| Questionnaire | Timepoints |
|--------------|------------|
| PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C | bl, 1mo, 3mo, 6mo, 12mo (NOT 3d) |
| MEQ-4, EBI, CEQ, PIQ | 3d only (dosing session) |
| Expectancy | bl only (baseline) |

### Rescheduled Dosing Sessions (_r Timepoints)

- `_r` timepoints in REDCap indicate the dosing session was rescheduled
- Participants either have ALL `_r` timepoints OR ALL standard timepoints
- Data is consolidated into the same output columns (e.g., `_3d`)
- `dosing_rescheduled` column tracks which participants had rescheduled sessions

### Data Transformation

**Input:** Long-format REDCap export (multiple rows per participant)

**Output:** Wide-format analysis file (one row per participant) with:
- Calculated questionnaire scores
- Severity classifications
- Timepoint-specific columns (e.g., `phq9_total_bl`, `phq9_total_1mo`)
- `dosing_rescheduled` flag

### Output Tabs (Excel)

1. **Main Data** - Full wide-format dataset
2. **Summary** - Key demographics + first/last scores + change
3. **Demographics** - Sample characteristics
4. **Data Completeness** - Completion rates by timepoint
5. **PHQ9 Summary/Outcomes** - Depression analysis
6. **GAD7 Summary/Outcomes** - Anxiety analysis
7. **WHO5 Summary/Outcomes** - Wellbeing analysis
8. **MEQ Analysis** - Mystical experience analysis
9. **Acute Experience** - EBI, PIQ, CEQ at dosing
10. **Calculations** - Score definitions and methods

## Measures Included

| Measure | Description | Range | Timepoints |
|---------|-------------|-------|------------|
| PHQ-9 | Depression severity | 0-27 | bl, 1mo, 3mo, 6mo, 12mo |
| GAD-7 | Anxiety severity | 0-21 | bl, 1mo, 3mo, 6mo, 12mo |
| WHO-5 | Wellbeing index | 0-100 | bl, 1mo, 3mo, 6mo, 12mo |
| PsyFlex | Psychological flexibility | 6-30 | bl, 1mo, 3mo, 6mo, 12mo |
| AUDIT-C | Alcohol use | 0-12 | bl, 1mo, 3mo, 6mo, 12mo |
| MEQ-4 | Mystical experience | 0-5 (mean) | 3d only |
| EBI | Emotional breakthrough | 0-30 | 3d only |
| PIQ | Psychological insight | 9-45 | 3d only |
| CEQ | Challenging experience | 0-35 | 3d only |

## Requirements

- Python 3.7+
- pandas >= 1.5.0
- numpy >= 1.21.0
- openpyxl >= 3.0.0

## Usage Examples

### Process Real Data
```bash
python scripts/integrate.py /path/to/redcap_export.xlsx /path/to/output_dir
```

### Specify Output Directory
```bash
python scripts/integrate.py data/sample_data.xlsx ./output
```

## Sample Data Generation

The `generate_sample_data.py` script creates realistic synthetic data with:
- 120 participants with consistent psychological profiles
- 60-70% treatment response rates
- Mystical experiences correlating with outcomes
- 15% with rescheduled dosing sessions (all `_r` timepoints)
- Correct questionnaire-timepoint mapping per protocol

## Documentation

- **Data Dictionary:** `data/data_dictionary_codebook.xlsx`
- **Protocol Details:** `documentation/Protocol.docx`
- **Data Structure Reports:** `documentation/*.md`

---

*PATH Lab - Real World Safety and Effectiveness Study of Psilocybin Therapy*
