# Comprehensive Data Structure Analysis Report
**Date:** November 30, 2025
**Purpose:** Complete understanding of SkinnyActualExampleData and codebook structure to inform output design and sample data generation

---

## Executive Summary

After thorough analysis of SkinnyActualExampleData.csv and the updated codebook, I can now provide a complete picture of the data structure and how the integration script processes it.

### Key Findings:
1. ✅ **timepoint_1_arm_1 IS definitively the baseline** (verified through multiple sources)
2. ✅ **Current integration script correctly handles the data structure**
3. ⚠️ **"_R" timepoint meaning requires clarification** from Silver & Rick
4. ✅ **Branching logic explains blank consent fields** (comprehension check failures)
5. ⚠️ **Three unusual edge cases** need protocol clarification

---

## 1. Baseline Structure: timepoint_1_arm_1 VERIFIED

### Evidence that timepoint_1_arm_1 is baseline:

#### A. Consent Data (100% definitive)
```
ALL consent signatures occur at timepoint_1_arm_1:
- consent_nameprint: 23 entries at t1, 0 at other timepoints
- consent_consent: 23 entries at t1, 0 at other timepoints
- consent_date: 23 entries at t1, 0 at other timepoints

Conclusion: Participants can only legally enter the study at t1.
```

#### B. Baseline-Only Forms (from codebook Instruments sheet)
**8 forms ONLY available at timepoint_1_arm_1:**
```
Form Name                          | Participants with Data
-----------------------------------|----------------------
study_information                  | 47/48 (98%)
informed_consent (attempts 1-3)    | 47/48 (98%)
expectancy_measure                 | 47/48 (98%)
date_calculation                   | 47/48 (98%)
when_is_tx_scheduled               | 47/48 (98%)
medssupps_predosing               | 47/48 (98%)
```

These forms can ONLY be completed at baseline - they're not available at any other timepoint.

#### C. Demographics Pattern
```
demographic_survey: 47/48 participants have data at t1
                    1/48 (Participant 65) has NO t1 row at all

Conclusion: Demographics are baseline data by design.
```

**VERDICT**: timepoint_1_arm_1 is unequivocally the baseline/entry point for the study.

---

## 2. Form-Event Mapping: What Data is Collected When

### Timepoint Structure from Codebook

**11 Total Events:**
- **6 Standard timepoints**: t1, t2, t3, t4, t5, t6
- **5 "_R" variants**: t2_r, t3_r, t4_r, t5_r, t6_r

### Forms by Timepoint Pattern

#### Pattern A: Baseline Only (8 forms)
**Available ONLY at timepoint_1_arm_1:**
- study_information
- informed_consent (versions 1, 2, 3 for multiple attempts)
- expectancy_measure
- date_calculation
- when_is_tx_scheduled
- medssupps_predosing
- demographic_survey
- treatment_preference

**Interpretation**: Collected once at study entry, never repeated.

---

#### Pattern B: Dosing Session Only (6 forms)
**Available ONLY at timepoint_2_arm_1 and timepoint_2_r_arm_1:**
```
Form                              | Purpose
----------------------------------|----------------------------------
MEQ-4 (Mystical Experience)       | Acute subjective effects
SSCS-S (State Self-Compassion)    | During/after dosing
MPoD-S (Metacognitive Decentering)| Perceptual changes
EBI (Emotional Breakthrough)      | Breakthrough intensity
CEQ-7 (Challenging Experiences)   | Difficult experiences
PIQ (Psychological Insight)       | Insight quality
```

**Interpretation**: These measure the acute psychedelic experience, so they're only relevant at the dosing visit (t2 or t2_r).

---

#### Pattern C: Repeated Outcome Measures (58 forms)
**Available at MULTIPLE timepoints (t1, t3, t4, t5, t6 and corresponding "_R" variants):**

Core outcome measures included in our integration script:
- PHQ-9 (Depression)
- GAD-7 (Anxiety)
- WHO-5 (Wellbeing)
- PsyFlex (Psychological Flexibility)
- AUDIT-C (Alcohol Use)

