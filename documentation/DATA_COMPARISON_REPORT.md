# Data Comparison Report: SkinnyActualExampleData vs sample_data

**Date:** November 29, 2025
**Purpose:** Investigate differences between outputs from two REDCap data sources

---

## Executive Summary

The outputs differ significantly because **the input files contain data at different timepoints**, not because of structural problems or script errors. Both files have identical column structures (1,574 columns), but they contain data from different phases of data collection.

### Key Finding:
✅ **Both files are structured correctly and process successfully**
⚠️ **SkinnyActualExampleData has "_r" (repeat) timepoints that sample_data doesn't have**

---

## 1. Input File Comparison

### File: `sample_data.xlsx`
- **Rows:** 532 (long format)
- **Unique Participants:** 120
- **Columns:** 1,574
- **Timepoints present:** t1, t2, t3, t4, t5, t6 (standard timepoints)
- **Data completeness:** High (realistic sample data with 60-70% response rates)
- **Purpose:** Generated sample data with realistic psychological profiles

### File: `SkinnyActualExampleData.csv`
- **Rows:** 59 (long format)
- **Unique Participants:** 48
- **Columns:** 1,574
- **Timepoints present:** t1, t2, t2_r, t3, t3_r, t4_r, t5_r (includes repeat timepoints)
- **Data completeness:** Low (3 PHQ-9 at baseline, 2 GAD-7 at baseline, 2 WHO-5 at baseline)
- **Purpose:** Early test/pilot data from actual REDCap system

### Critical Differences:

| Aspect | sample_data.xlsx | SkinnyActualExampleData.csv |
|--------|------------------|----------------------------|
| **Columns** | 1,574 | 1,574 ✓ SAME |
| **Structure** | Has `redcap_event_name` | Has `redcap_event_name` ✓ SAME |
| **Timepoints** | t1, t2, t3, t4, t5, t6 | t1, t2, t2_r, t3, t3_r, t4_r, t5_r |
| **Data Quality** | Realistic, complete | Sparse, test entries |
| **Participants** | 120 | 48 |

---

## 2. Output File Comparison

### Output from `sample_data.xlsx` → `insights_YYYYMMDD_THHMMSS.xlsx`
- **Rows:** 120 (one per participant)
- **Columns:** 335
- **Timepoint columns:** Variables end with _t1, _t2, _t3, _t4, _t5, _t6
- **Example columns:** `phq9_total_t1`, `phq9_total_t2`, `phq9_total_t3`, etc.

### Output from `SkinnyActualExampleData.csv` → `insights_YYYYMMDD_THHMMSS.xlsx`
- **Rows:** 48 (one per participant)
- **Columns:** 388
- **Timepoint columns:** Variables end with _t1, _t2, _t2_r, _t3, _t3_r, _t4_r, _t5_r
- **Example columns:** `phq9_total_t1`, `phq9_total_t2`, `phq9_total_t2_r`, etc.

### Why Different Column Counts?

**SkinnyActual has 53 MORE columns (388 vs 335)** because it has "_r" repeat timepoints:

**Extra columns in SkinnyActual output:**
- All variables × repeat timepoints: `*_t2_r`, `*_t3_r`, `*_t4_r`, `*_t5_r`
- Examples: `audit_4_t2_r`, `audit_4_t3_r`, `phq9_1_t2_r`, `gad7_1_t3_r`

