# Proposal: Streamlining PATh Lab’s REDCap Data for Analysis & Reporting

## 1\) Overall problem

Right now, our REDCap exports are so wide and branching that the signal gets lost in the noise. The team needs a way to (a) see the “few things that matter” quickly, (b) consistently compute and view key scores (e.g., PHQ‑9), and (c) collapse checkbox-style variables (e.g., demographics) into usable, single columns—without building heavy infrastructure or introducing compliance risk.

What I observed from the example export you sent:

- 1,574 columns (very wide).  
- Multiple timepoints and arms via `redcap_event_name` (e.g., `timepoint_1_arm_1`, `timepoint_2_r_arm_1`, etc.).  
- Standard scales present (e.g., PHQ‑9: `phq9_1`–`phq9_9`, `phq9_totalscore`; GAD‑7; PSQI; PCL; AUDIT‑C and full AUDIT; NIDA ASSIST modules).  
- Typical REDCap checkbox fields (e.g., \*\*race\*\* as \`race1\_\_\_1\`…\`race1\_\_\_6\`) that need collapsing for analysis.    
- Many instrument admin columns: \~83 `*_timestamp` and \~83 `*_complete` fields that are useful operationally but usually clutter analysis views.

---

## 2\) Current issues (as I understand them)

1) The export is too large to scan easily — we just want the essentials by cohort/timepoint — and some data is distributed where one person might have taken, e.g., PHQ9 at Timepoint x and another at timepoint y and the phq9 data is in different locations. What we want instead is for all the same data to be in the same place, and for there to just be a variable, e.g. timepoint arm 1, timepoint arm 2, etc.  
2) Key information is spread across many columns — especially checkbox fields (e.g., race) and instrument-specific items.  
3) Different respondents see different items (short vs. long forms, branching logic), which complicates “apples-to-apples” views.  
4) Scores vs. items — some totals exist (e.g., `phq9_totalscore`), others need consistent computation/validation.  
5) Operational columns mix with analytic columns — timestamps and “complete” flags are necessary for QA but get in the way.

---

## 3\) Key questions, answered

What do you need to decide from this data?

- Needs to be analyzed with SBSS (likely, since it’s used for social science drag-and-drop analysis) or R or python


Scope & content

- Any scoring rules we should standardize/validate (reverse-coded items, missingness rules, cut scores, severity bands)?  
  - Note. We will individual scores, but we will also want one tab that has the overall totals view (e.g., for each participant, PHQ9 totals, mystical experiences totals, etc.)

- On summing or reverse coding.  
  - IF individual scores are missing, we will want to reverse score them from the total. Be sure to mark reverse scores with an R (follow standard procedure in psychological/social science research)  
  - If a sum/avg/total score column is missing, we will want to create our own column. Be sure to follow standard procedure for the tool at hand. If it’s usually a sum, do a sum, if it’s usually an average do an average (Or, if there is a total column and just the value is missing, note that we will want to sum that value)

---

## 4\) Proposed solution

### Simple Python “cleaner” to output a tidy Excel/CSVWhat it is: A small, documented script that:

- Selects the core columns (ID, event, a handful of demographics).  
- Computes/validates key scores (PHQ‑9, GAD‑7, etc.) from items where needed.  
- Collapses checkboxes (e.g., `race1___*` → `race_omb`) using the REDCap codebook labels.  
- Drops/archives `*_timestamp` and `*_complete` into a separate “audit” output.  
- Produces a thin analytic file (one row per participant × timepoint) for downstream use.

## 5\) On generating a sample dataset

At some point, you will need to generate data so we can play with it and not use any actual confidential information. Follow these guidelines:

* For names, use famous psychonaut names like Albert Hofmann, Ann Shulgin, Sasha Shulgin, Michael Mithoefer, Annie Mithoefer, etc. Do research to find a big list, we’ll want at least 120 rows of data  
* Take note of required fields in the excel codebook I’ll have you generate. If it’s a required field, be sure to generate data there. If it’s not and a participant *could* leave it blank, be sure to have a few lines of data where the data is blank so that we can test reverse coding, summing, etc.