# MASTER DATA STRUCTURE REPORT
## Real World Safety and Effectiveness Study of Psilocybin Therapy

**Date:** November 30, 2025
**Purpose:** Comprehensive documentation of REDCap data structure, analytical findings, and technical specifications

**Sources:**
- Analysis of SkinnyActualExampleData.csv (real pilot data)
- Analysis of data_dictionary_codebook.xlsx (updated codebook)
- Analysis of sample_data.xlsx (synthetic data)
- Integration script behavior analysis

---

## Executive Summary

This report provides complete documentation of the REDCap data structure for the PATH Lab psilocybin therapy study. It combines:
1. **Technical specifications** for generating/validating synthetic data
2. **Analytical findings** from real pilot data (SkinnyActualExampleData)
3. **Integration script behavior** and output structure
4. **Questions and recommendations** for the research team

### Critical Findings:

**✅ Data Structure Verified:**
- 1,574 total columns in long format
- 11 events: 6 standard timepoints + 5 "_R" variants
- timepoint_1_arm_1 is definitively baseline (verified through consent data, baseline-only forms, and demographics)
- Longitudinal design: one row per (participant, timepoint) combination

**⚠️ "_R" Timepoint Meaning Requires Clarification:**
- Appears to mean "repeat/alternate" but no explicit documentation
- Found unusual patterns requiring team input (detailed in Section 10)

**✅ Integration Script Works Correctly:**
- Properly handles all observed patterns
- Creates appropriate output structure (one row per participant)
- No script changes needed

**⚠️ sample_data is Unrealistic:**
- Lacks "_R" timepoints (real data has them)
- No participants without baseline (real data has 1)
- Perfect consent completion (real data: 48%)

---

## Table of Contents