Plus many additional clinical and personality measures:
- BFI-44 (Big Five Inventory)
- FFMQ (Mindfulness)
- MAIA-2 (Interoceptive Awareness)
- PANAS (Positive/Negative Affect)
- RRQ (Rumination-Reflection)
- And ~40 more instruments

**Interpretation**: Longitudinal tracking of outcomes over time.

---

### Critical Finding: Standard vs "_R" Event Form Availability

#### Forms available at BOTH standard and "_R" timepoints:
```
Example: timepoint_2_arm_1 vs timepoint_2_r_arm_1

Forms at BOTH:
- MEQ-4 ✓
- SSCS-S ✓
- All acute experience measures ✓
- (14 total forms identical)

Forms ONLY at t2 (not t2_r):
- Tx information_timepoint 2 (1 form)
```

**Interpretation**: Standard and "_R" events are nearly identical in structure. "_R" events have almost all the same forms available, suggesting they serve a parallel function.

---

## 3. "_R" Timepoint Characteristics

### What We Know (from data):

#### Evidence from codebook:
- "_R" events exist in the Events sheet: "Timepoint 2_R", "Timepoint 3_R", etc.
- **No explanation provided** of what "_R" means
- "_R" events have (nearly) identical form assignments as standard events

#### Evidence from SkinnyActualExampleData:
```
Timepoint Distribution in Real Data:
- timepoint_1_arm_1:   47 participants (baseline)
- timepoint_2_arm_1:    6 participants
- timepoint_2_r_arm_1:  1 participant  ← "_R" variant
- timepoint_3_arm_1:    2 participants
- timepoint_3_r_arm_1:  1 participant  ← "_R" variant
- timepoint_4_r_arm_1:  1 participant  ← "_R" only (no standard t4)
- timepoint_5_r_arm_1:  1 participant  ← "_R" only (no standard t5)
```

### Three Unusual Patterns in Real Data:

#### Pattern 1: Standard OR Repeat (Most Common)
```
Typical Participant:
- timepoint_1_arm_1 (baseline)
- timepoint_2_arm_1 (standard dosing visit)
- timepoint_3_arm_1 (standard follow-up)

OR

- timepoint_1_arm_1 (baseline)
- timepoint_2_r_arm_1 (dosing visit - "_R" version)
- timepoint_3_arm_1 (standard follow-up)
```
**Hypothesis**: "_R" might be an alternative/makeup visit when standard time wasn't available?

---

#### Pattern 2: BOTH Standard AND Repeat (Unusual - 1 case)
```
Participant 126:
- timepoint_1_arm_1 (baseline)
- timepoint_2_arm_1 (standard)
- timepoint_2_r_arm_1 ("_R" version) ← Why both?
- timepoint_3_r_arm_1 ("_R" version)
```

**Questions:**
- Why would someone complete BOTH timepoint_2_arm_1 AND timepoint_2_r_arm_1?
- Is this a data quality issue (redo after problems)?
- Is this protocol-allowed (validation/reliability check)?
- Is this a data entry error?

---

#### Pattern 3: ONLY "_R" Timepoints, No Baseline (Rare - 1 case)
```
Participant 65:
- timepoint_4_r_arm_1
- timepoint_5_r_arm_1
(NO timepoint_1_arm_1 at all)
```

**Implications:**
- Participant 65 has NO consent data
- Participant 65 has NO demographics
- Participant 65 has NO baseline clinical data

**Questions:**
- Can participants enter the study mid-way without baseline?
- Is this a data entry issue (baseline data in different system)?
- Is this a late enrollment scenario?

---

### What We NEED to Ask Silver & Rick:

**Question 1**: What does "_R" stand for?
- Repeat/makeup visit?
- Reschedule?
- Remote (vs in-person)?
- Revised protocol?
- Something else?

**Question 2**: Can participants have both standard and "_R" for the same timepoint number?
- Is Participant 126 expected behavior?
- If yes, which should be prioritized in analysis?

**Question 3**: Can participants enter the study without baseline (like Participant 65)?
- Is this allowed by protocol?
- How should analysis handle participants without demographics?

**Question 4**: For analysis planning, should we:
- Treat standard and "_R" as equivalent timepoints?
- Analyze them separately?
- Use standard as primary, "_R" as backup?

