# Structural Analysis: SkinnyActualExampleData vs sample_data

**Date:** November 29, 2025
**Purpose:** Deep dive into data structures to inform integration improvements

---

## Executive Summary

After thorough analysis, both datasets follow the **same REDCap long-format structure** but differ in:
1. **Timepoint coverage**: SkinnyActual has early timepoints + repeats; sample_data has complete timeline
2. **Data completeness**: SkinnyActual is sparse pilot data; sample_data is rich synthetic data
3. **Repeat timepoints**: SkinnyActual has "_r" makeup visits; sample_data assumes perfect attendance

---

## 1. Structural Validation ✅

### Both files share:
- ✅ **1,574 columns** (identical REDCap structure)
- ✅ **Long format** (multiple rows per participant, one per timepoint)
- ✅ **`redcap_event_name`** field for timepoint identification
- ✅ **No duplicates** (max 1 row per participant per timepoint)
- ✅ **Same variable names** and coding schemes

**Conclusion:** Both are valid REDCap exports with identical schemas.

---

## 2. SkinnyActualExampleData Structure

### Profile:
- **59 rows** across **48 participants** (avg 1.2 timepoints per participant)
- **Early pilot/test data** with minimal actual responses
- **Most participants only have baseline** (47 out of 48 have t1)

### Timepoint Distribution:
```
timepoint_1_arm_1   : 47 participants (baseline)
timepoint_2_arm_1   :  6 participants
timepoint_2_r_arm_1 :  1 participant  (REPEAT)
timepoint_3_arm_1   :  2 participants
timepoint_3_r_arm_1 :  1 participant  (REPEAT)
timepoint_4_r_arm_1 :  1 participant  (REPEAT)
timepoint_5_r_arm_1 :  1 participant  (REPEAT)
```

### Notable Patterns:

**Participant 65 (Special Case #1):**
- Has ONLY repeat timepoints: `t4_r`, `t5_r`
- **No baseline (t1) data at all**
- Shows it's possible to enter study mid-way at makeup visits

**Participant 126 (Special Case #2):**
- Has 4 timepoints: `t1`, `t2`, `t2_r`, `t3_r`
- **Has BOTH standard t2 AND repeat t2_r**
- Unclear why someone would complete both scheduled and makeup for same timepoint
- Possibly:
  - Completed t2, flagged for quality issues, redid as t2_r?
  - Protocol allowed both for validation?
  - Data entry error?

**Participant Coverage:**
- 41 participants: Only 1 timepoint (baseline only)
- 4 participants: 2 timepoints
- 2 participants: 3 timepoints
- 1 participant: 4 timepoints (participant 126)

### Data Quality:
- **Names:** 23/47 participants with names at t1 (48%), many are test entries ("a", "s", "x", "sl")
- **PHQ-9:** Only 3 participants with PHQ-9 data at baseline
- **Other measures:** Similarly sparse (2 with GAD-7, 2 with WHO-5)

---

## 3. sample_data Structure

### Profile:
- **532 rows** across **120 participants** (avg 4.4 timepoints per participant)
- **Complete synthetic data** with realistic psychological profiles
- **Every participant has baseline** (120/120 have t1)

### Timepoint Distribution:
```
timepoint_1_arm_1 : 120 participants (baseline)
timepoint_2_arm_1 :  86 participants (72%)
timepoint_3_arm_1 :  82 participants (68%)
timepoint_4_arm_1 :  78 participants (65%)
timepoint_5_arm_1 :  87 participants (73%)
timepoint_6_arm_1 :  79 participants (66%)
```

### Notable Patterns:
- **No repeat timepoints** (assumes perfect attendance)
- **Realistic attrition**: ~15-35% dropout across timepoints
- **Varied longitudinal coverage**:
  - 8 participants: 2 timepoints
  - 17 participants: 3 timepoints
  - 30 participants: 4 timepoints
  - 45 participants: 5 timepoints
  - 20 participants: 6 timepoints (complete data)

### Data Quality:
- **Names:** 120/120 participants (100%) - famous psychonaut names
- **PHQ-9:** 104/120 at baseline (87%)
- **Other measures:** 78-93% complete at baseline
- **Realistic scores:** Based on 6 psychological profile types

---

## 4. Critical Differences

| Aspect | SkinnyActual | sample_data | Impact |
|--------|--------------|-------------|--------|
| **Repeat timepoints** | ✅ Has t2_r, t3_r, t4_r, t5_r | ❌ None | Output has different columns |
| **Late timepoints** | ❌ No t4, t5, t6 | ✅ Has all | SkinnyActual stops at t3 |
| **Baseline coverage** | 47/48 (98%) | 120/120 (100%) | Minor difference |
| **Longitudinal coverage** | 1.2 timepoints avg | 4.4 timepoints avg | Major difference |
| **Names at baseline** | 23/47 (49%) | 120/120 (100%) | Causes blank names in output |
| **Data completeness** | <10% with actual scores | 70-90% with scores | Major difference |

---

## 5. Why Outputs Differ

### Column Count Differences:
- **sample_data output:** 335 columns
  - Has columns ending in: `_t1`, `_t2`, `_t3`, `_t4`, `_t5`, `_t6`
  - Example: `phq9_total_t1`, `phq9_total_t2`, ..., `phq9_total_t6`

- **SkinnyActual output:** 388 columns (53 MORE)
  - Has columns ending in: `_t1`, `_t2`, `_t2_r`, `_t3`, `_t3_r`, `_t4_r`, `_t5_r`
  - Example: `phq9_total_t1`, `phq9_total_t2`, `phq9_total_t2_r`, ...
  - Extra columns for all repeat timepoints

### Name Blank Issue:
**Root cause:** Integration script only pulls `consent_nameprint` from `timepoint_1_arm_1`

**Why names are blank in SkinnyActual output:**
1. **24/47 participants** have blank `consent_nameprint` at t1 in the source data
2. **1 participant (65)** has no t1 row at all (only has t4_r and t5_r)
3. Script doesn't look for names at other timepoints

**Example:**
- Participant 65: No t1 row → Name = NaN
- Participant 122: Has t1 but name is blank → Name = NaN
- Participant 123: Has t1 with name "a" → Name = "a" ✓

---

## 6. Repeat Timepoint Patterns

### What are "_r" timepoints?
"_r" stands for **"repeat"** or **"makeup"** assessment for participants who missed scheduled visits.

### Three possible patterns:

**Pattern A: Missed scheduled, did makeup (most common)**
```
Participant A:
- timepoint_1_arm_1 (baseline)
- timepoint_2_r_arm_1 (missed t2, did makeup)
- timepoint_3_arm_1 (back on track)
```

**Pattern B: Has BOTH (unusual - Participant 126)**
```
Participant 126:
- timepoint_1_arm_1
- timepoint_2_arm_1
- timepoint_2_r_arm_1  (← Why both?)
- timepoint_3_r_arm_1
```
*Possible reasons: Data quality redo, protocol allows both, data entry error*

**Pattern C: Only repeats, no baseline (rare - Participant 65)**
```
Participant 65:
- timepoint_4_r_arm_1
- timepoint_5_r_arm_1
(No baseline at all - entered study late?)
```

---

## 7. Recommendations

### For sample_data Generation:

**Add realistic repeat timepoints (15-20% of participants):**

1. **Create missed visit scenarios:**
   - Randomly select 15-20% of participants per timepoint
   - Mark them as "missed" at standard timepoint
   - Create "_r" repeat timepoint instead

2. **Ensure variety:**
   - Some participants never miss (all standard timepoints)
   - Some miss 1-2 visits (have some "_r" timepoints)
   - Maybe 1-2 participants miss many visits (mostly "_r")
   - Possibly 1 participant enters late (no t1, starts at t2_r or t3_r)

3. **Data consistency:**
   - When someone has t2_r instead of t2, their data should be at t2_r
   - Avoid having BOTH t2 and t2_r for same participant (unless we understand why Participant 126 has this)

### For Integration Script:

**Fix name handling to be robust:**

```python
# Current (rigid):
df_baseline = df[df['redcap_event_name'] == 'timepoint_1_arm_1']
# Only gets names from t1

# Proposed (flexible):
for participant_id in unique_participants:
    # 1. Try t1 first
    # 2. If blank/missing, look for name at ANY timepoint
    # 3. Use first non-blank name found
```

**Benefits:**
- Handles participants without t1 (like Participant 65)
- Handles participants with blank names at t1 but filled elsewhere
- More robust to real-world data quality issues

---

## 8. Implementation Plan

### Phase 1: Fix Name Handling (High Priority)
1. Update `pivot_to_wide()` function in `integrate.py`
2. Add logic to search all timepoints for baseline variables if t1 is missing/blank
3. Test with SkinnyActualExampleData to verify Participant 65 gets name if available elsewhere
4. Apply same fix to `integrate_simple.py`

### Phase 2: Add Repeat Timepoints to sample_data (Medium Priority)
1. Update `generate_sample_data.py`
2. Add parameter: `repeat_visit_rate = 0.17` (17% miss each visit)
3. Implement logic to:
   - Randomly select participants to miss scheduled visits
   - Generate "_r" repeat data instead
   - Ensure data quality (names, demographics stay consistent)
4. Regenerate sample_data.xlsx
5. Test that integrate.py handles it correctly

### Phase 3: Documentation (Low Priority)
1. Update README to explain repeat timepoints
2. Add section in insights_readme.md about "_r" columns
3. Document the three patterns (A, B, C above)

---

## 9. Questions for Consideration

### About Participant 126 having both t2 and t2_r:
- **Is this expected behavior?**
- **Should we replicate this in sample_data?**
- **Or is it a data quality issue to be excluded?**

### About late entry (Participant 65):
- **Can participants really enter mid-study without baseline?**
- **If yes, how common is this?**
- **Should sample_data include 1-2 late entrants?**

### About repeat timepoint handling in analysis:
- **How should researchers handle participants with both standard and repeat?**
- **Priority order: Use standard, fall back to repeat?**
- **Or analyze as separate groups (scheduled vs makeup)?**

---

## 10. Conclusion

### Key Insights:
1. ✅ **Both datasets are structurally sound** - same REDCap format
2. ✅ **Integration script works correctly** - handles whatever timepoints exist
3. ⚠️ **sample_data is unrealistic** - assumes perfect attendance (no "_r")
4. ⚠️ **Name handling is fragile** - only looks at t1, fails if blank/missing

### Action Items:
1. **Immediate:** Fix name handling to search all timepoints
2. **Soon:** Add repeat timepoints to sample_data for realism
3. **Optional:** Decide on handling participants with both standard and repeat

### Bottom Line:
The differences we observed are **real and important** - they reflect the difference between:
- **SkinnyActual:** Real-world messy data with missed visits
- **sample_data:** Idealized synthetic data with perfect attendance

Making sample_data more realistic by adding "_r" timepoints will:
- Better prepare researchers for real data
- Test that the integration script handles edge cases
- Provide examples of how to interpret "_r" columns in output

---

*Analysis completed: November 29, 2025*
*Next steps: Implement Phase 1 (name handling fix)*
