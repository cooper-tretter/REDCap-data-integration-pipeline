# REDCap Data Structure Report
## Real World Safety and Effectiveness Study of Psilocybin Therapy

This document provides comprehensive instructions for generating synthetic data that mirrors the structure of the actual REDCap survey data export.

---

## ⚠️ IMPORTANT: Personally Identifiable Information (PII) Fields

### Overview
The following fields contain or may contain participant names and other identifying information. These are critical to identify for:
1. **De-identification** when cleaning real data
2. **Realistic synthetic data generation** (use fake names/emails)
3. **Data consolidation** (one row per participant)

### Direct Name Fields
| Column Name | Field Type | Form | Description |
|-------------|------------|------|-------------|
| `consent_nameprint` | text | informed_consent | Name of Participant (Print) - First consent attempt |
| `consent_nameprint_v2` | text | informed_consent_attempt2 | Name of Participant (Print) - Second consent attempt |
| `consent_nameprint_v3` | text | informed_consent_attempt3 | Name of Participant (Print) - Third consent attempt |

**Sample values observed**: "Silver Liftin", "silver l", "sil", "a", "s" (test data with partial/fake names)

### Signature Fields (Contains Name in Filename)
| Column Name | Field Type | Form | Description |
|-------------|------------|------|-------------|
| `consent_signature` | file (signature) | informed_consent | Signature of Participant - First attempt |
| `consent_signature_v2` | file (signature) | informed_consent_attempt2 | Signature of Participant - Second attempt |
| `consent_signature_v3` | file (signature) | informed_consent_attempt3 | Signature of Participant - Third attempt |

**Format**: `signature_YYYY-MM-DD_HHMM.png` (e.g., "signature_2025-08-30_1636.png")

### Email Fields (Marked as Identifier)
| Column Name | Field Type | Form | Description |
|-------------|------------|------|-------------|
| `email` | text (email) | informed_consent | Participant email for survey links - First attempt |
| `email_v2` | text (email) | informed_consent_attempt2 | Participant email - Second attempt |
| `email_v3` | text (email) | informed_consent_attempt3 | Participant email - Third attempt |

**Sample values observed**: "hopekronman@gmail.com", "lifts380@newschool.edu"

### Free-Text Fields (Potential PII Risk)
These fields accept free text and could potentially contain names or identifying information:

| Column Name | Field Type | Form | Description |
|-------------|------------|------|-------------|
| `other_concern` | text | (various) | Free text for "other" concerns |
| `consent_centerid` | text | informed_consent | Center ID provided by service center |
| Various `_specific` fields | text | (various) | "Please specify" write-in fields |
| Various `writein` fields | text | (various) | Write-in response fields |

### System Identifier
| Column Name | Description |
|-------------|-------------|
| `record_id` | REDCap's internal participant ID (integer) |

### Summary: All PII-Related Columns (9 Primary Fields)
```
consent_nameprint
consent_nameprint_v2
consent_nameprint_v3
consent_signature
consent_signature_v2
consent_signature_v3
email
email_v2
email_v3
```

### De-identification Notes
When consolidating to one row per participant:
1. **Name fields**: Will need to be removed or replaced with synthetic names
2. **Email fields**: Will need to be removed or hashed
3. **Signature files**: References will need to be removed; actual files stored separately need deletion
4. **record_id**: Can be kept as a non-identifying numeric ID, or replaced with a new random ID
5. **Free-text fields**: Should be reviewed for incidental PII mentions

---

## 1. High-Level Data Structure

### 1.1 File Format
- **Format**: CSV (comma-separated values)
- **Encoding**: UTF-8
- **Total columns**: 1,574
- **Column types**: Mix of numeric codes, text, dates, and timestamps

### 1.2 Row Structure (Longitudinal Design)
The study uses a **longitudinal design with multiple events (timepoints)**. Each row represents **one participant at one timepoint**.

**Key principle**: A new row is created for each `(record_id, redcap_event_name)` combination.

Example:
| record_id | redcap_event_name |
|-----------|-------------------|
| 123 | timepoint_1_arm_1 |
| 123 | timepoint_2_arm_1 |
| 123 | timepoint_3_arm_1 |
| 124 | timepoint_1_arm_1 |