---

## 4. Branching Logic Impact on Data Structure

### Key Finding: Outcome Measures Have NO Branching Logic

```
Measures with NO branching logic (ALWAYS shown when form is opened):
- PHQ-9: All 9 items always displayed
- GAD-7: All 7 items always displayed
- WHO-5: All 5 items always displayed
- MEQ-4: All 4 subscales always displayed
- PsyFlex: All 6 items always displayed
- AUDIT-C: All 3 items always displayed
```

**Implication**: Missing data in outcome measures = **true missingness** (participant chose not to answer), NOT hidden by branching logic.

---

### Consent Fields Have Complex Branching Logic

```
consent_nameprint only shows if:
  [consent_age]="1"

consent_consent only shows if:
  [consent_age] = "1" AND
  [consent_psilocybintherapy] = "1" AND
  [consent_primarypurpose] = "2" AND
  [consent_involvement] = "1" AND
  [consent_emotionaldiscomfort] = "1" AND
  [consent_services] = "2" AND
  [consent_participation] = "1"
```

**This is a comprehension check!** Participants must correctly answer all consent understanding questions before they can sign.

---

### Why 24/47 Participants Have Blank Names

**Analysis of SkinnyActualExampleData:**
```
Participants with consent_nameprint at t1: 23/47 (49%)
Participants without consent_nameprint at t1: 24/47 (51%)
```

**Possible explanations:**
1. **Failed comprehension check**: Didn't answer consent questions correctly, so `consent_nameprint` field never appeared
2. **Partial completion**: Started consent process but didn't finish
3. **Test data artifacts**: Early pilot testing where researchers were checking the system

**Implication**: Blank names are likely a DATA QUALITY issue from early testing, not a structural issue with the script.

---

### Overall Branching Logic Statistics

```
Total variables: 1,391
Variables with branching logic: 364 (26.2%)
```

**26% of fields have conditional display**, but importantly:
- All OUTCOME MEASURES have no branching (always shown)
- Branching is concentrated in:
  - Consent comprehension checks
  - Follow-up questions (e.g., "if yes, explain")
  - Protocol-specific routing

**Implication for output structure**: Branching logic does NOT change the output columns created. It explains patterns of systematic missingness, but all variables still exist in the output.

---

## 5. Current Integration Script Behavior

### How integrate.py Handles This Structure:

#### Step 1: Identify Unique Participants
```python
participant_col = 'participant_id' or 'record_id'
unique_participants = df[participant_col].unique()
```

#### Step 2: Extract Baseline Data (Demographics & Consent)
```python
df_baseline = df[df['redcap_event_name'] == 'timepoint_1_arm_1']

For each participant:
    - Pull name from consent_nameprint at t1
    - Pull age, gender, education from t1
    - If t1 doesn't exist → demographics = NaN
    - If t1 exists but fields are blank → preserve blank as NaN
```

**Current behavior with edge cases:**
- **Participant 65** (no t1): Name = NaN, Age = NaN, Gender = NaN ✓ Correct
- **24 participants with blank names**: Name = NaN ✓ Correct (preserves data quality issue)

---

#### Step 3: Pivot Time-Varying Measures to Wide Format
```python
For each timepoint found in the data:
    - Detect redcap_event_name
    - Map to short code (t1, t2, t2_r, t3, t3_r, etc.)
    - Create columns: variable_t1, variable_t2, variable_t2_r, etc.

Example with SkinnyActualExampleData:
    Timepoints found: t1, t2, t2_r, t3, t3_r, t4_r, t5_r

    phq9_1 becomes:
    - phq9_1_t1
    - phq9_1_t2
    - phq9_1_t2_r  ← Extra column for repeat
    - phq9_1_t3
    - phq9_1_t3_r  ← Extra column for repeat
    - phq9_1_t4_r  ← Only "_R" exists, no standard t4
    - phq9_1_t5_r  ← Only "_R" exists, no standard t5
```