1. [Personally Identifiable Information (PII) Fields](#1-personally-identifiable-information-pii-fields)
2. [High-Level Data Structure](#2-high-level-data-structure)
3. [Technical Specifications](#3-technical-specifications)
4. [Baseline Structure Verification](#4-baseline-structure-verification)
5. [Form-Event Mapping](#5-form-event-mapping)
6. [Event-Specific Data Patterns](#6-event-specific-data-patterns)
7. [Branching Logic](#7-branching-logic)
8. [Checkbox Field Structure](#8-checkbox-field-structure)
9. [Column Structure and Naming](#9-column-structure-and-naming)
10. [Edge Cases and Unusual Patterns](#10-edge-cases-and-unusual-patterns)
11. [Integration Script Behavior](#11-integration-script-behavior)
12. [Output Structure](#12-output-structure)
13. [Validation Rules](#13-validation-rules)
14. [Questions for Research Team](#14-questions-for-research-team)
15. [Recommendations](#15-recommendations)

---

## 1. Personally Identifiable Information (PII) Fields

### 1.1 Overview
The following fields contain or may contain participant names and other identifying information. These are critical to identify for:
1. **De-identification** when cleaning real data
2. **Realistic synthetic data generation** (use fake names/emails)
3. **Data consolidation** (one row per participant)

### 1.2 Direct Name Fields
| Column Name | Field Type | Form | Description |
|-------------|------------|------|-------------|
| `consent_nameprint` | text | informed_consent | Name of Participant (Print) - First consent attempt |
| `consent_nameprint_v2` | text | informed_consent_attempt2 | Name of Participant (Print) - Second consent attempt |
| `consent_nameprint_v3` | text | informed_consent_attempt3 | Name of Participant (Print) - Third consent attempt |

**Sample values observed in SkinnyActualExampleData**: "Silver Liftin", "silver l", "sil", "a", "s", "x" (test data with partial/fake names)

**Note**: In SkinnyActualExampleData, 24/47 (51%) participants have blank `consent_nameprint` at baseline, likely due to failed consent comprehension checks or incomplete test data entries.

### 1.3 Signature Fields (Contains Name in Filename)
| Column Name | Field Type | Form | Description |
|-------------|------------|------|-------------|
| `consent_signature` | file (signature) | informed_consent | Signature of Participant - First attempt |
| `consent_signature_v2` | file (signature) | informed_consent_attempt2 | Signature of Participant - Second attempt |
| `consent_signature_v3` | file (signature) | informed_consent_attempt3 | Signature of Participant - Third attempt |

**Format**: `signature_YYYY-MM-DD_HHMM.png`
**Example**: "signature_2025-08-30_1636.png"

### 1.4 Email Fields (Marked as Identifier)
| Column Name | Field Type | Form | Description |
|-------------|------------|------|-------------|
| `email` | text (email) | informed_consent | Participant email for survey links - First attempt |
| `email_v2` | text (email) | informed_consent_attempt2 | Participant email - Second attempt |
| `email_v3` | text (email) | informed_consent_attempt3 | Participant email - Third attempt |

**Sample values observed**: "hopekronman@gmail.com", "lifts380@newschool.edu"

### 1.5 Free-Text Fields (Potential PII Risk)
These fields accept free text and could potentially contain names or identifying information:

| Column Name | Field Type | Form | Description |
|-------------|------------|------|-------------|
| `other_concern` | text | (various) | Free text for "other" concerns |
| `consent_centerid` | text | informed_consent | Center ID provided by service center |
| Various `_specific` fields | text | (various) | "Please specify" write-in fields |
| Various `writein` fields | text | (various) | Write-in response fields |

### 1.6 System Identifier
| Column Name | Description |
|-------------|-------------|
| `record_id` | REDCap's internal participant ID (integer) |

### 1.7 Summary: All PII-Related Columns (9 Primary Fields)
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

### 1.8 De-identification Recommendations
When consolidating to one row per participant:
1. **Name fields**: Remove or replace with synthetic names
2. **Email fields**: Remove or hash
3. **Signature files**: Remove references; delete actual files stored separately
4. **record_id**: Can be kept as non-identifying numeric ID, or replaced with new random ID
5. **Free-text fields**: Review for incidental PII mentions

---

## 2. High-Level Data Structure

### 2.1 File Format
- **Format**: CSV (comma-separated values) or Excel (.xlsx)
- **Encoding**: UTF-8
- **Total columns**: 1,574
- **Column types**: Mix of numeric codes, text, dates, timestamps, and file references

### 2.2 Row Structure (Longitudinal Design)
The study uses a **longitudinal design with multiple events (timepoints)**. Each row represents **one participant at one timepoint**.

**Key principle**: A new row is created for each `(record_id, redcap_event_name)` combination.

**Example from SkinnyActualExampleData:**
```
Participant 126 has 4 rows:
- (126, timepoint_1_arm_1)      ← Baseline
- (126, timepoint_2_arm_1)      ← Standard dosing visit
- (126, timepoint_2_r_arm_1)    ← Repeat dosing visit (unusual!)
- (126, timepoint_3_r_arm_1)    ← Repeat follow-up
```

### 2.3 Events (Timepoints)
There are **11 possible events**. Each participant may have data in multiple events:

| Event Name | Unique Event Name | Description | Observed in SkinnyActual |
|------------|-------------------|-------------|--------------------------|
| Timepoint 1 | `timepoint_1_arm_1` | Baseline/intake | 47/48 participants (98%) |
| Timepoint 2 | `timepoint_2_arm_1` | Post-dosing (primary) | 6 participants (13%) |
| Timepoint 2_R | `timepoint_2_r_arm_1` | Post-dosing (repeat) | 1 participant (2%) |
| Timepoint 3 | `timepoint_3_arm_1` | Follow-up | 2 participants (4%) |
| Timepoint 3_R | `timepoint_3_r_arm_1` | Follow-up (repeat) | 1 participant (2%) |
| Timepoint 4 | `timepoint_4_arm_1` | Follow-up | 0 participants |
| Timepoint 4_R | `timepoint_4_r_arm_1` | Follow-up (repeat) | 1 participant (2%) |
| Timepoint 5 | `timepoint_5_arm_1` | Follow-up | 0 participants |
| Timepoint 5_R | `timepoint_5_r_arm_1` | Follow-up (repeat) | 1 participant (2%) |
| Timepoint 6 | `timepoint_6_arm_1` | Final follow-up | 0 participants |
| Timepoint 6_R | `timepoint_6_r_arm_1` | Final follow-up (repeat) | 0 participants |

**Critical Note**: "_R" meaning is not explicitly documented in the codebook. Appears to mean "repeat/alternate" based on naming convention, but requires clarification from research team.

---

## 3. Technical Specifications

### 3.1 System Columns (Always Present)
These columns appear first in every row:

| Column | Description | Example Values | Notes |
|--------|-------------|----------------|-------|
| `record_id` | Unique participant identifier | 65, 122, 123, 126 | Integer, unique per participant |
| `redcap_event_name` | Event/timepoint identifier | `timepoint_1_arm_1` | Must be one of 11 valid event names |
| `redcap_survey_identifier` | Survey response identifier | Usually empty | Optional tracking field |

### 3.2 Data Types and Value Formats

| Field Type | Value Format | Example | Notes |
|------------|--------------|---------|-------|
| **text** | Free text string | "John Smith", "a" | Any string |
| **text (email)** | Email address | "user@example.com" | Valid email format |
| **text (date_mdy)** | Date string M/D/YY | "8/30/25", "9/8/25" | Month/Day/2-digit year |
| **text (number)** | Numeric value | 22, 33, 4 | Integer or decimal |
| **text (time)** | Time string | "14:30" | HH:MM format |
| **yesno** | 0 or 1 | 0=No, 1=Yes | Binary choice |
| **radio** | Integer code | 1, 2, 3 | See codebook for meaning |
| **dropdown** | Integer code | 0, 1, 2 | See codebook for meaning |
| **checkbox** | 0 or 1 per option | 0=unchecked, 1=checked | Multiple columns per question |
| **slider** | Numeric value | 2, 33, 69, 79 | Typically 0-100 range |
| **file (signature)** | Filename string | "signature_2025-08-30_1636.png" | PNG file reference |
| **descriptive** | No data | Always empty | Display only, no data stored |
| **calc** | Calculated value | Usually empty | Server-side calculation |

### 3.3 Timestamp Format
**Format**: `M/D/YY H:MM` or `M/D/YY HH:MM`
**Examples**: "8/30/25 16:32", "9/8/25 9:06"
**Used for**: All `{instrument}_timestamp` columns

### 3.4 Date Format
**Format**: `M/D/YY`
**Examples**: "8/30/25", "9/21/25", "10/14/25"
**Used for**: Date fields like `consent_date`, `treatment_date`

### 3.5 Signature File Format
**Format**: `signature_YYYY-MM-DD_HHMM.png`
**Example**: "signature_2025-08-30_1636.png"
**Note**: Actual signature image stored separately; only filename appears in CSV

### 3.6 Form Completion Status
The `{form}_complete` columns use standardized codes:
- `0` = Incomplete
- `1` = Unverified
- `2` = Complete

**Example columns**: `study_information_complete`, `phq9_complete`, `gad7_complete`

---

## 4. Baseline Structure Verification

### 4.1 Evidence that timepoint_1_arm_1 IS Baseline

Multiple independent sources confirm timepoint_1_arm_1 is the baseline/entry point:

#### A. Consent Data (Definitive Proof)
```
Analysis of SkinnyActualExampleData consent fields:

consent_nameprint at timepoint_1_arm_1:   23 entries (49%)
consent_nameprint at other timepoints:     0 entries (0%)

consent_consent at timepoint_1_arm_1:      23 entries
consent_consent at other timepoints:        0 entries

consent_date at timepoint_1_arm_1:         23 entries
consent_date at other timepoints:           0 entries

Conclusion: Participants can ONLY legally enter the study at timepoint_1_arm_1.
```

#### B. Baseline-Only Forms (From Codebook Instruments Sheet)

**8 forms ONLY available at timepoint_1_arm_1:**

| Form Name | Participants with Data |
|-----------|------------------------|
| study_information | 47/48 (98%) |
| informed_consent (attempt 1) | 47/48 (98%) |
| informed_consent_attempt2 | 47/48 (98%) |
| informed_consent_attempt3 | 47/48 (98%) |
| expectancy_measure | 47/48 (98%) |
| date_calculation | 47/48 (98%) |
| when_is_tx_scheduled | 47/48 (98%) |
| medssupps_predosing | 47/48 (98%) |

**Note**: These forms physically cannot be completed at any other timepoint - they're not assigned to other events in the codebook.

#### C. Demographics Pattern
```
demographic_survey at timepoint_1_arm_1:   47/48 participants (98%)
demographic_survey at other timepoints:     0 participants (0%)

Exception: Participant 65 has NO timepoint_1_arm_1 row at all.
```

**VERDICT**: timepoint_1_arm_1 is unequivocally the baseline/entry point for the study.

---

## 5. Form-Event Mapping

### 5.1 Complete Form Assignment Analysis

From codebook Instruments sheet: **72 total forms/instruments** assigned to specific events.

### 5.2 Pattern A: Baseline Only (8 forms)

**Available ONLY at timepoint_1_arm_1:**
```
Form                          | Purpose
------------------------------|------------------------------------------
study_information             | Initial consent screen
informed_consent (3 versions) | Consent with comprehension checks (allows 3 attempts)
you_passed                    | Confirmation of consent completion
expectancy_measure            | Pre-treatment expectations
date_calculation              | Scheduling calculations
when_is_tx_scheduled          | Treatment date tracking
medssupps_predosing          | Pre-treatment medications/supplements
demographic_survey            | Age, gender, education, employment
treatment_preference          | Treatment setting preferences
```

**Interpretation**: These are collected once at study entry and never repeated.

---

### 5.3 Pattern B: Dosing Session Only (6 forms)

**Available ONLY at timepoint_2_arm_1 and timepoint_2_r_arm_1:**

| Form | Acronym | Purpose |
|------|---------|---------|
| Mystical Experience Questionnaire | MEQ-4 | Mystical/transcendent experiences during session |
| State Self-Compassion Scale | SSCS-S | Self-compassion during dosing |
| Metacognitive Processes of Decentering | MPoD-S | Perceptual shifts and decentering |
| Emotional Breakthrough Inventory | EBI | Emotional breakthrough intensity |
| Challenging Experience Questionnaire | CEQ-7 | Difficult/challenging experiences |
| Psychological Insight Questionnaire | PIQ | Quality and depth of insights |

**Interpretation**: These capture the acute psychedelic experience during/immediately after dosing. Only relevant at the treatment timepoint.

**Critical Finding**: One form differs between standard and "_R":
- **"Tx information_timepoint 2"**: Available at timepoint_2_arm_1 but NOT at timepoint_2_r_arm_1
- All other dosing session forms are available at BOTH t2 and t2_r

---

### 5.4 Pattern C: Repeated Outcome Measures (58 forms)

**Available at MULTIPLE timepoints** (t1, t3-t6 and corresponding "_R" variants):

**Core outcome measures (included in integration script):**
- PHQ-9 (Depression - 9 items)
- GAD-7 (Anxiety - 7 items)
- WHO-5 (Wellbeing - 5 items)
- PsyFlex (Psychological Flexibility - 6 items)
- AUDIT-C (Alcohol Use - 3 items)

**Additional clinical measures (~53 more instruments):**
- BFI-44 (Big Five Inventory - personality)
- FFMQ (Five Facet Mindfulness Questionnaire)
- MAIA-2 (Multidimensional Assessment of Interoceptive Awareness)
- PANAS (Positive and Negative Affect Schedule)
- RRQ (Rumination-Reflection Questionnaire)
- And ~48 more clinical/personality measures

**Interpretation**: These track outcomes longitudinally over time to assess treatment effects.

---

## 6. Event-Specific Data Patterns

### 6.1 Timepoint 1 (Baseline) - Most Data-Rich Event

**Contains:**
- Consent forms (3 attempts possible)
- Demographics and eligibility screening
- ALL baseline assessments (PHQ-9, GAD-7, WHO-5, etc.)
- Pre-dosing medications/supplements
- Treatment expectations and preferences

**Typical non-empty columns**: 250-300 out of 1,574

**Observed in SkinnyActualExampleData:**
- 47/48 participants have timepoint_1_arm_1 data
- Data completeness highly variable (test data)
- 23/47 (49%) completed consent fully (have names)
- 24/47 (51%) have blank consent (likely failed comprehension checks or incomplete entries)

---

### 6.2 Timepoint 2/2_R (Post-Dosing)

**Contains:**
- Consent to continue (consent_t2)
- Treatment information (status, date, setting)
- Acute experience measures (MEQ, EBI, CEQ, PIQ, SSCS-S, MPoD-S)
- Post-dosing side effects inventory
- Some outcome measures (PHQ-9, GAD-7, etc. if administered)

**Typical non-empty columns**: 40-60

**Observed in SkinnyActualExampleData:**
- timepoint_2_arm_1: 6 participants
- timepoint_2_r_arm_1: 1 participant (unusual - why "_R"?)
- Very sparse data (pilot testing)

---

### 6.3 Timepoint 3+ (Follow-ups)

**Contains:**
- Consent to continue
- Follow-up assessments (PHQ-9, GAD-7, WHO-5, etc.)
- Major life events tracking
- Subset of outcome measures
- Continued monitoring

**Typical non-empty columns**: 50-80

**Observed in SkinnyActualExampleData:**
- timepoint_3_arm_1: 2 participants
- timepoint_3_r_arm_1: 1 participant
- timepoint_4_r_arm_1: 1 participant (Participant 65 - no baseline!)
- timepoint_5_r_arm_1: 1 participant (Participant 65 again)
- Very low follow-up rates (early pilot data)

---

## 7. Branching Logic

### 7.1 Overview
**364 out of 1,391 variables (26.2%)** have branching logic that controls when fields are displayed.

**How it works**: When a field's branching condition is NOT met, its value is **empty/null** in the data export.

### 7.2 CRITICAL Finding: Outcome Measures Have NO Branching Logic

```
Measures with NO branching logic (ALWAYS shown when form is opened):

✓ PHQ-9: All 9 items always displayed
✓ GAD-7: All 7 items always displayed
✓ WHO-5: All 5 items always displayed
✓ MEQ-4: All items/subscales always displayed
✓ PsyFlex: All 6 items always displayed
✓ AUDIT-C: All 3 items always displayed
```

**Implication**: Missing data in these outcome measures represents **true missingness** (participant chose not to answer), NOT fields hidden by branching logic. This is critical for statistical analysis.

---

### 7.3 Consent Flow Branching (Most Complex)

#### Comprehension Check Structure:
```
consent_age → If "1" (Yes, 21+):
  └── consent_psilocybintherapy → If "1" (Yes, willing):
        └── consent_primarypurpose (comprehension question)
        └── consent_involvement (comprehension question)
        └── consent_emotionaldiscomfort (comprehension question)
        └── consent_services (comprehension question)
        └── consent_participation (comprehension question)
              └── If ALL answered CORRECTLY:
                    └── consent_consent (final consent checkbox)
                    └── consent_nameprint (name field appears)
                    └── consent_signature (signature field appears)
                    └── consent_date (date field appears)
```

#### Branching Logic for Name Field:
```
consent_nameprint only shows if:
  [consent_age]="1" AND
  [consent_psilocybintherapy]="1" AND
  [consent_primarypurpose] = "2" AND         ← Must answer correctly
  [consent_involvement] = "1" AND             ← Must answer correctly
  [consent_emotionaldiscomfort] = "1" AND     ← Must answer correctly
  [consent_services] = "2" AND                ← Must answer correctly
  [consent_participation] = "1"               ← Must answer correctly
```

**This explains why 24/47 participants in SkinnyActualExampleData have blank names:**
- Failed one or more comprehension questions
- OR started consent but didn't complete it
- OR test data where researchers were checking the system

---

### 7.4 Multiple Consent Attempts
The study allows **THREE consent attempts** if participants fail comprehension checks:

**Attempt 1**: informed_consent form
- Variables: `consent_age`, `consent_nameprint`, etc.

**Attempt 2**: informed_consent_attempt2 form
- Variables: `consent_age_v2`, `consent_nameprint_v2`, etc.

**Attempt 3**: informed_consent_attempt3 form
- Variables: `consent_age_v3`, `consent_nameprint_v3`, etc.

**Implication**: When looking for participant names, may need to check all three versions (`consent_nameprint`, `consent_nameprint_v2`, `consent_nameprint_v3`).

---

### 7.5 Other Branching Patterns

#### Medication/Supplement Follow-ups:
```
med_supps_pre_dosing___6 = "1" → thyroid field appears
med_supps_pre_dosing___7 = "1" → steroid field appears
med_supps_pre_dosing___8 = "1" → antidepressant_specific field appears
```

#### "If Yes, Explain" Follow-ups:
Many fields have free-text follow-ups that only appear if a certain response is selected:
```
life_events___3 = "1" → life_events_3_specific appears
adverse_event = "1" → adverse_event_description appears
```

---

### 7.6 Fill Rate Implications

**From column analysis of sample data:**
- ~994 columns (63%): 0% fill at timepoint_1 (event-specific, not applicable to baseline)
- ~322 columns (20%): 1-25% fill (branching-dependent or optional fields)
- ~234 columns (15%): 100% fill (core required fields)
- ~24 columns (2%): Variable fill rates

**Interpretation**: Most columns will be empty for most participants at any given timepoint. This is by design due to:
1. Event-specific forms (baseline forms don't appear at follow-up, etc.)
2. Branching logic (fields only shown when conditions met)
3. Optional vs required fields

---

## 8. Checkbox Field Structure

### 8.1 How Checkboxes Export
Each checkbox question creates **N columns** where N = number of options.

**Example**: `employ` (employment status) has 9 options:
```
employ___1   (Full-time employed)
employ___2   (Part-time employed)
employ___3   (Self-employed)
employ___4   (Student)
employ___5   (Homemaker)
employ___6   (Retired)
employ___7   (Unemployed)
employ___8   (Unable to work)
employ___9   (Other)
```

### 8.2 Value Encoding
- `0` = Option NOT selected
- `1` = Option selected

**Important**: All checkbox columns in a group typically have a value (0 or 1) when the question is shown. They are ALL empty when the question is skipped via branching logic.

### 8.3 Checkbox Groups in This Study (29 Total)

**Major checkbox groups:**
```
employ___1 to employ___9                     (Employment - 9 options)
race1___1 to race1___N                       (Race/ethnicity - multiple options)
broad_category___1 to broad_category___N     (Substance categories)
med_supps_pre_dosing___1 to med_supps_pre_dosing___N  (Medications/supplements)
types___1 to types___7                       (Types of something - 7 options)
life_events___1 to life_events___N           (Major life events)
[24 more checkbox groups...]
```

**Total checkbox columns**: ~215 out of 1,574 (14%)

### 8.4 Validation Rule for Checkboxes
In valid data: Either ALL columns in a checkbox group have values (mix of 0s and 1s), OR ALL columns in the group are empty (question not shown/answered).

**Invalid pattern**: Some columns in group have values, others are empty
**Valid pattern 1**: employ___1=1, employ___2=0, employ___3=0, ..., employ___9=0
**Valid pattern 2**: employ___1=(empty), employ___2=(empty), ..., employ___9=(empty)

---

## 9. Column Structure and Naming

### 9.1 Column Order Pattern
The full column order follows this structure:

**1. System columns (3 columns):**
```
record_id
redcap_event_name
redcap_survey_identifier
```

**2. For each instrument (72 instruments):**
```
{instrument}_timestamp
{variable_1}
{variable_2}
...
{variable_N}
{instrument}_complete
```

**Column count breakdown:**
- 3 system columns
- 83 timestamp columns (one per instrument, some instruments at multiple timepoints)
- 83 complete status columns (one per instrument)
- 215 checkbox columns (multiple per checkbox question)
- ~1,190 standard variable columns

**Total**: 1,574 columns

---

### 9.2 Naming Conventions

#### Standard Variables:
**Format**: `{variable_name}`
**Examples**: `consent_age`, `phq9_1`, `gad7_total`

#### Checkbox Variables:
**Format**: `{variable_name}___{option_number}`
**Examples**: `employ___1`, `race1___2`, `med_supps_pre_dosing___8`

**Note**: Three underscores separate variable name from option number.

#### Versioned Variables (Multiple Consent Attempts):
**Format**: `{variable_name}` or `{variable_name}_v2` or `{variable_name}_v3`
**Examples**:
- First attempt: `consent_primarypurpose`
- Second attempt: `consent_primarypurpose_v2`
- Third attempt: `consent_primarypurpose_v3`

#### Timestamp Columns:
**Format**: `{instrument}_timestamp`
**Examples**: `study_information_timestamp`, `phq9_timestamp`, `gad7_timestamp`

#### Completion Status Columns:
**Format**: `{instrument}_complete`
**Examples**: `study_information_complete`, `phq9_complete`, `gad7_complete`
**Values**: 0 (Incomplete), 1 (Unverified), 2 (Complete)

---

## 10. Edge Cases and Unusual Patterns

### 10.1 Edge Case 1: Participant Without Baseline (Participant 65)

**Data Present:**
```
record_id: 65
Rows: 2
Timepoints: timepoint_4_r_arm_1, timepoint_5_r_arm_1
```

**Data ABSENT:**
```
NO timepoint_1_arm_1 row
NO consent data (consent_nameprint, consent_consent, consent_date)
NO demographics (age, gender, education)
NO baseline clinical measures
```

**Output in wide format:**
```
record_id | name | age | gender | education | phq9_total_t4_r | phq9_total_t5_r
65        | NaN  | NaN | NaN    | NaN       | [score if avail]| [score if avail]
```

**Questions for team:**
1. Can participants enter the study mid-way without baseline?
2. Is this late enrollment scenario?
3. Is baseline data recorded elsewhere?
4. Should this participant be excluded from analysis?

---

### 10.2 Edge Case 2: Participant with BOTH Standard AND "_R" at Same Timepoint (Participant 126)

**Timepoints Present:**
```
record_id: 126
Row 1: timepoint_1_arm_1        (baseline)
Row 2: timepoint_2_arm_1        (standard dosing visit)
Row 3: timepoint_2_r_arm_1      (repeat dosing visit)
Row 4: timepoint_3_r_arm_1      (repeat follow-up)
```

**Unusual**: Has BOTH timepoint_2_arm_1 AND timepoint_2_r_arm_1

**Output in wide format:**
```
record_id | name | phq9_total_t1 | phq9_total_t2 | phq9_total_t2_r | phq9_total_t3_r
126       | "s"  | [baseline]    | [score at t2] | [score at t2_r] | [score at t3_r]
```

**Possible explanations:**
1. Data quality redo (completed t2, had issues, redid as t2_r)
2. Protocol allows both for validation/reliability
3. Data entry error
4. Testing different versions of forms

**Questions for team:**
1. Is this expected behavior?
2. Should both be included in synthetic data?
3. For analysis, which should be prioritized?
4. How common is this pattern?

---

### 10.3 Edge Case 3: Blank Names Despite Having Baseline (24 participants)

**Pattern:**
```
Has timepoint_1_arm_1 row: YES
Has some data at baseline: YES (e.g., age, timestamps)
consent_nameprint value: BLANK/NaN
```

**Example - Participant 122:**
```
record_id: 122
redcap_event_name: timepoint_1_arm_1
consent_nameprint: (blank)
age: 25
gender: Male (coded as numeric)
study_information_timestamp: 8/30/25 16:32
study_information_complete: 2 (Complete)
```

**Cause (from branching logic analysis):**
- Failed consent comprehension check → `consent_nameprint` field never appeared
- OR started consent process but didn't finish
- OR test/pilot data where consent wasn't fully completed

**Prevalence in SkinnyActualExampleData**: 24/47 (51%) of participants with baseline

**Implication**: This is likely a **data quality issue from pilot testing**, not a structural problem with the integration script. Real study data should have complete consent for all enrolled participants.

**Current integration script behavior**: Preserves blank as NaN (correct - maintains data integrity)

---

### 10.4 Summary of Edge Cases

| Pattern | Count | Baseline? | Demographics? | Issue |
|---------|-------|-----------|---------------|-------|
| Normal | 22/48 | Yes | Yes | None |
| Blank name | 24/48 | Yes | Partial | Failed consent comprehension |
| No baseline | 1/48 | No | No | Late entry or data error |
| Both standard & "_R" | 1/48 | Yes | Yes | Unknown reason |

---

## 11. Integration Script Behavior

### 11.1 Current Script Processing Steps

#### Step 1: Identify Unique Participants
```python
participant_col = 'participant_id' or 'record_id'  # Auto-detect
unique_participants = df[participant_col].unique()
```

#### Step 2: Extract Baseline Data
```python
df_baseline = df[df['redcap_event_name'] == 'timepoint_1_arm_1']

For each participant:
    name = consent_nameprint at timepoint_1_arm_1
    age = age at timepoint_1_arm_1
    gender = gender at timepoint_1_arm_1
    education = education at timepoint_1_arm_1

    If timepoint_1_arm_1 doesn't exist for participant:
        → All demographics = NaN

    If timepoint_1_arm_1 exists but fields are blank:
        → Preserve blank as NaN (maintains data integrity)
```

**Handles Edge Cases:**
- ✅ Participant 65 (no t1): Demographics = NaN
- ✅ 24 participants with blank names: Name = NaN

---

#### Step 3: Detect Timepoints and Pivot to Wide Format
```python
# Detect all timepoints present in data
unique_timepoints = df['redcap_event_name'].unique()

# Map to short codes using TIMEPOINT_MAP:
TIMEPOINT_MAP = {
    'timepoint_1_arm_1': 't1',
    'timepoint_2_arm_1': 't2',
    'timepoint_2_r_arm_1': 't2_r',    # Repeat timepoint
    'timepoint_3_arm_1': 't3',
    'timepoint_3_r_arm_1': 't3_r',    # Repeat timepoint
    'timepoint_4_arm_1': 't4',
    'timepoint_4_r_arm_1': 't4_r',
    'timepoint_5_arm_1': 't5',
    'timepoint_5_r_arm_1': 't5_r',
    'timepoint_6_arm_1': 't6',
    'timepoint_6_r_arm_1': 't6_r'
}

# Create columns for each (variable, timepoint) combination
For each variable (e.g., phq9_1):
    For each timepoint in data (e.g., t1, t2, t2_r, t3):
        Create column: phq9_1_t1, phq9_1_t2, phq9_1_t2_r, phq9_1_t3
```

**Example with SkinnyActualExampleData:**
```
Timepoints detected: t1, t2, t2_r, t3, t3_r, t4_r, t5_r

phq9_1 becomes 7 columns:
- phq9_1_t1
- phq9_1_t2
- phq9_1_t2_r     ← Extra column for repeat
- phq9_1_t3
- phq9_1_t3_r     ← Extra column for repeat
- phq9_1_t4_r     ← Only "_R" exists (no standard t4 in data)
- phq9_1_t5_r     ← Only "_R" exists (no standard t5 in data)
```

---

#### Step 4: Calculate Composite Scores
```python
For each timepoint where items are present:
    # PHQ-9 (Depression)
    if all items present (phq9_1 through phq9_9):
        phq9_total = sum(phq9_1 through phq9_9)
    else:
        phq9_total = NaN

    # GAD-7 (Anxiety)
    if all items present (gad7_1 through gad7_7):
        gad7_total = sum(gad7_1 through gad7_7)
    else:
        gad7_total = NaN

    # WHO-5 (Wellbeing)
    if all items present (who5_1 through who5_5):
        who5_total = sum(who5_1 through who5_5) * 4  # Scale to 0-100
    else:
        who5_total = NaN

    # Similar for MEQ-4, PsyFlex, AUDIT-C
```

**Missing data handling**: Requires ALL items to be present. If any item is NaN, total score = NaN.

---

#### Step 5: Create Output Structure
**One row per participant** with columns:
```
Demographics (from t1):
- record_id
- name
- age
- gender
- education

Individual items × timepoints:
- phq9_1_t1, phq9_1_t2, phq9_1_t2_r, phq9_1_t3, ...
- phq9_2_t1, phq9_2_t2, phq9_2_t2_r, phq9_2_t3, ...
- gad7_1_t1, gad7_1_t2, gad7_1_t2_r, gad7_1_t3, ...

Computed scores × timepoints:
- phq9_total_t1, phq9_total_t2, phq9_total_t2_r, phq9_total_t3, ...
- gad7_total_t1, gad7_total_t2, gad7_total_t2_r, gad7_total_t3, ...
- who5_total_t1, who5_total_t2, who5_total_t2_r, who5_total_t3, ...

[Continue for all measures and timepoints]
```

---

### 11.2 What the Script Correctly Handles

✅ **Variable numbers of timepoints per participant**
- Participant with only t1: Gets columns for all timepoints, most are NaN
- Participant with t1, t2, t3: Data fills appropriate columns

✅ **Missing baseline (Participant 65)**
- Demographics = NaN
- Can still have data at later timepoints (t4_r, t5_r)

✅ **Blank names in source data**
- Preserved as NaN
- Maintains data integrity (doesn't make up values)

✅ **Repeat ("_R") timepoints**
- Creates separate columns for standard and "_R"
- Example: Both `phq9_total_t2` and `phq9_total_t2_r` columns exist

✅ **Both standard and "_R" at same timepoint (Participant 126)**
- Both values preserved in separate columns
- Allows analyst to decide how to handle

✅ **Missing data in outcome measures**
- Preserved as NaN
- Indicates participant didn't complete measure or items missing

---

### 11.3 Script Does NOT Need Modification

The current integration script correctly handles ALL observed patterns:
- Edge cases (no baseline, blank names)
- Repeat timepoints
- Missing data
- Variable longitudinal coverage

**No changes needed** unless:
1. Want to add data quality reporting (flag edge cases)
2. Want to search multiple timepoints for names (enhancement, not fix)
3. Want to handle multiple consent attempt versions (v2, v3)

---

## 12. Output Structure

### 12.1 SkinnyActualExampleData Output

**Input (long format):**
```
59 rows (multiple rows per participant)
48 unique participants
1,574 columns
Timepoints present: t1, t2, t2_r, t3, t3_r, t4_r, t5_r
```

**Output (wide format):**
```
48 rows (one row per participant)
388 columns

Column structure:
- 5 demographic columns:
  - record_id
  - name (24/48 are NaN due to blank consent)
  - age
  - gender
  - education

- 383 time-varying columns:
  - Variables ending in: _t1, _t2, _t2_r, _t3, _t3_r, _t4_r, _t5_r
  - Example: phq9_1_t1, phq9_1_t2, phq9_1_t2_r, phq9_1_t3, phq9_1_t3_r, phq9_1_t4_r, phq9_1_t5_r
  - Example: phq9_total_t1, phq9_total_t2, phq9_total_t2_r, phq9_total_t3, phq9_total_t3_r, phq9_total_t4_r, phq9_total_t5_r
```

**Why 388 columns**: Has "_R" timepoint columns (t2_r, t3_r, t4_r, t5_r) that sample_data doesn't have.

---

### 12.2 sample_data Output

**Input (long format):**
```
532 rows (multiple rows per participant)
120 unique participants
1,574 columns (same structure as SkinnyActual)
Timepoints present: t1, t2, t3, t4, t5, t6 (NO "_R" timepoints)
```

**Output (wide format):**
```
120 rows (one row per participant)
335 columns

Column structure:
- 5 demographic columns (same as above)

- 330 time-varying columns:
  - Variables ending in: _t1, _t2, _t3, _t4, _t5, _t6
  - NO "_R" columns (sample_data lacks repeat timepoints)
  - Example: phq9_1_t1, phq9_1_t2, phq9_1_t3, phq9_1_t4, phq9_1_t5, phq9_1_t6
```

**Why 335 columns**: Has standard t4, t5, t6 but NO "_R" timepoints.

---

### 12.3 Why Column Counts Differ

**SkinnyActual has MORE columns (388 vs 335):**
- Reason: Has 7 timepoint suffixes vs 6
- SkinnyActual: _t1, _t2, _t2_r, _t3, _t3_r, _t4_r, _t5_r (7 timepoints)
- sample_data: _t1, _t2, _t3, _t4, _t5, _t6 (6 timepoints)

**This is CORRECT behavior**: The script creates columns for whatever timepoints exist in the input data.

**53 column difference** = Variables × (extra "_R" timepoints - missing standard timepoints)

---

### 12.4 Data Completeness Comparison

| Metric | SkinnyActualExampleData | sample_data |
|--------|-------------------------|-------------|
| **Participants** | 48 | 120 |
| **Avg timepoints per participant** | 1.2 | 4.4 |
| **Baseline completion** | 47/48 (98%) | 120/120 (100%) |
| **Name completion** | 23/47 (49%) | 120/120 (100%) |
| **PHQ-9 at baseline** | 3/48 (6%) | 104/120 (87%) |
| **GAD-7 at baseline** | 2/48 (4%) | 93/120 (78%) |
| **WHO-5 at baseline** | 2/48 (4%) | 89/120 (74%) |
| **Follow-up data** | Very sparse | Rich (65-73% per timepoint) |
| **Has "_R" timepoints** | Yes (5 "_R" rows) | No |
| **Has edge cases** | Yes (Participant 65, 126) | No |

**Conclusion**: SkinnyActualExampleData is early pilot/test data with low completion rates. sample_data is complete synthetic data but lacks real-world patterns like "_R" timepoints.

---

## 13. Validation Rules

### 13.1 Structural Validation (Long Format Input)

For valid REDCap export:

- [ ] Each row has unique (record_id, redcap_event_name) combination
- [ ] All 1,574 columns present
- [ ] Columns in correct order (system columns first, then instruments)
- [ ] No duplicate column names
- [ ] record_id column exists and has values
- [ ] redcap_event_name column exists and has values

---

### 13.2 Value Validation

| Field Type | Valid Values | Invalid Examples |
|------------|--------------|------------------|
| record_id | Positive integer | Negative, decimal, text, empty |
| redcap_event_name | One of 11 event names | Typos, other values |
| yesno fields | 0, 1, or empty | 2, -1, text |
| _complete fields | 0, 1, 2, or empty | 3, -1, text |
| checkbox columns | 0, 1, or empty | 2, -1, text |
| date fields | M/D/YY format or empty | Wrong format, invalid dates |
| timestamp fields | M/D/YY H:MM or empty | Wrong format |
| text (number) | Numeric or empty | Non-numeric text |
| text (email) | Valid email or empty | Invalid email format |

---

### 13.3 Branching Logic Validation

For realistic/valid data:

- [ ] Downstream fields are empty when branching condition NOT met
  - Example: If `consent_age=0`, then `consent_psilocybintherapy` should be empty

- [ ] Downstream fields have values when branching condition IS met
  - Example: If `consent_age=1` AND `consent_psilocybintherapy=1`, then comprehension questions should have values

- [ ] All checkbox columns in a group are either:
  - ALL populated (mix of 0s and 1s), OR
  - ALL empty

- [ ] Event-specific fields only populated for correct events
  - Example: `study_information_timestamp` only at timepoint_1_arm_1
  - Example: `consent_t2` only at timepoint_2_arm_1 or later

---

### 13.4 Baseline Data Validation

Every participant should have:

- [ ] At least one row in the dataset
- [ ] Ideally: timepoint_1_arm_1 row (baseline)
- [ ] If has timepoint_1_arm_1: should have consent data (if enrolled)
  - `consent_consent` should be "1" (agreed)
  - `consent_nameprint` should have value (unless failed comprehension)
  - `consent_date` should have value

Exception: Participant 65 in SkinnyActual shows late entry is possible (may need protocol clarification)

---

### 13.5 Longitudinal Data Validation

For participants with multiple timepoints:

- [ ] Baseline (t1) should be earliest timepoint
  - Exception: Participant 65 (needs clarification)

- [ ] Standard and "_R" timepoints should not both exist for same number
  - Exception: Participant 126 has both t2 and t2_r (needs clarification)

- [ ] Timepoints should be reasonably ordered
  - Valid: t1, t2, t4, t5 (missed t3)
  - Questionable: t5, t3, t1, t2 (reverse order)

---

## 14. Questions for Research Team

### 14.1 CRITICAL Questions (Must Answer Before Proceeding)

**Q1: What does "_R" mean in event names?**
- Examples: timepoint_2_r_arm_1, timepoint_3_r_arm_1
- Options: Repeat/makeup visit? Reschedule? Remote (vs in-person)? Revised protocol? Other?
- **Why critical**: Affects how we interpret data, generate synthetic data, and document the system

**Q2: Can participants have BOTH standard and "_R" for same timepoint number?**
- Example: Participant 126 has both timepoint_2_arm_1 AND timepoint_2_r_arm_1
- Is this expected behavior or data error?
- If expected, which should be prioritized in analysis?
- How common is this pattern?

**Q3: Can participants enter the study without baseline data?**
- Example: Participant 65 has only timepoint_4_r_arm_1 and timepoint_5_r_arm_1 (no t1)
- Is this protocol-allowed (late enrollment)?
- Is baseline data recorded elsewhere?
- Should participants without baseline be excluded from analysis?

**Q4: For analysis, how should "_R" timepoints be treated?**
- As equivalent to standard timepoints? (combine t2 and t2_r as "timepoint 2")
- As separate groups? (analyze scheduled vs makeup visits separately)
- As backup data? (use standard if available, otherwise use "_R")
- Other approach?

---

### 14.2 Secondary Questions (Good to Know)

**Q5: Why do 24/48 participants in SkinnyActual have blank consent names?**
- Is this because SkinnyActual is early test data?
- Or are these real participants who failed comprehension checks?
- Or participants who started but didn't complete consent?

**Q6: The codebook shows THREE consent form versions (v1, v2, v3)**
- What are these for? Multiple consent attempts if participants fail?
- How does this work in practice?
- How many attempts do participants typically need?

**Q7: One form differs between standard and "_R" timepoints:**
- "Tx information_timepoint 2" exists at t2 but NOT at t2_r
- Is this intentional?
- What information is collected differently at standard vs "_R" dosing visits?

**Q8: Integration script name handling:**
- Currently only checks `consent_nameprint` at timepoint_1_arm_1
- Should we also check `consent_nameprint_v2` and `consent_nameprint_v3`?
- Should we search other timepoints if name is blank at t1?
- Or is blank name at t1 always a data quality issue to be preserved?

---

## 15. Recommendations

### 15.1 IMMEDIATE: Get Clarification on "_R" Timepoints (PRIORITY)

**Cannot proceed with confidence until we understand:**
1. What "_R" means
2. How to handle "_R" data in analysis
3. Whether both standard and "_R" for same timepoint is expected

**Why critical**:
- Affects synthetic data generation
- Affects integration script documentation
- Affects how researchers interpret output
- Affects statistical analysis approach

**Action**: Schedule meeting or send questions to Silver & Rick

---

### 15.2 After Clarification: Update sample_data to Match Real Structure

**Current issue**: sample_data is unrealistic
- Lacks "_R" timepoints (real data has them)
- No participants without baseline (real data has 1)
- Perfect consent completion (real data: 48%)
- No participants with both standard and "_R" (real data has 1)

**Recommendation**: Update sample_data generation to include:

1. **Add "_R" repeat timepoints** (15-20% of participants)
   ```
   Pattern examples:
   - Some participants: all standard timepoints (t1, t2, t3, t4, t5, t6)
   - Some participants: mix of standard and "_R" (t1, t2, t3_r, t4, t5_r, t6)
   - Some participants: mostly "_R" (t1, t2_r, t3_r, t4_r, t5, t6_r)
   ```

2. **Add 1-2 participants without baseline** (if protocol allows)
   - Mirrors Participant 65 pattern
   - Tests script robustness
   - Prepares researchers for this edge case

3. **Add 1 participant with both standard and "_R"** (if expected behavior)
   - Mirrors Participant 126 pattern
   - Shows researchers how output looks
   - Clarifies how to handle in analysis

4. **Keep perfect consent completion in sample_data**
   - Real blank names are test artifacts
   - Teaching data should be clean
   - Easier to understand for new users

---

### 15.3 Integration Script: Consider Optional Enhancements

**Current script works correctly**. Optional enhancements:

#### Option A: Data Quality Report
Add function to flag:
```python
def data_quality_report(df):
    issues = []

    # Check for participants without baseline
    no_baseline = participants without timepoint_1_arm_1
    if len(no_baseline) > 0:
        issues.append(f"{len(no_baseline)} participants without baseline")

    # Check for blank consents
    blank_names = participants with t1 but blank consent_nameprint
    if len(blank_names) > 0:
        issues.append(f"{len(blank_names)} participants with blank names")

    # Check for both standard and "_R" at same timepoint
    both_patterns = participants with both tX and tX_r
    if len(both_patterns) > 0:
        issues.append(f"{len(both_patterns)} participants with both standard and repeat")

    return issues
```

#### Option B: Enhanced Name Finding
```python
def find_participant_name(participant_df):
    # Try consent_nameprint at t1 first
    name = get_from_t1('consent_nameprint')
    if name is not None:
        return name

    # Try consent_nameprint_v2 and v3 at t1
    name = get_from_t1('consent_nameprint_v2')
    if name is not None:
        return name
    name = get_from_t1('consent_nameprint_v3')
    if name is not None:
        return name

    # Try any timepoint (if no baseline)
    name = get_from_any_timepoint('consent_nameprint')
    if name is not None:
        return name

    return NaN  # No name found
```

**Recommendation**: Wait until after "_R" clarification to decide if enhancements are needed.

---

### 15.4 Documentation Updates

After "_R" clarification, update:

1. **README.md**
   - Add section explaining "_R" timepoints
   - Clarify what researchers should expect in output

2. **insights_readme.md**
   - Explain why some columns end in "_r"
   - Provide guidance on handling "_R" data in analysis

3. **MASTER_DATA_STRUCTURE_REPORT.md** (this document)
   - Add team's answers to questions in Section 14
   - Update recommendations based on answers

---

### 15.5 No Action Needed For:

✅ **Integration script core logic** - Working correctly as-is

✅ **Output structure** - Correctly reflects input data

✅ **Missing data handling** - Appropriate (preserves as NaN)

✅ **Baseline identification** - Verified as correct (timepoint_1_arm_1)

✅ **Branching logic understanding** - Complete and documented

---

## 16. Conclusion

### 16.1 Summary of Report

This master report documents:

1. **Complete technical specifications** for REDCap data structure
   - 1,574 columns with detailed data type mappings
   - 11 events with form assignments
   - Branching logic patterns (26.2% of variables)
   - PII fields for de-identification

2. **Analytical findings from real data** (SkinnyActualExampleData)
   - Baseline structure verified (timepoint_1_arm_1)
   - 3 edge cases identified and documented
   - Blank names explained (failed consent comprehension)
   - "_R" timepoint patterns observed

3. **Integration script behavior** validated
   - Correctly handles all observed patterns
   - Produces appropriate output structure
   - No modifications needed currently

4. **Questions for research team** about "_R" timepoints
   - Meaning and intended use
   - Analysis approach
   - Expected vs unexpected patterns

5. **Recommendations** for next steps
   - Get "_R" clarification first (critical)
   - Update sample_data for realism (after clarification)
   - Consider optional script enhancements (after clarification)

---

### 16.2 Key Takeaways

**✅ What We Know for Certain:**
- Data structure is clear and fully documented
- Integration script works correctly
- timepoint_1_arm_1 is baseline (proven multiple ways)
- Branching logic explains missing data patterns
- Output differences between files are due to different timepoints present (correct behavior)

**⚠️ What Needs Clarification:**
- "_R" timepoint meaning and use
- Expected vs unexpected patterns (Participant 65, 126)
- Analysis approach for "_R" data

**📋 Next Actions:**
1. Send questions to Silver & Rick
2. Wait for clarification
3. Update sample_data generation
4. Update documentation with answers

---

### 16.3 Bottom Line

**The integration script is working perfectly.**

The outputs differ between SkinnyActualExampleData and sample_data not due to errors, but because:
1. Different timepoints are present in the input data (standard vs "_R")
2. Different data completeness levels (sparse pilot vs rich synthetic)
3. Real pilot data vs idealized synthetic data

Before generating new sample data or making any script changes, we **must** clarify the meaning and proper handling of "_R" timepoints with the research team.

---

*Report completed: November 30, 2025*
*This master document supersedes individual reports*
*Ready for team review and "_R" timepoint clarification*