A participant who completes 3 timepoints will have 3 rows in the data.

### 1.3 Events (Timepoints)
There are 11 possible events. Each participant may have data in multiple events:

| Event Name | Unique Event Name | Description |
|------------|-------------------|-------------|
| Timepoint 1 | `timepoint_1_arm_1` | Baseline/intake |
| Timepoint 2 | `timepoint_2_arm_1` | Post-dosing (primary) |
| Timepoint 2_R | `timepoint_2_r_arm_1` | Post-dosing (repeat/alternate) |
| Timepoint 3 | `timepoint_3_arm_1` | Follow-up |
| Timepoint 3_R | `timepoint_3_r_arm_1` | Follow-up (repeat) |
| Timepoint 4 | `timepoint_4_arm_1` | Follow-up |
| Timepoint 4_R | `timepoint_4_r_arm_1` | Follow-up (repeat) |
| Timepoint 5 | `timepoint_5_arm_1` | Follow-up |
| Timepoint 5_R | `timepoint_5_r_arm_1` | Follow-up (repeat) |
| Timepoint 6 | `timepoint_6_arm_1` | Final follow-up |
| Timepoint 6_R | `timepoint_6_r_arm_1` | Final follow-up (repeat) |

**Observed patterns in sample data**:
- Most participants have only `timepoint_1_arm_1` (baseline)
- Participants who continue have additional rows for subsequent timepoints
- The "_R" variants appear to be for rescheduled or repeat assessments

---

## 2. Column Structure

### 2.1 System Columns (Always Present)
These columns appear first in every row:

| Column | Description | Example Values |
|--------|-------------|----------------|
| `record_id` | Unique participant identifier | 65, 122, 123 |
| `redcap_event_name` | Event/timepoint identifier | `timepoint_1_arm_1` |
| `redcap_survey_identifier` | Survey response identifier | Usually empty |

### 2.2 Instrument-Based Columns
Columns are grouped by **instrument (form)**. For each instrument:
- `{instrument}_timestamp` - When the form was submitted
- Variable columns from the form
- `{instrument}_complete` - Form completion status

Example for "study_information" instrument:
```
study_information_timestamp, cont_consent, no_consent, study_information_complete
```

### 2.3 Column Naming Conventions

#### Standard Variables
Format: `{variable_name}`
Example: `consent_age`, `consent_psilocybintherapy`

#### Checkbox Variables
Format: `{variable_name}___{option_number}`
Each checkbox option gets its own column with values 0 or 1.

Example for "employ" checkbox with 9 options:
```
employ___1, employ___2, employ___3, employ___4, employ___5, employ___6, employ___7, employ___8, employ___9
```

#### Versioned Variables
Variables that repeat across consent attempts use suffixes:
- `consent_primarypurpose` (first attempt)
- `consent_primarypurpose_v2` (second attempt)
- `consent_primarypurpose_v3` (third attempt)

---

## 3. Data Types and Value Formats

### 3.1 Field Type → Value Mapping

| Field Type | Value Format | Example |
|------------|--------------|---------|
| **text** | Free text string | "John Smith", "a", "hopekronman@gmail.com" |
| **text (email)** | Email address string | "hopekronman@gmail.com" |
| **text (date_mdy)** | Date string M/D/YY | "8/30/25", "9/8/25" |
| **text (number)** | Numeric value | 22, 33, 4 |
| **text (time)** | Time string | (not observed in sample) |
| **yesno** | 0 or 1 | 0=No, 1=Yes |
| **radio** | Integer code matching choice | 1, 2, 3 (see codebook for meaning) |
| **dropdown** | Integer code matching choice | 0, 1, 2 |
| **checkbox** | 0 or 1 per option column | 0=unchecked, 1=checked |
| **slider** | Numeric value (typically 0-100) | 2, 33, 69, 79 |
| **file (signature)** | Filename string | "signature_2025-08-30_1636.png" |
| **descriptive** | No data (display only) | Always empty |
| **calc** | Calculated value | Usually empty in export (calculated server-side) |