**Why SkinnyActual has 388 columns vs sample_data's 335:**
- SkinnyActual has: `*_t2_r`, `*_t3_r`, `*_t4_r`, `*_t5_r` columns
- sample_data has: standard `*_t4`, `*_t5`, `*_t6` columns only
- Different timepoints = different column structure

---

#### Step 4: Calculate Composite Scores
```python
For each timepoint where data exists:
    phq9_total_t1 = sum(phq9_1_t1 through phq9_9_t1) if all items present
    phq9_total_t2_r = sum(phq9_1_t2_r through phq9_9_t2_r) if all items present

    # Handles missing data:
    If any item is NaN → total = NaN
```

---

#### Step 5: Create Output Structure
```
One row per participant:
- participant_id
- name (from t1)
- age (from t1)
- gender (from t1)
- education (from t1)
- phq9_1_t1, phq9_1_t2, phq9_1_t2_r, ... (all items × all timepoints)
- phq9_total_t1, phq9_total_t2, phq9_total_t2_r, ... (scores × all timepoints)
- gad7_1_t1, gad7_1_t2, gad7_1_t2_r, ... (all items × all timepoints)
- gad7_total_t1, gad7_total_t2, gad7_total_t2_r, ... (scores × all timepoints)
- [continue for all measures...]
```

---

### ✅ Script Correctly Handles:
1. ✅ Variable numbers of timepoints per participant
2. ✅ Missing baseline (Participant 65) → leaves demographics blank
3. ✅ Blank names in source data → preserved as NaN
4. ✅ Repeat ("_R") timepoints → creates separate columns
5. ✅ Missing data in outcome measures → preserved as NaN
6. ✅ Both standard and "_R" at same timepoint (Participant 126) → separate columns for each

---

## 6. Output Structure Implications

### For SkinnyActualExampleData Output:

```
48 rows (one per participant)
388 columns

Column structure:
- 5 demographic columns (participant_id, name, age, gender, education)
- 383 time-varying columns:
  - Variables ending in: _t1, _t2, _t2_r, _t3, _t3_r, _t4_r, _t5_r
  - Includes both individual items AND computed totals
  - Example: phq9_1_t1, phq9_1_t2, phq9_1_t2_r, phq9_1_t3, phq9_1_t3_r, phq9_1_t4_r, phq9_1_t5_r
  - Example: phq9_total_t1, phq9_total_t2, phq9_total_t2_r, phq9_total_t3, phq9_total_t3_r, phq9_total_t4_r, phq9_total_t5_r
```

### For sample_data Output:

```
120 rows (one per participant)
335 columns

Column structure:
- 5 demographic columns
- 330 time-varying columns:
  - Variables ending in: _t1, _t2, _t3, _t4, _t5, _t6
  - NO "_R" columns (sample_data has no repeat timepoints)
```

---

### Why Column Counts Differ:

**SkinnyActual has MORE columns** because:
- Has 7 timepoint suffixes: _t1, _t2, _t2_r, _t3, _t3_r, _t4_r, _t5_r
- Each variable × 7 timepoints = more columns

**SkinnyActual has FEWER participants** because:
- Only 48 participants (early pilot data)
- vs 120 in sample_data (complete synthetic dataset)

**SkinnyActual has MORE missing data** because:
- Real sparse pilot data
- Some participants only have baseline
- Most outcome measures mostly blank

---

## 7. Edge Cases and Unusual Patterns

### Edge Case 1: Participant 65 (No Baseline)
```
Data Present:
- timepoint_4_r_arm_1: Some measures completed
- timepoint_5_r_arm_1: Some measures completed

Data Absent:
- timepoint_1_arm_1: NO DATA
- consent_nameprint: NO DATA
- age, gender, education: NO DATA

Output Structure:
participant_id | name | age | gender | education | phq9_total_t4_r | phq9_total_t5_r
65            | NaN  | NaN | NaN    | NaN       | [score if avail]| [score if avail]
```

**Questions for team:**
- Is this expected? Can someone enter mid-study?
- Should this participant be excluded from analysis?
- Is baseline data recorded elsewhere?

---

