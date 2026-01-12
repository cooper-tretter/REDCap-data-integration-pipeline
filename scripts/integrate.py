"""
REDCap Data Integration Script
==============================

ONE ROW PER PARTICIPANT with comprehensive analytical tabs.

Features:
- Wide format: one row per participant, timepoint-specific columns
- All 50+ questionnaires from the protocol
- Proper consent flow logic with status tracking
- _r timepoints consolidated with standard timepoints (t2_r -> t2, etc.)
- dosing_rescheduled flag preserved at participant level
- Multiple analytical tabs with outcomes and visualizations

IMPORTANT: _r timepoint consolidation
- _r timepoints indicate the dosing session was rescheduled
- Data from _r timepoints is consolidated into the standard timepoint columns
- The dosing_rescheduled flag indicates which participants had rescheduled sessions
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import sys
warnings.filterwarnings('ignore')


# =============================================================================
# TIMEPOINT MAPPING
# =============================================================================

# Internal timepoint mapping (REDCap event names to internal codes)
TIMEPOINT_MAP = {
    'timepoint_1_arm_1': 't1',
    'timepoint_2_arm_1': 't2',
    'timepoint_2_r_arm_1': 't2',
    'timepoint_3_arm_1': 't3',
    'timepoint_3_r_arm_1': 't3',
    'timepoint_4_arm_1': 't4',
    'timepoint_4_r_arm_1': 't4',
    'timepoint_5_arm_1': 't5',
    'timepoint_5_r_arm_1': 't5',
    'timepoint_6_arm_1': 't6',
    'timepoint_6_r_arm_1': 't6',
}

TIMEPOINT_ORDER = ['t1', 't2', 't3', 't4', 't5', 't6']

# Output timepoint labels (for insights output only)
# Per protocol: t1=baseline, t2=3 days, t3=1 month, t4=3 months, t5=6 months, t6=12 months
OUTPUT_TIMEPOINT_LABELS = {
    't1': 'bl',    # Baseline (pre-intervention)
    't2': '3d',    # 3 days post-treatment
    't3': '1mo',   # 1 month post-treatment
    't4': '3mo',   # 3 months post-treatment
    't5': '6mo',   # 6 months post-treatment
    't6': '12mo',  # 12 months post-treatment
}


# =============================================================================
# QUESTIONNAIRE DEFINITIONS - Matches generate_sample_data.py
# =============================================================================

QUESTIONNAIRES = {
    # === PRIMARY OUTCOME MEASURES ===
    'phq9': {
        'name': 'PHQ-9 (Depression)', 'items': 9, 'item_range': (0, 3),
        'total_range': (0, 27), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
        'interpretation': '0-4: None-minimal, 5-9: Mild, 10-14: Moderate, 15-19: Moderately severe, 20-27: Severe',
    },
    'gad7': {
        'name': 'GAD-7 (Anxiety)', 'items': 7, 'item_range': (0, 3),
        'total_range': (0, 21), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
        'interpretation': '0-4: Minimal, 5-9: Mild, 10-14: Moderate, 15-21: Severe',
    },
    'who5': {
        'name': 'WHO-5 (Wellbeing)', 'items': 5, 'item_range': (0, 5),
        'total_range': (0, 100), 'scoring': 'sum_x4', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': False,
        'interpretation': '<28: Poor wellbeing, Higher = better',
    },
    'psyflex': {
        'name': 'PsyFlex (Psychological Flexibility)', 'items': 6, 'item_range': (1, 5),
        'total_range': (6, 30), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': False,
    },
    'auditc': {
        'name': 'AUDIT-C (Alcohol Use - Short)', 'items': 3, 'item_range': (0, 4),
        'total_range': (0, 12), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
        'short_version_of': 'audit_full',
    },
    'audit_full': {
        'name': 'AUDIT (Alcohol Use - Full)', 'items': 10, 'item_range': (0, 4),
        'total_range': (0, 40), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
        'item_prefix': 'audit',  # Items 1-3 are auditc_1-3, items 4-10 are audit_4-10
    },

    # === DOSING SESSION MEASURES ===
    'meq4': {
        'name': 'MEQ-4 (Mystical Experience)', 'items': 4, 'item_range': (0, 5),
        'total_range': (0, 5), 'scoring': 'mean', 'timepoints': [2],
        'higher_is_worse': False,
        'interpretation': '>=3.5: Complete mystical experience',
    },
    'ebi': {
        'name': 'EBI (Emotional Breakthrough)', 'items': 6, 'item_range': (0, 5),
        'total_range': (0, 30), 'scoring': 'sum', 'timepoints': [2],
        'higher_is_worse': False,
    },
    'ceq': {
        'name': 'CEQ-7 (Challenging Experience)', 'items': 7, 'item_range': (0, 5),
        'total_range': (0, 35), 'scoring': 'sum', 'timepoints': [2],
        'higher_is_worse': True,
    },
    'piq': {
        'name': 'PIQ (Psychological Insight)', 'items': 23, 'item_range': (1, 5),
        'total_range': (23, 115), 'scoring': 'sum', 'timepoints': [2],
        'higher_is_worse': False,
    },
    'sscs': {
        'name': 'SSCS-S (State Self-Compassion)', 'items': 6, 'item_range': (1, 5),
        'total_range': (6, 30), 'scoring': 'sum', 'timepoints': [2],
        'higher_is_worse': False,
    },
    'mpod_s': {
        'name': 'MPoD-S (State Decentering)', 'items': 3, 'item_range': (1, 5),
        'total_range': (3, 15), 'scoring': 'sum', 'timepoints': [2],
        'higher_is_worse': False,
    },

    # === DEPRESSION/MOOD ===
    'epds': {
        'name': 'EPDS (Edinburgh Postnatal Depression)', 'items': 10, 'item_range': (0, 3),
        'total_range': (0, 30), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'ymrs': {
        'name': 'YMRS (Young Mania Rating)', 'items': 11, 'item_range': (0, 4),
        'total_range': (0, 60), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === ANXIETY ===
    'pdss': {
        'name': 'PDSS (Panic Disorder Severity)', 'items': 7, 'item_range': (0, 4),
        'total_range': (0, 28), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'spin': {
        'name': 'SPIN (Social Phobia Inventory)', 'items': 17, 'item_range': (0, 4),
        'total_range': (0, 68), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'specific_phobia': {
        'name': 'APA Specific Phobia Severity', 'items': 10, 'item_range': (0, 4),
        'total_range': (0, 40), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === TRAUMA ===
    'pcl': {
        'name': 'PCL-S (PTSD Checklist)', 'items': 20, 'item_range': (1, 5),
        'total_range': (20, 100), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'ies_r': {
        'name': 'IES-R (Impact of Events)', 'items': 22, 'item_range': (0, 4),
        'total_range': (0, 88), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'pg13': {
        'name': 'PG-13-R (Prolonged Grief)', 'items': 13, 'item_range': (1, 5),
        'total_range': (13, 65), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === PERSONALITY/FUNCTIONING ===
    'lpfs': {
        'name': 'LPFS-BF (Personality Functioning)', 'items': 12, 'item_range': (1, 4),
        'total_range': (12, 48), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'bsl23': {
        'name': 'BSL-23 (Borderline Symptoms)', 'items': 23, 'item_range': (0, 4),
        'total_range': (0, 92), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === BEHAVIORAL ADDICTIONS ===
    'iat': {
        'name': 'IAT (Internet Addiction)', 'items': 20, 'item_range': (1, 5),
        'total_range': (20, 100), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'sogs': {
        'name': 'SOGS (South Oaks Gambling)', 'items': 20, 'item_range': (0, 1),
        'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'hrs': {
        'name': 'HRS (Hoarding Rating)', 'items': 5, 'item_range': (0, 8),
        'total_range': (0, 40), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === OCD ===
    'ybocs': {
        'name': 'Y-BOCS (OCD Severity)', 'items': 10, 'item_range': (0, 4),
        'total_range': (0, 40), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === NEURODEVELOPMENTAL ===
    'asq': {
        'name': 'ASQ (Autism Spectrum Quotient)', 'items': 28, 'item_range': (0, 1),
        'total_range': (0, 28), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'asrs': {
        'name': 'ASRS (ADHD Self-Report)', 'items': 18, 'item_range': (0, 4),
        'total_range': (0, 72), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'atq': {
        'name': 'ATQ (Adult Tic Questionnaire)', 'items': 20, 'item_range': (0, 4),
        'total_range': (0, 80), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'cpib': {
        'name': 'CPIB-SF (Communicative Participation)', 'items': 10, 'item_range': (0, 3),
        'total_range': (0, 30), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': False,
    },

    # === PSYCHOTIC ===
    'panss': {
        'name': 'PANSS (Positive/Negative Syndrome)', 'items': 30, 'item_range': (1, 7),
        'total_range': (30, 210), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === DISSOCIATIVE/EATING ===
    'dss': {
        'name': 'DSS-B (Dissociative Symptoms)', 'items': 8, 'item_range': (0, 4),
        'total_range': (0, 32), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'edeqs': {
        'name': 'EDE-QS (Eating Disorder)', 'items': 12, 'item_range': (0, 3),
        'total_range': (0, 36), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === SLEEP/COGNITIVE ===
    'psqi': {
        'name': 'PSQI (Sleep Quality)', 'items': 7, 'item_range': (0, 3),
        'total_range': (0, 21), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'cfq': {
        'name': 'CFQ (Cognitive Failures)', 'items': 25, 'item_range': (0, 4),
        'total_range': (0, 100), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === PAIN ===
    'peg': {
        'name': 'PEG (Pain Scale)', 'items': 3, 'item_range': (0, 10),
        'total_range': (0, 30), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === ALL TIMEPOINTS ===
    'rrs': {
        'name': 'RRS (Rumination)', 'items': 22, 'item_range': (1, 4),
        'total_range': (22, 88), 'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'bcss': {
        'name': 'BCSS (Brief Core Schema)', 'items': 24, 'item_range': (0, 4),
        'total_range': (0, 96), 'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'bis': {
        'name': 'BIS (Impulsiveness)', 'items': 8, 'item_range': (1, 4),
        'total_range': (8, 32), 'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'higher_is_worse': True,
    },
    'bfi10': {
        'name': 'BFI-10 (Big Five Personality)', 'items': 10, 'item_range': (1, 5),
        'total_range': (10, 50), 'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'higher_is_worse': False,
    },
    'mpod_t': {
        'name': 'MPoD-T (Trait Decentering)', 'items': 15, 'item_range': (1, 5),
        'total_range': (15, 75), 'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'higher_is_worse': False,
    },

    # === SATISFACTION ===
    'csq8': {
        'name': 'CSQ-8 (Client Satisfaction)', 'items': 8, 'item_range': (1, 4),
        'total_range': (8, 32), 'scoring': 'sum', 'timepoints': [3],
        'higher_is_worse': False,
    },

    # === BASELINE ONLY ===
    'expectancy': {
        'name': 'Expectancy Measure', 'items': 1, 'item_range': (0, 10),
        'total_range': (0, 10), 'scoring': 'single', 'timepoints': [1],
        'higher_is_worse': False,
    },

    # === SIDE EFFECTS ===
    'swiss_se': {
        'name': 'Swiss Psychedelic Side Effects', 'items': 32, 'item_range': (0, 5),
        'total_range': (0, 160), 'scoring': 'sum', 'timepoints': [2, 3, 4, 5, 6],
        'higher_is_worse': True,
    },

    # === SUBSTANCE USE ===
    'nida_cannabis': {'name': 'NIDA-ASSIST Cannabis', 'items': 5, 'item_range': (0, 4), 'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6], 'higher_is_worse': True},
    'nida_cocaine': {'name': 'NIDA-ASSIST Cocaine', 'items': 5, 'item_range': (0, 4), 'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6], 'higher_is_worse': True},
    'nida_stimulants': {'name': 'NIDA-ASSIST Stimulants', 'items': 5, 'item_range': (0, 4), 'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6], 'higher_is_worse': True},
    'nida_meth': {'name': 'NIDA-ASSIST Methamphetamine', 'items': 5, 'item_range': (0, 4), 'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6], 'higher_is_worse': True},
    'nida_inhalants': {'name': 'NIDA-ASSIST Inhalants', 'items': 5, 'item_range': (0, 4), 'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6], 'higher_is_worse': True},
    'nida_sedatives': {'name': 'NIDA-ASSIST Sedatives', 'items': 5, 'item_range': (0, 4), 'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6], 'higher_is_worse': True},
    'nida_hallucinogens': {'name': 'NIDA-ASSIST Hallucinogens', 'items': 5, 'item_range': (0, 4), 'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6], 'higher_is_worse': True},
    'nida_street_opioids': {'name': 'NIDA-ASSIST Street Opioids', 'items': 5, 'item_range': (0, 4), 'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6], 'higher_is_worse': True},
    'nida_rx_opioids': {'name': 'NIDA-ASSIST Prescription Opioids', 'items': 5, 'item_range': (0, 4), 'total_range': (0, 20), 'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6], 'higher_is_worse': True},
}


# =============================================================================
# SCORING FUNCTIONS
# =============================================================================

def calc_sum(row, items):
    vals = [row[i] for i in items if i in row.index and pd.notna(row[i])]
    return sum(vals) if len(vals) == len(items) else np.nan


def calc_mean(row, items):
    vals = [row[i] for i in items if i in row.index and pd.notna(row[i])]
    return np.mean(vals) if len(vals) == len(items) else np.nan


def phq9_severity(score):
    if pd.isna(score): return np.nan
    elif score < 5: return 'None-minimal'
    elif score < 10: return 'Mild'
    elif score < 15: return 'Moderate'
    elif score < 20: return 'Moderately severe'
    else: return 'Severe'


def gad7_severity(score):
    if pd.isna(score): return np.nan
    elif score < 5: return 'Minimal'
    elif score < 10: return 'Mild'
    elif score < 15: return 'Moderate'
    else: return 'Severe'


def collapse_checkbox(df, prefix, n_options, labels=None):
    if labels is None:
        labels = {i: f'Option {i}' for i in range(1, n_options + 1)}

    def collapse_row(row):
        selected = [labels[i] for i in range(1, n_options + 1)
                   if f'{prefix}{i}' in row.index and row[f'{prefix}{i}'] == 1]
        return ', '.join(selected) if selected else np.nan

    return df.apply(collapse_row, axis=1)


# =============================================================================
# DETERMINE RESCHEDULED STATUS
# =============================================================================

def determine_dosing_rescheduled(df):
    rescheduled_info = []
    for record_id in df['record_id'].unique():
        participant_events = df[df['record_id'] == record_id]['redcap_event_name'].tolist()
        has_r_events = any('_r_' in event for event in participant_events)
        rescheduled_info.append({
            'record_id': record_id,
            'dosing_rescheduled': has_r_events
        })
    return pd.DataFrame(rescheduled_info)


# =============================================================================
# EXTRACT PARTICIPANT INFO
# =============================================================================

def extract_participant_info(df, df_rescheduled):
    print("   Extracting participant info...")

    all_record_ids = df['record_id'].unique()
    participant_info = []

    for record_id in all_record_ids:
        participant_rows = df[df['record_id'] == record_id]
        info = {'record_id': record_id}

        rescheduled_row = df_rescheduled[df_rescheduled['record_id'] == record_id]
        info['dosing_rescheduled'] = rescheduled_row['dosing_rescheduled'].iloc[0] if len(rescheduled_row) > 0 else False

        baseline_rows = participant_rows[participant_rows['redcap_event_name'] == 'timepoint_1_arm_1']
        has_baseline = len(baseline_rows) > 0
        info['has_baseline'] = has_baseline

        if has_baseline:
            baseline = baseline_rows.iloc[0]

            consent_age = baseline.get('consent_age', np.nan)
            info['consent_age'] = consent_age

            if pd.isna(consent_age):
                info['consent_status'] = 'incomplete'
                info['consent_passed'] = False
            elif consent_age == 0:
                info['consent_status'] = 'failed_age_check'
                info['consent_passed'] = False
            else:
                psilocybin = baseline.get('consent_psilocybintherapy', np.nan)
                info['consent_psilocybintherapy'] = psilocybin

                if pd.isna(psilocybin):
                    info['consent_status'] = 'incomplete'
                    info['consent_passed'] = False
                elif psilocybin == 0:
                    info['consent_status'] = 'failed_psilocybin_check'
                    info['consent_passed'] = False
                else:
                    has_any_name = False
                    for name_field in ['consent_nameprint', 'consent_nameprint_v2', 'consent_nameprint_v3']:
                        if name_field in baseline.index:
                            val = baseline[name_field]
                            if pd.notna(val) and str(val).strip() != '':
                                has_any_name = True
                                break

                    if has_any_name:
                        info['consent_status'] = 'passed'
                        info['consent_passed'] = True
                    else:
                        info['consent_status'] = 'eligible_but_incomplete'
                        info['consent_passed'] = False

            name = None
            for name_field in ['consent_nameprint', 'consent_nameprint_v2', 'consent_nameprint_v3']:
                if name_field in baseline.index:
                    val = baseline[name_field]
                    if pd.notna(val) and str(val).strip() != '':
                        name = val
                        break

            info['consent_nameprint'] = name

            email = None
            for email_field in ['email', 'email_v2', 'email_v3']:
                if email_field in baseline.index and pd.notna(baseline[email_field]):
                    email = baseline[email_field]
                    break
            info['email'] = email

            demo_vars = ['age', 'gender', 'sex', 'education', 'relat', 'latino',
                        'income_est', 'military_service', 'consent_date']
            for var in demo_vars:
                if var in baseline.index:
                    info[var] = baseline[var]

            checkbox_prefixes = [
                ('race1___', 6), ('employ___', 9),
                ('psychiatric_medications___', 8), ('psychedelics_used___', 9),
            ]
            for prefix, n in checkbox_prefixes:
                for i in range(1, n + 1):
                    col = f'{prefix}{i}'
                    if col in baseline.index:
                        info[col] = baseline[col]
        else:
            info['consent_age'] = np.nan
            info['consent_status'] = 'no_baseline'
            info['consent_passed'] = False
            info['consent_nameprint'] = np.nan
            info['email'] = np.nan

        info['events_original'] = ', '.join(participant_rows['redcap_event_name'].tolist())
        info['n_events'] = len(participant_rows)

        consolidated_tps = sorted(set([TIMEPOINT_MAP.get(e, e) for e in participant_rows['redcap_event_name'].tolist()]))
        info['timepoints'] = ', '.join(consolidated_tps)

        participant_info.append(info)

    df_participants = pd.DataFrame(participant_info)

    print(f"   - Total participants: {len(df_participants)}")
    print(f"   - With baseline: {df_participants['has_baseline'].sum()}")
    print(f"   - Consent passed: {df_participants['consent_passed'].sum()}")
    print(f"   - Dosing rescheduled: {df_participants['dosing_rescheduled'].sum()}")

    return df_participants


# =============================================================================
# PIVOT TIME-VARYING DATA
# =============================================================================

def pivot_time_varying(df):
    print("   Pivoting time-varying variables...")

    time_varying = []

    # Build list of all questionnaire item columns
    for q_key, q_info in QUESTIONNAIRES.items():
        # Special handling for audit_full - items are named differently
        if q_key == 'audit_full':
            # audit_full items 1-3 are auditc_1-3 (already added)
            # audit_full items 4-10 are audit_4 through audit_10
            for i in range(4, 11):
                time_varying.append(f'audit_{i}')
            continue

        for i in range(1, q_info['items'] + 1):
            time_varying.append(f'{q_key}_{i}')
        if q_info['scoring'] == 'mean':
            time_varying.append(f'{q_key}_mean')
        else:
            time_varying.append(f'{q_key}_total')

    # Also add audit_remaining_total if it exists
    time_varying.append('audit_remaining_total')

    time_varying.extend(['treatment_date', 'treatment_status'])

    time_varying = [c for c in time_varying if c in df.columns]

    df_wide = df[['record_id', 'redcap_event_name'] + time_varying].copy()
    df_wide['timepoint'] = df_wide['redcap_event_name'].map(TIMEPOINT_MAP)

    pivoted_dfs = []
    for var in time_varying:
        try:
            df_var = df_wide[['record_id', 'timepoint', var]].pivot(
                index='record_id', columns='timepoint', values=var
            )
            df_var.columns = [f'{var}_{col}' for col in df_var.columns]
            pivoted_dfs.append(df_var.reset_index())
        except Exception:
            df_grouped = df_wide.groupby(['record_id', 'timepoint'])[var].first().unstack()
            df_grouped.columns = [f'{var}_{col}' for col in df_grouped.columns]
            pivoted_dfs.append(df_grouped.reset_index())

    if pivoted_dfs:
        df_merged = pivoted_dfs[0]
        for pivoted in pivoted_dfs[1:]:
            df_merged = df_merged.merge(pivoted, on='record_id', how='outer')
        return df_merged
    else:
        return pd.DataFrame({'record_id': df['record_id'].unique()})


# =============================================================================
# CALCULATE SCORES
# =============================================================================

def calculate_all_scores(df):
    print("   Computing scores for all timepoints...")

    for tp in TIMEPOINT_ORDER:
        tp_num = int(tp[1])

        for q_key, q_info in QUESTIONNAIRES.items():
            if tp_num not in q_info['timepoints']:
                continue

            # Special handling for AUDIT full (combines auditc_1-3 and audit_4-10)
            if q_key == 'audit_full':
                auditc_items = [f'auditc_{i}_{tp}' for i in range(1, 4)]
                audit_items = [f'audit_{i}_{tp}' for i in range(4, 11)]
                all_items = auditc_items + audit_items

                # Check if AUDIT-C items exist
                has_auditc = all(c in df.columns for c in auditc_items)
                # Check if remaining AUDIT items exist
                has_audit_remaining = all(c in df.columns for c in audit_items)

                if has_auditc and has_audit_remaining:
                    # Calculate full AUDIT score
                    df[f'audit_full_total_{tp}'] = df.apply(lambda row: calc_sum(row, all_items), axis=1)
                    # Add version indicator
                    df[f'audit_version_{tp}'] = df.apply(
                        lambda row: 'full' if pd.notna(calc_sum(row, audit_items)) else
                                   ('short' if pd.notna(calc_sum(row, auditc_items)) else np.nan),
                        axis=1
                    )
                elif has_auditc:
                    # Only short version available
                    df[f'audit_version_{tp}'] = df.apply(
                        lambda row: 'short' if pd.notna(calc_sum(row, auditc_items)) else np.nan,
                        axis=1
                    )
                continue

            # Skip auditc here since we handle it in the audit_full block
            if q_key == 'auditc':
                items = [f'{q_key}_{i}_{tp}' for i in range(1, q_info['items'] + 1)]
                if all(c in df.columns for c in items):
                    df[f'{q_key}_total_{tp}'] = df.apply(lambda row: calc_sum(row, items), axis=1)
                continue

            items = [f'{q_key}_{i}_{tp}' for i in range(1, q_info['items'] + 1)]

            if not all(c in df.columns for c in items):
                continue

            if q_info['scoring'] == 'mean':
                df[f'{q_key}_total_{tp}'] = df.apply(lambda row: calc_mean(row, items), axis=1)
            elif q_info['scoring'] == 'sum_x4':
                raw_sum = df.apply(lambda row: calc_sum(row, items), axis=1)
                df[f'{q_key}_total_{tp}'] = raw_sum * 4
            else:
                df[f'{q_key}_total_{tp}'] = df.apply(lambda row: calc_sum(row, items), axis=1)

        # Add severity classifications for key scales
        if f'phq9_total_{tp}' in df.columns:
            df[f'phq9_severity_{tp}'] = df[f'phq9_total_{tp}'].apply(phq9_severity)
        if f'gad7_total_{tp}' in df.columns:
            df[f'gad7_severity_{tp}'] = df[f'gad7_total_{tp}'].apply(gad7_severity)
        if f'meq4_total_{tp}' in df.columns:
            df[f'meq4_mystical_{tp}'] = df[f'meq4_total_{tp}'].apply(
                lambda x: 'Yes' if pd.notna(x) and x >= 3.5 else ('No' if pd.notna(x) else np.nan)
            )

    return df


# =============================================================================
# ANALYTICAL TABS
# =============================================================================

def create_scale_summary(df, scale_name):
    summary_data = []
    for tp in TIMEPOINT_ORDER:
        col = f'{scale_name}_{tp}'
        if col in df.columns:
            n = df[col].notna().sum()
            if n > 0:
                summary_data.append({
                    'Timepoint': tp, 'N': n,
                    'Mean': round(df[col].mean(), 2),
                    'SD': round(df[col].std(), 2),
                    'Median': round(df[col].median(), 2),
                    'Min': df[col].min(), 'Max': df[col].max(),
                })
    return pd.DataFrame(summary_data)


def create_improvement_analysis(df, scale_name, baseline='t1', higher_is_worse=True):
    improvement_data = []
    baseline_col = f'{scale_name}_{baseline}'
    if baseline_col not in df.columns:
        return pd.DataFrame()

    for tp in ['t3', 't4', 't5', 't6']:
        tp_col = f'{scale_name}_{tp}'
        if tp_col in df.columns:
            both = df[baseline_col].notna() & df[tp_col].notna()
            if both.sum() > 0:
                df_paired = df[both].copy()
                df_paired['change'] = df_paired[tp_col] - df_paired[baseline_col]

                if higher_is_worse:
                    df_paired['responder'] = df_paired['change'] <= -0.5 * df_paired[baseline_col]
                    df_paired['improved'] = df_paired['change'] < 0
                else:
                    df_paired['responder'] = df_paired['change'] >= 0.5 * df_paired[baseline_col]
                    df_paired['improved'] = df_paired['change'] > 0

                improvement_data.append({
                    'Comparison': f'{baseline} to {tp}',
                    'N_paired': len(df_paired),
                    'Mean_baseline': round(df_paired[baseline_col].mean(), 2),
                    'Mean_followup': round(df_paired[tp_col].mean(), 2),
                    'Mean_change': round(df_paired['change'].mean(), 2),
                    'Improved_N': df_paired['improved'].sum(),
                    'Improved_pct': round(df_paired['improved'].mean() * 100, 1),
                    'Responders_N': df_paired['responder'].sum(),
                    'Responders_pct': round(df_paired['responder'].mean() * 100, 1),
                })

    return pd.DataFrame(improvement_data)


def create_demographics_summary(df):
    print("   Creating demographics summary...")

    df_consented = df[df['consent_passed'] == True].copy()
    if len(df_consented) == 0:
        return pd.DataFrame({'Note': ['No consented participants found']})

    summary = {'Variable': [], 'Category': [], 'N': [], 'Percent': []}

    if 'age' in df_consented.columns:
        age_valid = df_consented['age'].dropna()
        if len(age_valid) > 0:
            summary['Variable'].append('Age')
            summary['Category'].append('Mean (SD)')
            summary['N'].append(f"{age_valid.mean():.1f} ({age_valid.std():.1f})")
            summary['Percent'].append('')

    if 'dosing_rescheduled' in df_consented.columns:
        rescheduled = df_consented['dosing_rescheduled'].sum()
        total = len(df_consented)
        summary['Variable'].append('Dosing Rescheduled')
        summary['Category'].append('Yes')
        summary['N'].append(rescheduled)
        summary['Percent'].append(f"{100*rescheduled/total:.1f}%" if total > 0 else '')

    if 'gender' in df_consented.columns:
        for code, label in {1: 'Male', 2: 'Female', 3: 'Non-binary', 4: 'Other'}.items():
            count = (df_consented['gender'] == code).sum()
            if count > 0:
                summary['Variable'].append('Gender')
                summary['Category'].append(label)
                summary['N'].append(count)
                total = df_consented['gender'].notna().sum()
                summary['Percent'].append(f"{100*count/total:.1f}%" if total > 0 else '')

    return pd.DataFrame(summary)


def create_completeness_summary(df):
    print("   Creating completeness summary...")

    scales = ['phq9_total', 'gad7_total', 'who5_total', 'psyflex_total',
              'auditc_total', 'meq4_total', 'ebi_total', 'piq_total', 'ceq_total',
              'rrs_total', 'bcss_total', 'pcl_total', 'ies_r_total']

    completeness_data = []
    for tp in TIMEPOINT_ORDER:
        row = {'Timepoint': tp}
        for scale in scales:
            col = f'{scale}_{tp}'
            row[scale] = df[col].notna().sum() if col in df.columns else 0
        completeness_data.append(row)

    return pd.DataFrame(completeness_data)


def create_summary_tab(df):
    print("   Creating summary tab...")

    summary_data = []
    scales = {
        'phq9_total': 'PHQ9', 'gad7_total': 'GAD7', 'who5_total': 'WHO5',
        'meq4_total': 'MEQ4', 'psyflex_total': 'PsyFlex', 'auditc_total': 'AUDIT-C',
        'ebi_total': 'EBI', 'piq_total': 'PIQ', 'ceq_total': 'CEQ',
    }

    for _, row in df.iterrows():
        summary_row = {
            'record_id': row['record_id'],
            'consent_nameprint': row.get('consent_nameprint', np.nan),
            'consent_status': row.get('consent_status', np.nan),
            'dosing_rescheduled': row.get('dosing_rescheduled', np.nan),
            'age': row.get('age', np.nan),
            'gender': row.get('gender', np.nan),
            'n_events': row.get('n_events', np.nan),
            'timepoints': row.get('timepoints', np.nan),
        }

        for scale_base, scale_label in scales.items():
            first_val, first_tp = np.nan, None
            last_val, last_tp = np.nan, None

            for tp in TIMEPOINT_ORDER:
                col = f'{scale_base}_{tp}'
                if col in row.index and pd.notna(row[col]):
                    if pd.isna(first_val):
                        first_val, first_tp = row[col], tp
                    last_val, last_tp = row[col], tp

            summary_row[f'{scale_base}_first'] = first_val
            summary_row[f'{scale_base}_last'] = last_val

            if pd.notna(first_val) and pd.notna(last_val) and first_tp != last_tp:
                summary_row[f'{scale_base}_change'] = last_val - first_val
            else:
                summary_row[f'{scale_base}_change'] = np.nan

        summary_data.append(summary_row)

    return pd.DataFrame(summary_data)


def create_calculations_tab():
    calculations = []
    for q_key, q_info in QUESTIONNAIRES.items():
        tps = ', '.join([f't{t}' for t in q_info['timepoints']])
        calculations.append({
            'Measure': q_info['name'],
            'Score Name': f'{q_key}_total',
            'Calculation': f"{q_info['scoring']} of {q_info['items']} items",
            'Item Range': f"{q_info['item_range'][0]}-{q_info['item_range'][1]}",
            'Total Range': f"{q_info['total_range'][0]}-{q_info['total_range'][1]}",
            'Timepoints': tps,
            'Higher is Worse': q_info['higher_is_worse'],
            'Interpretation': q_info.get('interpretation', ''),
        })

    return pd.DataFrame(calculations)


# =============================================================================
# MAIN INTEGRATION
# =============================================================================

def integrate_full(input_path, output_dir=None):
    print("=" * 80)
    print("REDCap Data Integration")
    print(f"Questionnaires: {len(QUESTIONNAIRES)}")
    print("=" * 80)

    print(f"\n1. Reading data: {input_path}")
    df = pd.read_excel(input_path) if str(input_path).endswith('.xlsx') else pd.read_csv(input_path)
    print(f"   - Original: {len(df)} rows x {len(df.columns)} columns")
    print(f"   - Unique participants: {df['record_id'].nunique()}")

    r_events = df[df['redcap_event_name'].str.contains('_r_', na=False)]
    print(f"   - Rows with _r timepoints: {len(r_events)}")

    output_dir = Path(output_dir or Path(input_path).parent)

    print("\n2. Determining dosing rescheduled status...")
    df_rescheduled = determine_dosing_rescheduled(df)
    print(f"   - Participants with rescheduled dosing: {df_rescheduled['dosing_rescheduled'].sum()}")

    print("\n3. Extracting participant info...")
    df_participants = extract_participant_info(df, df_rescheduled)

    print("\n4. Pivoting time-varying data...")
    df_time_varying = pivot_time_varying(df)

    print("\n5. Merging data...")
    df_wide = df_participants.merge(df_time_varying, on='record_id', how='left')
    print(f"   - Result: {len(df_wide)} rows x {len(df_wide.columns)} columns")

    print("\n6. Collapsing checkbox fields...")
    checkbox_defs = {
        'race1___': (6, {1: 'AI/AN', 2: 'Asian', 3: 'Black', 4: 'NH/PI', 5: 'White', 6: 'Other'}),
        'employ___': (9, None),
        'psychiatric_medications___': (8, None),
        'psychedelics_used___': (9, {1: 'Psilocybin', 2: 'LSD', 3: 'MDMA', 4: 'Ayahuasca',
                                     5: 'DMT', 6: 'Mescaline', 7: 'Ketamine', 8: 'Salvia', 9: 'Other'}),
    }

    for prefix, (n, labels) in checkbox_defs.items():
        cols = [f'{prefix}{i}' for i in range(1, n + 1)]
        if any(c in df_wide.columns for c in cols):
            new_name = prefix.rstrip('_').replace('___', '')
            df_wide[new_name] = collapse_checkbox(df_wide, prefix, n, labels)
            df_wide.drop(columns=[c for c in cols if c in df_wide.columns], inplace=True, errors='ignore')

    print("\n7. Computing all scores...")
    df_wide = calculate_all_scores(df_wide)

    print("\n8. Creating analytical tabs...")
    df_summary = create_summary_tab(df_wide)
    df_demographics = create_demographics_summary(df_wide)
    df_completeness = create_completeness_summary(df_wide)

    df_phq9_summary = create_scale_summary(df_wide, 'phq9_total')
    df_phq9_outcomes = create_improvement_analysis(df_wide, 'phq9_total', higher_is_worse=True)

    df_gad7_summary = create_scale_summary(df_wide, 'gad7_total')
    df_gad7_outcomes = create_improvement_analysis(df_wide, 'gad7_total', higher_is_worse=True)

    df_who5_summary = create_scale_summary(df_wide, 'who5_total')
    df_who5_outcomes = create_improvement_analysis(df_wide, 'who5_total', higher_is_worse=False)

    df_calculations = create_calculations_tab()

    print("\n9. Renaming timepoint columns for output...")
    # Rename columns: _t1 -> _bl, _t2 -> _3d, _t3 -> _1mo, etc.
    def rename_timepoint_columns(df):
        rename_map = {}
        for col in df.columns:
            new_col = col
            for internal, output in OUTPUT_TIMEPOINT_LABELS.items():
                # Replace _t1, _t2, etc. at end of column names
                if col.endswith(f'_{internal}'):
                    new_col = col[:-len(f'_{internal}')] + f'_{output}'
                    break
            if new_col != col:
                rename_map[col] = new_col
        return df.rename(columns=rename_map)

    # Also update the 'timepoints' column values
    def rename_timepoints_value(val):
        if pd.isna(val):
            return val
        result = str(val)
        for internal, output in OUTPUT_TIMEPOINT_LABELS.items():
            result = result.replace(internal, output)
        return result

    df_wide = rename_timepoint_columns(df_wide)
    if 'timepoints' in df_wide.columns:
        df_wide['timepoints'] = df_wide['timepoints'].apply(rename_timepoints_value)

    df_summary = rename_timepoint_columns(df_summary)
    df_completeness = rename_timepoint_columns(df_completeness)
    if 'Timepoint' in df_completeness.columns:
        df_completeness['Timepoint'] = df_completeness['Timepoint'].apply(rename_timepoints_value)

    df_phq9_summary = rename_timepoint_columns(df_phq9_summary)
    if 'Timepoint' in df_phq9_summary.columns:
        df_phq9_summary['Timepoint'] = df_phq9_summary['Timepoint'].apply(rename_timepoints_value)
    df_phq9_outcomes = rename_timepoint_columns(df_phq9_outcomes)
    if 'Comparison' in df_phq9_outcomes.columns:
        df_phq9_outcomes['Comparison'] = df_phq9_outcomes['Comparison'].apply(rename_timepoints_value)

    df_gad7_summary = rename_timepoint_columns(df_gad7_summary)
    if 'Timepoint' in df_gad7_summary.columns:
        df_gad7_summary['Timepoint'] = df_gad7_summary['Timepoint'].apply(rename_timepoints_value)
    df_gad7_outcomes = rename_timepoint_columns(df_gad7_outcomes)
    if 'Comparison' in df_gad7_outcomes.columns:
        df_gad7_outcomes['Comparison'] = df_gad7_outcomes['Comparison'].apply(rename_timepoints_value)

    df_who5_summary = rename_timepoint_columns(df_who5_summary)
    if 'Timepoint' in df_who5_summary.columns:
        df_who5_summary['Timepoint'] = df_who5_summary['Timepoint'].apply(rename_timepoints_value)
    df_who5_outcomes = rename_timepoint_columns(df_who5_outcomes)
    if 'Comparison' in df_who5_outcomes.columns:
        df_who5_outcomes['Comparison'] = df_who5_outcomes['Comparison'].apply(rename_timepoints_value)

    # Update calculations tab timepoints
    if 'Timepoints' in df_calculations.columns:
        df_calculations['Timepoints'] = df_calculations['Timepoints'].apply(rename_timepoints_value)

    # Reorder columns: short questionnaire columns before long questionnaire columns
    def reorder_short_long_columns(df):
        """Reorder columns so short questionnaire versions come before long versions."""
        cols = list(df.columns)

        # Define short/long column patterns
        # Short version columns (should come first)
        short_patterns = ['auditc_']
        # Long version columns (should come after short)
        long_patterns = ['audit_4', 'audit_5', 'audit_6', 'audit_7', 'audit_8',
                        'audit_9', 'audit_10', 'audit_remaining', 'audit_full', 'audit_version']

        # Separate columns into categories
        non_questionnaire = []  # record_id, demographics, etc.
        short_cols = []
        long_cols = []
        other_questionnaire = []

        for col in cols:
            is_short = any(col.startswith(p) for p in short_patterns)
            is_long = any(col.startswith(p) for p in long_patterns)

            if is_short:
                short_cols.append(col)
            elif is_long:
                long_cols.append(col)
            elif any(col.startswith(f'{q}_') for q in QUESTIONNAIRES.keys() if q not in ['auditc', 'audit_full']):
                other_questionnaire.append(col)
            else:
                non_questionnaire.append(col)

        # Rebuild column order: non-questionnaire, other questionnaires, short, long
        new_order = non_questionnaire + other_questionnaire + short_cols + long_cols

        # Only include columns that exist
        new_order = [c for c in new_order if c in df.columns]

        # Add any columns we might have missed
        for c in cols:
            if c not in new_order:
                new_order.append(c)

        return df[new_order]

    df_wide = reorder_short_long_columns(df_wide)

    print("\n10. Saving outputs...")
    excel_output = output_dir / 'insights.xlsx'

    with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
        df_wide.to_excel(writer, sheet_name='Main Data', index=False)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
        df_demographics.to_excel(writer, sheet_name='Demographics', index=False)
        df_completeness.to_excel(writer, sheet_name='Data Completeness', index=False)

        if not df_phq9_summary.empty:
            df_phq9_summary.to_excel(writer, sheet_name='PHQ9 Summary', index=False)
        if not df_phq9_outcomes.empty:
            df_phq9_outcomes.to_excel(writer, sheet_name='PHQ9 Outcomes', index=False)

        if not df_gad7_summary.empty:
            df_gad7_summary.to_excel(writer, sheet_name='GAD7 Summary', index=False)
        if not df_gad7_outcomes.empty:
            df_gad7_outcomes.to_excel(writer, sheet_name='GAD7 Outcomes', index=False)

        if not df_who5_summary.empty:
            df_who5_summary.to_excel(writer, sheet_name='WHO5 Summary', index=False)
        if not df_who5_outcomes.empty:
            df_who5_outcomes.to_excel(writer, sheet_name='WHO5 Outcomes', index=False)

        df_calculations.to_excel(writer, sheet_name='Calculations', index=False)

    print(f"   - Saved: {excel_output}")

    csv_output = output_dir / 'insights.csv'
    df_wide.to_csv(csv_output, index=False)
    print(f"   - Saved: {csv_output}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Input: {len(df)} rows (long format)")
    print(f"Output: {len(df_wide)} rows (wide format)")
    print(f"Columns: {len(df_wide.columns)}")
    print(f"Dosing Rescheduled: {df_wide['dosing_rescheduled'].sum()} participants")

    print("\nData Availability by Scale (any timepoint):")
    for scale in ['phq9_total', 'gad7_total', 'who5_total', 'meq4_total', 'rrs_total', 'pcl_total']:
        cols = [c for c in df_wide.columns if c.startswith(f'{scale}_t')]
        if cols:
            any_data = df_wide[cols].notna().any(axis=1).sum()
            print(f"  - {scale}: {any_data} participants")

    print("\n" + "=" * 80)
    print("Integration complete!")
    print("=" * 80)

    return df_wide


if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = Path(__file__).parent.parent / 'data' / 'sample_data.xlsx'

    if len(sys.argv) > 2:
        output_directory = Path(sys.argv[2])
    else:
        output_directory = Path(input_file).parent

    print(f"Input file: {input_file}")
    print(f"Output directory: {output_directory}\n")

    df_analytic = integrate_full(input_file, output_directory)

    print("\nPreview (first 10 participants):")
    cols = ['record_id', 'consent_nameprint', 'dosing_rescheduled', 'age', 'timepoints']
    cols = [c for c in cols if c in df_analytic.columns]
    print(df_analytic[cols].head(10).to_string())