### 3.2 Timestamp Format
Format: `M/D/YY H:MM` or `M/D/YY HH:MM`
Examples: "8/30/25 16:32", "9/8/25 9:06"

### 3.3 Date Format
Format: `M/D/YY`
Examples: "8/30/25", "9/21/25", "10/14/25"

### 3.4 Signature File Format
Format: `signature_YYYY-MM-DD_HHMM.png`
Example: "signature_2025-08-30_1636.png"

### 3.5 Form Completion Status
The `{form}_complete` columns use these codes:
- `0` = Incomplete
- `1` = Unverified
- `2` = Complete

---

## 4. Branching Logic (Conditional Fields)

### 4.1 How Branching Works
Many fields only appear when certain conditions are met. When a field's branching condition is NOT met, its value is **empty/null** in the data.

### 4.2 Key Branching Patterns

#### Consent Flow Branching
```
consent_age → If "1" (Yes, 21+):
  └── consent_psilocybintherapy → If "1" (Yes):
        └── All other consent questions become available
        └── If "0" (No): Shows eligibility message, stops
  └── If "0" (No): Shows eligibility message, stops
```

**Example from actual data**:
| consent_age | consent_psilocybintherapy | consent_primarypurpose |
|-------------|---------------------------|------------------------|
| 0 | (empty) | (empty) |
| 1 | 1 | 2 |
| 1 | 1 | 2 |

#### Medication/Supplement Branching
Fields like `thyroid`, `steroid`, `antidepressant_specific` only have values when the corresponding checkbox is selected:
```
med_supps_pre_dosing(6) = "1" → thyroid field appears
med_supps_pre_dosing(7) = "1" → steroid field appears
```

#### Consent Version Branching
If participant fails initial consent questions:
- `informed_consent_attempt2` form appears
- If fails again: `informed_consent_attempt3` form appears

### 4.3 Fill Rate Implications
In sample data:
- ~994 columns have 0% fill in timepoint_1 (not applicable to that event)
- ~322 columns have 1-25% fill (branching-dependent or optional)
- ~234 columns have 100% fill (core required fields)

---

## 5. Event-Specific Data Patterns

### 5.1 Timepoint 1 (Baseline)
**Most data-rich event.** Contains:
- Consent forms (study_information, informed_consent)
- Demographics and eligibility
- All baseline assessments (PHQ-9, GAD-7, WHO-5, etc.)
- Pre-dosing medications/supplements

**Typical non-empty columns**: 250-300

### 5.2 Timepoint 2/2_R (Post-Dosing)
Contains:
- Consent to continue (consent_t2)
- Treatment information (treatment_status, treatment_date)
- Post-dosing assessments
- Side effects inventory

**Typical non-empty columns**: 40-60

### 5.3 Timepoint 3+ (Follow-ups)
Contains:
- Consent to continue
- Follow-up assessments
- Major life events tracking
- Subset of outcome measures

**Typical non-empty columns**: 50-80

---

## 6. Checkbox Field Structure

### 6.1 How Checkboxes Export
Each checkbox question creates **N columns** where N = number of options.

Example: `employ` has 9 options, creating:
- `employ___1` through `employ___9`

### 6.2 Value Encoding
- `0` = Option NOT selected
- `1` = Option selected

**Important**: All checkbox columns in a group typically have a value (0 or 1) when the question is shown. They are all empty when the question is skipped via branching.

### 6.3 Checkbox Groups in This Study
29 checkbox groups identified, including:
- `employ___1` to `employ___9`
- `race1___1` to `race1___N`
- `broad_category___1` to `broad_category___N`
- `med_supps_pre_dosing___1` to `med_supps_pre_dosing___N`
- `types___1` to `types___7`
- `life_events___1` to `life_events___N`
- And others...

---

## 7. Sample Data Generation Rules

### 7.1 Required for Every Row
1. `record_id` - Unique integer per participant
2. `redcap_event_name` - Must be one of the 11 valid event names
3. `redcap_survey_identifier` - Can be empty