### Edge Case 2: Participant 126 (Both Standard and "_R")
```
Timepoints:
- timepoint_1_arm_1
- timepoint_2_arm_1
- timepoint_2_r_arm_1
- timepoint_3_r_arm_1

Output Structure:
participant_id | phq9_total_t1 | phq9_total_t2 | phq9_total_t2_r | phq9_total_t3_r
126           | [baseline]    | [score at t2] | [score at t2_r] | [score at t3_r]
```

**Questions for team:**
- Why both t2 and t2_r?
- For analysis, which should be used?
- Is this a validation/reliability check?

---

### Edge Case 3: Blank Names Despite Having t1 (24 participants)
```
Pattern:
- Has timepoint_1_arm_1 row
- Has some data at t1
- consent_nameprint = blank/NaN

Cause (from branching logic):
- Failed consent comprehension check
- OR started consent but didn't finish
- OR test data artifact

Output Structure:
participant_id | name | age | gender | phq9_total_t1
122           | NaN  | 25  | Male   | NaN
```

**Implication**: This is a data quality issue from pilot testing, not a structural problem. Real study data should have names for all participants who complete consent.

---

## 8. Comparison: SkinnyActualExampleData vs sample_data

### SkinnyActualExampleData (Real Pilot Data):
```
Participants: 48
Rows (long format): 59
Timepoints present: t1, t2, t2_r, t3, t3_r, t4_r, t5_r
Data completeness: SPARSE (3 PHQ-9 at baseline, 2 GAD-7, 2 WHO-5)
Names at baseline: 23/47 (49%)
Consent completion: 23/48 (48%)

Special patterns:
- 1 participant with no baseline (Participant 65)
- 1 participant with both t2 and t2_r (Participant 126)
- 24 participants with blank names despite having t1
- 41 participants with ONLY baseline (no follow-up)
```

### sample_data (Synthetic Data):
```
Participants: 120
Rows (long format): 532
Timepoints present: t1, t2, t3, t4, t5, t6
Data completeness: RICH (87% PHQ-9 at baseline, 78% GAD-7, 74% WHO-5)
Names at baseline: 120/120 (100%)
Consent completion: 120/120 (100%)

Special patterns:
- NO repeat ("_R") timepoints ← UNREALISTIC
- NO participants without baseline ← UNREALISTIC
- NO blank names ← UNREALISTIC (but cleaner for teaching)
- Realistic attrition (65-73% at each follow-up)
```

---

### Key Difference: sample_data is TOO CLEAN

**sample_data does NOT reflect real-world patterns:**
1. ❌ No "_R" repeat timepoints (real data has them)
2. ❌ No participants without baseline (real data has 1)
3. ❌ No blank names (real data has 24)
4. ❌ No participants with both standard and "_R" (real data has 1)
5. ❌ Perfect baseline completion (real data: 48%)

**If sample_data is meant to prepare researchers for real data**, it should include these patterns.

---

## 9. Recommendations

### Recommendation 1: Clarify "_R" Meaning with Team (PRIORITY)

**Before proceeding with any changes, ask Silver & Rick:**

1. What does "_R" mean in the study protocol?
2. How should "_R" timepoints be handled in analysis?
3. Is it expected that some participants have both standard and "_R"?
4. Can participants enter without baseline?

**Why this is critical**: We cannot create realistic sample data or modify the integration script appropriately without understanding the intended meaning and use of "_R" timepoints.

---

### Recommendation 2: Decide on Name Handling Strategy

**Current behavior**: Only pulls names from timepoint_1_arm_1
**Issue**: 24/47 participants have blank names at t1

**Option A: Keep current behavior** (preserves data integrity)
- Pro: Reflects actual data quality issues
- Pro: Doesn't make assumptions about data
- Con: Leaves NaN for names in output

**Option B: Search all timepoints for names** (fills in blanks)
- Pro: Finds names if they exist elsewhere
- Pro: Handles Participant 65 (no t1 at all)
- Con: Might use name from later timepoint (less ideal)

**Recommendation**: Keep current behavior for now. Blank names in SkinnyActual are likely early test data artifacts. Real study data should have complete consent at t1.

---

### Recommendation 3: Update sample_data to Match Real Structure

**After clarifying "_R" meaning**, update sample_data generation to include:

