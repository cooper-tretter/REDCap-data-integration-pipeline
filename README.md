# REDCap Data Integration Pipeline

Transform messy REDCap exports into clean, analysis-ready datasets for the PATH Lab psychedelic therapy study.

## Directory Structure

```
RWSEStudy/
├── scripts/                    # Main processing scripts
│   ├── integrate.py           # Main integration script
│   └── generate_sample_data.py # Generate synthetic test data
├── data/                       # Data files
│   ├── sample_data.xlsx       # Generated sample data
│   └── data_dictionary_codebook.xlsx  # REDCap codebook
├── documentation/              # Project documentation
├── past_versions/             # Archived previous versions
├── requirements.txt           # Python dependencies
└── README.md                  # This file
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

This creates `insights_[timestamp].xlsx` with multiple analytical tabs.

## Key Features

### Questionnaire-Timepoint Mapping (Per Protocol)

| Questionnaire | Timepoints |
|--------------|------------|
| PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C | t1, t3, t4, t5, t6 (NOT t2) |
| MEQ-4, EBI, CEQ, PIQ | t2 only (dosing session) |
| Expectancy | t1 only (baseline) |

### Rescheduled Dosing Sessions (_r Timepoints)

- `_r` timepoints indicate the dosing session was rescheduled
- Participants either have ALL `_r` timepoints OR ALL standard timepoints
- Data is consolidated: `t2_r` data feeds into `t2` columns
- `dosing_rescheduled` column tracks which participants had rescheduled sessions

### Data Transformation

**Input:** Long-format REDCap export (multiple rows per participant)

**Output:** Wide-format analysis file (one row per participant) with:
- Calculated questionnaire scores
- Severity classifications
- Timepoint-specific columns (e.g., `phq9_total_t1`, `phq9_total_t3`)
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
| PHQ-9 | Depression severity | 0-27 | t1, t3-t6 |
| GAD-7 | Anxiety severity | 0-21 | t1, t3-t6 |
| WHO-5 | Wellbeing index | 0-100 | t1, t3-t6 |
| PsyFlex | Psychological flexibility | 6-30 | t1, t3-t6 |
| AUDIT-C | Alcohol use | 0-12 | t1, t3-t6 |
| MEQ-4 | Mystical experience | 0-5 (mean) | t2 only |
| EBI | Emotional breakthrough | 0-30 | t2 only |
| PIQ | Psychological insight | 9-45 | t2 only |
| CEQ | Challenging experience | 0-35 | t2 only |

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

## Previous Versions

Archived versions are in `past_versions/`. The current version includes:
- Correct questionnaire-timepoint mapping
- `_r` timepoint consolidation
- `dosing_rescheduled` tracking column

---

*PATH Lab - Real World Safety and Effectiveness Study of Psilocybin Therapy*