### 7.2 Baseline Record Rules (timepoint_1_arm_1)
Every participant needs at least one baseline row with:
1. `study_information_timestamp` - Required
2. `cont_consent` - 1 (yes) to continue
3. `study_information_complete` - 2 (complete)
4. Consent flow fields based on branching logic

### 7.3 Follow-up Record Rules
For timepoint_2+ rows:
1. Only include columns relevant to that event
2. All baseline-only columns should be empty
3. Include event-specific consent (consent_t2, consent_t3, etc.)

### 7.4 Branching Consistency Rules
- If `consent_age = 0`: Leave all downstream consent fields empty
- If `consent_age = 1` AND `consent_psilocybintherapy = 0`: Leave downstream fields empty
- Checkbox fields: Either ALL columns in group have values, or ALL are empty

### 7.5 Value Range Rules
| Field Type | Valid Values |
|------------|--------------|
| yesno | 0, 1 |
| dropdown (_complete) | 0, 1, 2 |
| radio | Depends on choices (typically 0-N) |
| checkbox columns | 0, 1 |
| slider | 0-100 (numeric) |
| text | Any string |
| date | M/D/YY format |
| timestamp | M/D/YY H:MM format |

---

## 8. Multi-Row Participant Example

A participant completing multiple timepoints:

**Row 1** (record_id=126, timepoint_1_arm_1):
```csv
126,timepoint_1_arm_1,,8/30/25 19:10,1,2,8/30/25 19:10,1,1,s,2,1,1,2,1,1,s,signature_2025-08-30_1910.png,8/30/25,email@example.com,2,...[250+ more columns with baseline data]...
```

**Row 2** (record_id=126, timepoint_2_arm_1):
```csv
126,timepoint_2_arm_1,,...[empty baseline columns]...,8/30/25 19:12,1,2,...[timepoint 2 specific data]...
```

**Row 3** (record_id=126, timepoint_2_r_arm_1):
```csv
126,timepoint_2_r_arm_1,,...[different set of columns populated]...
```

---

## 9. Column Order Reference

The full column order follows this pattern:
1. System columns (record_id, redcap_event_name, redcap_survey_identifier)
2. For each instrument (in order from codebook):
   - `{instrument}_timestamp`
   - All variables from that instrument
   - `{instrument}_complete`

The codebook's variable order (#1-1391) corresponds to the column order in the export.

---

## 10. Key Validation Rules for Synthetic Data

### 10.1 Structural Validation
- [ ] Each row has unique (record_id, redcap_event_name) combination
- [ ] All 1,574 columns present in correct order
- [ ] No duplicate column names

### 10.2 Value Validation
- [ ] record_id is positive integer
- [ ] redcap_event_name is one of 11 valid values
- [ ] Numeric fields contain valid numbers or empty
- [ ] Date fields match M/D/YY format
- [ ] Timestamp fields match M/D/YY H:MM format
- [ ] yesno fields are 0, 1, or empty
- [ ] Checkbox fields are 0, 1, or empty (per column)
- [ ] _complete fields are 0, 1, 2, or empty

### 10.3 Branching Logic Validation
- [ ] Downstream fields are empty when branching condition not met
- [ ] All checkbox columns in a group are either all populated or all empty
- [ ] Event-specific fields only populated for correct events

---

## Appendix A: Complete Column List

The full list of 1,574 columns can be extracted from the codebook Excel file. Key column groups:

1. **System columns** (3): record_id, redcap_event_name, redcap_survey_identifier
2. **Timestamp columns** (83): One per instrument
3. **Complete status columns** (83): One per instrument  
4. **Checkbox columns** (215): Multiple per checkbox question
5. **Standard variable columns** (~1,190): All other fields

## Appendix B: Instruments by Event

See the "Instruments" sheet in the codebook for the complete mapping of which instruments appear at which events.

Key patterns:
- **timepoint_1_arm_1 only**: study_information, informed_consent (x3), you_passed, when_is_tx_scheduled, date_calculation, expectancy_measure
- **Multiple timepoints**: PHQ-9, GAD-7, WHO-5, and most assessment instruments
- **Post-dosing only**: Swiss Psychedelic Side Effects Inventory, treatment information forms