**Missing columns in SkinnyActual output:**
- Variables at standard t4, t5, t6 timepoints (which SkinnyActual doesn't have data for)
- Examples: `audit_4_t4`, `audit_4_t5`, `audit_4_t6`, `auditc_1_t4`, etc.

---

## 3. What Are "_r" Repeat Timepoints?

**Definition:** "_r" stands for "repeat" or "makeup" assessments for participants who missed their originally scheduled visit.

**Examples:**
- `timepoint_2_r_arm_1` = Repeat assessment for timepoint 2
- `timepoint_3_r_arm_1` = Repeat assessment for timepoint 3

**Why they exist:**
- In longitudinal studies, participants sometimes miss appointments
- REDCap creates repeat events to capture makeup assessments
- This preserves all data collection attempts

**In the data:**
- **sample_data:** No repeat timepoints (assumes perfect attendance for teaching purposes)
- **SkinnyActual:** Has repeat timepoints (reflects real-world data collection)

---

## 4. Script Behavior Analysis

### ✅ The Script is Working Correctly

The integration script (`integrate.py`) correctly handles BOTH file types:

1. **Detects all timepoints present** in the input data
2. **Creates columns for each timepoint** found
3. **Pivots to wide format** (one row per participant)
4. **Preserves all data** without loss

### Timepoint Detection Logic

```python
TIMEPOINT_MAP = {
    'timepoint_1_arm_1': 't1',
    'timepoint_2_arm_1': 't2',
    'timepoint_2_r_arm_1': 't2_r',  # Handles repeats
    'timepoint_3_arm_1': 't3',
    'timepoint_3_r_arm_1': 't3_r',  # Handles repeats
    # ... etc
}
```

The script dynamically creates columns for whatever timepoints exist in your data.

---

## 5. Data Quality Comparison

### sample_data.xlsx (Generated Sample)
```
PHQ-9 at baseline (t1): 104/120 participants (87%)
GAD-7 at baseline (t1): 93/120 participants (78%)
WHO-5 at baseline (t1): 89/120 participants (74%)
MEQ-4 at t2: 67/120 participants (56%)

Sample participant names: Albert Hofmann, Alexander Shulgin, Ann Shulgin (famous psychonauts)
Ages: Realistic distribution (26-66 years)
Scores: Realistic psychological profiles with treatment responses
```

### SkinnyActualExampleData.csv (Early Test Data)
```
PHQ-9 at baseline (t1): 3/48 participants (6%)
GAD-7 at baseline (t1): 2/48 participants (4%)
WHO-5 at baseline (t1): 2/48 participants (4%)
MEQ-4 at t2: 0/48 participants (0%)

Sample participant names: "a", "s", "x" (test entries)
Ages: Some missing, range 22-25 for entries present
Scores: Mostly empty/missing (test data)
```

**Conclusion:** SkinnyActual is early test/pilot data with minimal entries, not suitable for real analysis.

---

## 6. Implications for Your Study

### ✅ Good News:
1. **Script handles both file types correctly**
2. **Repeat timepoints are automatically detected and processed**
3. **No data is lost in the transformation**
4. **One row per participant format works for both**

### 📋 Recommendations:

1. **For real analysis:** Use complete REDCap exports, not test data
   - Ensure participants have baseline data (t1)
   - Check for adequate sample sizes at each timepoint

2. **Understanding repeat timepoints:**
   - `t2` = Scheduled timepoint 2
   - `t2_r` = Makeup for timepoint 2 (if participant missed)
   - You may have EITHER t2 OR t2_r for a given participant, rarely both

3. **Data analysis considerations:**
   - Decide how to handle repeat vs standard timepoints
   - May want to prioritize standard timepoints, use repeats as backup
   - Or analyze them separately (scheduled vs makeup visits)

4. **Future data exports:**
   - Your actual study data will likely have some "_r" timepoints (this is normal!)
   - The script will handle them automatically
   - Resulting output will have more columns than sample_data (expected)

---

## 7. Timestamp Feature Added

As requested, output filenames now include timestamps:

**Format:** `insights_YYYYMMDD_THHMMSS.xlsx`

**Example:** `insights_20251129_T165452.xlsx`
- Date: November 29, 2025
- Time: 16:54:52 (4:54:52 PM)

**Benefits:**
- Never overwrite previous outputs
- Track when analyses were run
- Easy to identify most recent version
- Useful for version control

---

## 8. Conclusion

### Summary:
- ✅ **No structural problems** - both files have identical 1,574 column structure
- ✅ **Script works correctly** - handles both standard and repeat timepoints
- ✅ **Outputs differ** because inputs contain different timepoints
- ✅ **Timestamp feature** added as requested

### The Real Difference:
```
sample_data.xlsx:         Has t1, t2, t3, t4, t5, t6
                          Complete realistic data
                          120 participants

SkinnyActualExampleData:  Has t1, t2, t2_r, t3, t3_r, t4_r, t5_r
                          Sparse test data
                          48 participants
```

### Bottom Line:
Your integration script is working perfectly. The outputs differ because the **inputs contain data from different timepoints**, which is exactly what should happen. When you receive real REDCap exports, they will likely include some repeat timepoints, and the script will handle them automatically.

---

*Report generated: November 29, 2025*
*Analyst: Claude*