1. **Add "_R" repeat timepoints** (~15-20% of participants)
   - Some participants have standard timepoints (t2, t3, t4)
   - Some have "_R" instead (t2_r, t3_r, t4_r)
   - Realistic mix like real data

2. **Add 1-2 participants without baseline** (edge case testing)
   - Mirrors Participant 65 pattern
   - Tests script robustness

3. **Add 1 participant with both standard and "_R"** (if protocol allows)
   - Mirrors Participant 126 pattern
   - Ensures script handles this correctly

4. **Keep perfect consent completion** in sample_data
   - Real-world blank names are test artifacts
   - Teaching data should be clean here

---

### Recommendation 4: No Script Changes Needed Currently

**The integration script correctly handles all patterns we've observed:**
- ✅ Missing baseline → NaN for demographics
- ✅ "_R" timepoints → separate columns created
- ✅ Both standard and "_R" → both columns created
- ✅ Blank names → preserved as NaN

**Only potential enhancement**: Add a data quality report that flags:
- Participants without baseline
- Participants with blank consent
- Participants with both standard and "_R" at same timepoint

But this is optional and can wait until after "_R" clarification.

---

## 10. Questions for Silver & Rick

### Critical Questions (Must Answer Before Proceeding):

**Q1: What does "_R" mean?**
- Options: Repeat/makeup visit? Reschedule? Remote? Revised protocol? Other?
- This affects how we interpret the data and document it

**Q2: Can participants have both standard and "_R" for the same timepoint number?**
- Example: Participant 126 has both timepoint_2_arm_1 AND timepoint_2_r_arm_1
- Is this expected? If yes, which should be prioritized in analysis?

**Q3: Can participants enter the study without baseline data?**
- Example: Participant 65 has only timepoint_4_r_arm_1 and timepoint_5_r_arm_1 (no t1)
- Is this protocol-allowed? Or data entry error?

**Q4: For analysis, how should "_R" timepoints be treated?**
- As equivalent to standard timepoints?
- As separate groups?
- As backup data (use standard if available, otherwise use "_R")?

---

### Secondary Questions (Nice to Know):

**Q5: Why do 24/48 participants have blank consent names?**
- Is this because SkinnyActual is early test data?
- Or are these real participants who failed comprehension checks?

**Q6: The codebook shows THREE consent form versions (v1, v2, v3)**
- What are these for? Multiple consent attempts?
- How does this work in practice?

**Q7: One form differs between standard and "_R":**
- "Tx information_timepoint 2" exists at t2 but not t2_r
- Is this intentional? What's the difference?

---

## 11. Conclusion

### Summary of Findings:

1. **✅ Data structure is clear**: timepoint_1_arm_1 is definitively baseline, verified through consent data, baseline-only forms, and demographics

2. **✅ Integration script works correctly**: Handles all observed patterns including missing baseline, "_R" timepoints, and blank names

3. **⚠️ "_R" meaning unclear**: Need team input to understand what "_R" represents and how to handle it in analysis

4. **✅ Branching logic understood**: Explains blank consent fields (comprehension checks), but doesn't affect outcome measures (no branching)

5. **⚠️ sample_data is unrealistic**: Lacks "_R" timepoints and edge cases present in real data

### Next Steps:

**IMMEDIATE (Cannot proceed without this):**
- Get answers to Critical Questions 1-4 from Silver & Rick

**AFTER CLARIFICATION:**
- Update sample_data generation to include "_R" timepoints
- Add edge case examples (if appropriate)
- Update documentation with "_R" explanation

**OPTIONAL:**
- Add data quality reporting to integration script
- Decide whether to enhance name-finding logic

---

### Bottom Line:

The integration script correctly transforms the data structure we've identified. The outputs differ between SkinnyActualExampleData and sample_data **not due to errors**, but because:
1. Different timepoints are present (standard vs "_R")
2. Different data completeness levels
3. Real pilot data vs synthetic data

Before generating new sample data, we MUST clarify the meaning and handling of "_R" timepoints with the research team.

---

*Report completed: November 30, 2025*
*Ready for team review and clarification of "_R" timepoint protocol*
