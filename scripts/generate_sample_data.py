"""
Generate REALISTIC sample dataset with consistent psychological profiles
and typical psychedelic therapy outcomes.

KEY FEATURES:
- Consistent psychological profiles (e.g., if anxious at baseline, consistently anxious)
- Realistic treatment responses (60-70% responders)
- Mystical experiences that correlate with outcomes
- Correct questionnaire-timepoint mapping per protocol
- Proper handling of rescheduled dosing sessions:
  - Participants either have ALL _r timepoints or ALL non-_r timepoints
  - A dosing_rescheduled flag tracks this at participant level
  - Data is consolidated so _r and non-_r feed into same analysis columns

TIMEPOINT-QUESTIONNAIRE MAPPING (per codebook):
- t1 (baseline): Demographics, consent, PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C, Expectancy
- t2 (dosing): MEQ-4, EBI, CEQ, PIQ, SSCS-S, MPoD-S, RRS, BCSS, BIS, BFI-10
  NOTE: PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C are NOT administered at t2
- t3-t6 (follow-ups): PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C, RRS, BCSS, BIS, BFI-10
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Famous psychonauts and researchers
PSYCHONAUT_NAMES = [
    ("Albert", "Hofmann"), ("Alexander", "Shulgin"), ("Ann", "Shulgin"),
    ("Michael", "Mithoefer"), ("Annie", "Mithoefer"), ("Timothy", "Leary"),
    ("Richard", "Alpert"), ("Terence", "McKenna"), ("Dennis", "McKenna"),
    ("Aldous", "Huxley"), ("Maria", "Sabina"), ("Stanislav", "Grof"),
    ("Christina", "Grof"), ("Ralph", "Metzner"), ("Rick", "Doblin"),
    ("Amanda", "Feilding"), ("Roland", "Griffiths"), ("Matthew", "Johnson"),
    ("Robin", "Carhart-Harris"), ("David", "Nutt"), ("Charles", "Grob"),
    ("Julie", "Holland"), ("James", "Fadiman"), ("Ram", "Dass"),
    ("Humphry", "Osmond"), ("Abram", "Hoffer"), ("Myron", "Stolaroff"),
    ("Al", "Hubbard"), ("Oscar", "Janiger"), ("Leo", "Zeff"),
    ("Claudio", "Naranjo"), ("Laura", "Huxley"), ("Anais", "Nin"),
    ("Ken", "Kesey"), ("Robert", "Wilson"), ("John", "Lilly"),
    ("Sasha", "Shulgin"), ("David", "Nichols"), ("Rick", "Strassman"),
    ("Stephen", "Ross"), ("Charles", "Tart"), ("Willis", "Harman"),
    ("George", "Greer"), ("Requa", "Tolbert"), ("Philip", "Wolfson"),
    ("Janis", "Phelps"), ("Alicia", "Danforth"), ("Francoise", "Bourzat"),
    ("Gabor", "Mate"), ("Bessel", "van der Kolk"), ("Zendo", "Project"),
    ("Kathryn", "MacRae"), ("William", "Richards"), ("Mary", "Cosimano"),
    ("Mendel", "Kaelen"), ("Rosalind", "Watts"), ("Leor", "Roseman"),
    ("David", "Yaden"), ("Christopher", "Timmermann"), ("Emma", "Hapke"),
    ("Natalie", "Gukasyan"), ("Frederick", "Barrett"), ("Albert", "Garcia-Romeu"),
    ("Peter", "Hendricks"), ("Lisa", "Jerome"), ("Marcela", "Otalora"),
    ("Berra", "Yazar-Klosinski"), ("Amy", "Emerson"), ("Ingmar", "Gorman"),
    ("Talia", "Puzantian"), ("Saj", "Razvi"), ("Randall", "Tackett"),
    ("Shannon", "Carlin"), ("Elizabeth", "Nielson"), ("Friederike", "Fischer"),
    ("Henrik", "Jungaberle"), ("Torsten", "Passie"), ("Franz", "Vollenweider"),
    ("Michael", "Pollan"), ("Ayelet", "Waldman"), ("Paul", "Stamets"),
    ("Kathleen", "Harrison"), ("Jonathan", "Ott"), ("Jeremy", "Narby"),
    ("Wade", "Davis"), ("Giorgio", "Samorini"), ("Christian", "Ratsch"),
    ("Dale", "Pendell"), ("Daniel", "Pinchbeck"), ("Graham", "Hancock"),
    ("Rupert", "Sheldrake"), ("Andrew", "Weil"), ("Carl", "Ruck"),
    ("Gordon", "Wasson"), ("Valentina", "Wasson"), ("Sidney", "Cohen"),
    ("Betty", "Eisner"), ("Jan", "Bastiaans"), ("Hanscarl", "Leuner"),
    ("Walter", "Pahnke"), ("William", "McGlothlin"), ("Louis", "West"),
    ("Huston", "Smith"), ("Walter", "Clark"), ("Stephen", "Gray"),
    ("Kathleen", "Hatcher"), ("Nicolas", "Langlitz"), ("Erika", "Dyck"),
    ("Matthew", "Oram"), ("Bia", "Labate"), ("Clancy", "Cavnar"),
    ("Kenneth", "Tupper"), ("Thomas", "Roberts"), ("Charles", "Savage"),
]

# Ensure we have 120 names
while len(PSYCHONAUT_NAMES) < 120:
    PSYCHONAUT_NAMES.append((f"Researcher{len(PSYCHONAUT_NAMES)}", f"Name{len(PSYCHONAUT_NAMES)}"))


# =============================================================================
# PSYCHOLOGICAL PROFILES
# =============================================================================

PROFILES = {
    'severe_depression': {
        'weight': 20,
        'phq9_baseline': (15, 23),  # Moderately severe to severe
        'gad7_baseline': (8, 14),   # Mild to moderate anxiety
        'who5_baseline': (8, 24),   # Low wellbeing
        'response_prob': 0.65,      # 65% respond to treatment
    },
    'moderate_depression': {
        'weight': 25,
        'phq9_baseline': (10, 18),  # Moderate
        'gad7_baseline': (5, 12),
        'who5_baseline': (16, 40),
        'response_prob': 0.75,
    },
    'high_anxiety': {
        'weight': 20,
        'phq9_baseline': (8, 15),
        'gad7_baseline': (12, 19),  # Moderate to severe anxiety
        'who5_baseline': (20, 44),
        'response_prob': 0.70,
    },
    'comorbid': {
        'weight': 15,
        'phq9_baseline': (14, 22),  # Both high
        'gad7_baseline': (13, 20),
        'who5_baseline': (8, 28),
        'response_prob': 0.55,      # Harder to treat
    },
    'mild_symptoms': {
        'weight': 15,
        'phq9_baseline': (5, 11),   # Mild
        'gad7_baseline': (4, 10),
        'who5_baseline': (32, 56),
        'response_prob': 0.80,      # Easier to treat
    },
    'subclinical': {
        'weight': 5,
        'phq9_baseline': (0, 6),    # Minimal/none
        'gad7_baseline': (0, 6),
        'who5_baseline': (48, 76),
        'response_prob': 0.50,      # Less room for improvement
    },
}


def assign_profile():
    """Assign a psychological profile to a participant."""
    profiles = list(PROFILES.keys())
    weights = [PROFILES[p]['weight'] for p in profiles]
    return random.choices(profiles, weights=weights)[0]


def generate_baseline_scores(profile_name):
    """Generate baseline scores consistent with profile."""
    profile = PROFILES[profile_name]

    phq9 = random.randint(*profile['phq9_baseline'])
    gad7 = random.randint(*profile['gad7_baseline'])
    who5 = random.randint(*profile['who5_baseline'])

    # Add some individual variation
    phq9 = max(0, min(27, phq9 + random.randint(-2, 2)))
    gad7 = max(0, min(21, gad7 + random.randint(-2, 2)))
    who5 = max(0, min(100, who5 + random.randint(-4, 4)))

    return phq9, gad7, who5


def generate_followup_scores(baseline_phq9, baseline_gad7, baseline_who5,
                             timepoint, profile_name, is_responder):
    """
    Generate follow-up scores with realistic treatment response.

    Responders: 40-60% reduction in symptoms
    Non-responders: 0-20% reduction or slight worsening

    Note: timepoint here refers to the logical timepoint (1-6), not _r vs non-_r
    """
    if timepoint == 1:  # Baseline (t1)
        return baseline_phq9, baseline_gad7, baseline_who5

    # Treatment typically happens between t1 and t2
    # Effects start showing at t3, peak at t3-t4, may fade slightly by t5-t6
    # Note: t2 doesn't have PHQ-9/GAD-7/WHO-5 per protocol

    if is_responder:
        if timepoint == 3:  # First follow-up - moderate improvement
            phq9_reduction = random.uniform(0.40, 0.55)
            gad7_reduction = random.uniform(0.35, 0.50)
            who5_improvement = random.uniform(0.40, 0.55)
        elif timepoint == 4:  # Peak improvement
            phq9_reduction = random.uniform(0.50, 0.70)
            gad7_reduction = random.uniform(0.45, 0.65)
            who5_improvement = random.uniform(0.50, 0.70)
        else:  # t5, t6 - sustained but may fade slightly
            phq9_reduction = random.uniform(0.40, 0.60)
            gad7_reduction = random.uniform(0.35, 0.55)
            who5_improvement = random.uniform(0.40, 0.60)
    else:
        # Non-responders: minimal change or slight worsening
        phq9_reduction = random.uniform(-0.10, 0.20)
        gad7_reduction = random.uniform(-0.10, 0.15)
        who5_improvement = random.uniform(-0.10, 0.20)

    # Calculate new scores
    phq9 = baseline_phq9 * (1 - phq9_reduction)
    gad7 = baseline_gad7 * (1 - gad7_reduction)
    who5_raw = baseline_who5 + (100 - baseline_who5) * who5_improvement

    # Add noise
    phq9 = max(0, min(27, phq9 + random.uniform(-2, 2)))
    gad7 = max(0, min(21, gad7 + random.uniform(-1.5, 1.5)))
    who5 = max(0, min(100, who5_raw + random.uniform(-6, 6)))

    return round(phq9), round(gad7), round(who5)


def generate_meq_score(is_responder, profile_name):
    """
    Generate MEQ score (0-5 scale, mean reported).

    Mystical experience (mean >= 3.5) correlates with better outcomes.
    """
    if is_responder:
        # Responders more likely to have mystical experience
        if random.random() < 0.70:  # 70% of responders have mystical exp
            return round(random.uniform(3.5, 5.0), 2)
        else:
            return round(random.uniform(2.0, 3.4), 2)
    else:
        # Non-responders less likely
        if random.random() < 0.30:  # 30% of non-responders have mystical exp
            return round(random.uniform(3.5, 4.5), 2)
        else:
            return round(random.uniform(1.5, 3.2), 2)


def generate_psyflex_score(baseline_phq9, current_phq9):
    """
    Psychological flexibility (6-30 scale, sum of 6 items 1-5 each).
    Higher = more flexible. Improves as depression improves.
    """
    # Base on depression level (inverse relationship)
    base = 30 - (current_phq9 * 0.7)
    score = max(6, min(30, base + random.uniform(-3, 3)))
    return round(score)


def generate_audit_score(age, profile_name):
    """AUDIT-C score (0-12). Younger and more distressed = higher scores."""
    base = 0

    if age < 30:
        base += random.randint(2, 6)
    elif age < 50:
        base += random.randint(1, 4)
    else:
        base += random.randint(0, 3)

    # More severe profiles may have more substance use
    if 'severe' in profile_name or 'comorbid' in profile_name:
        base += random.randint(0, 3)

    return min(12, base)


def generate_ebi_score(is_responder):
    """EBI (Emotional Breakthrough Inventory) - 0-40 scale."""
    if is_responder:
        return round(random.uniform(20, 38))
    else:
        return round(random.uniform(8, 25))


def generate_ceq_score(is_responder):
    """CEQ (Challenging Experience) - 0-35 scale."""
    # Some challenging experiences are normal; very high can be concerning
    base = random.uniform(5, 25)
    if not is_responder:
        base += random.uniform(0, 8)  # Non-responders may have more challenging experiences
    return round(min(35, base))


def generate_piq_score(is_responder):
    """PIQ (Psychological Insight) - 9-45 scale."""
    if is_responder:
        return round(random.uniform(28, 43))
    else:
        return round(random.uniform(15, 32))


def assign_timepoint_pattern(participant_num, total_participants, dosing_rescheduled):
    """
    Assign timepoint pattern for a participant.

    IMPORTANT: A participant either has ALL _r timepoints OR ALL non-_r timepoints.
    This is determined by whether their dosing session was rescheduled.

    Args:
        participant_num: The participant number
        total_participants: Total number of participants
        dosing_rescheduled: Boolean indicating if dosing was rescheduled

    Returns:
        List of (event_name, logical_timepoint) tuples
    """
    # Determine how many timepoints (most complete 2-5 follow-ups after baseline)
    n_followups = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 30, 35, 15])[0]

    # Build timepoint list - always include t1 and t2
    # Then randomly select from t3-t6
    followup_options = [3, 4, 5, 6]
    selected_followups = sorted(random.sample(followup_options, min(n_followups, len(followup_options))))

    timepoints_to_use = [1, 2] + selected_followups

    # Convert to event names based on rescheduled status
    if dosing_rescheduled:
        # ALL timepoints use _r variant (except t1 which has no _r)
        events = []
        for tp in timepoints_to_use:
            if tp == 1:
                events.append(('timepoint_1_arm_1', 1))
            else:
                events.append((f'timepoint_{tp}_r_arm_1', tp))
    else:
        # ALL timepoints use standard variant
        events = [(f'timepoint_{tp}_arm_1', tp) for tp in timepoints_to_use]

    return events


# =============================================================================
# QUESTIONNAIRE-TIMEPOINT MAPPING (per codebook)
# =============================================================================

def should_have_questionnaire(questionnaire, timepoint):
    """
    Determine if a questionnaire should be administered at a given timepoint.
    Based on the data_dictionary_codebook.xlsx Instruments sheet.

    Args:
        questionnaire: Name of the questionnaire (e.g., 'phq9', 'meq4')
        timepoint: Logical timepoint number (1-6)

    Returns:
        Boolean indicating if questionnaire should be administered
    """
    # Questionnaires that are at ALL timepoints (t1-t6) EXCEPT t2
    at_t1_and_followups = {'phq9', 'gad7', 'who5', 'psyflex', 'auditc'}

    # Questionnaires that are ONLY at t2 (dosing session)
    dosing_only = {'meq4', 'ebi', 'ceq', 'piq', 'sscs', 'mpod_s'}

    # Questionnaires that are at ALL timepoints including t2
    all_timepoints = {'rrs', 'bcss', 'bis', 'bfi10', 'mpod_t'}

    # Questionnaires that are ONLY at t1 (baseline)
    baseline_only = {'expectancy', 'demographics', 'consent'}

    # Questionnaires that are ONLY at t3
    t3_only = {'csq8'}

    if questionnaire in at_t1_and_followups:
        return timepoint in [1, 3, 4, 5, 6]  # NOT at t2
    elif questionnaire in dosing_only:
        return timepoint == 2
    elif questionnaire in all_timepoints:
        return True  # All timepoints t1-t6
    elif questionnaire in baseline_only:
        return timepoint == 1
    elif questionnaire in t3_only:
        return timepoint == 3
    else:
        return False


# =============================================================================
# GENERATE DATASET
# =============================================================================

def generate_realistic_data():
    """Generate realistic sample dataset with correct timepoint-questionnaire mapping."""

    print("Generating realistic sample dataset...")
    print("=" * 70)
    print("Key features:")
    print("  - Participants either have ALL _r or ALL non-_r timepoints")
    print("  - PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C NOT at t2 (per protocol)")
    print("  - MEQ-4, EBI, CEQ, PIQ ONLY at t2")
    print("  - dosing_rescheduled column tracks rescheduled sessions")
    print("=" * 70)

    # Read headers from the codebook or use comprehensive headers
    # For this script, we'll build the columns we need

    rows = []
    participant_info = []  # Store participant-level info
    record_id = 1

    profile_counts = {p: 0 for p in PROFILES.keys()}
    responder_count = 0
    mystical_exp_count = 0
    rescheduled_count = 0

    for first_name, last_name in PSYCHONAUT_NAMES[:120]:
        # Assign profile
        profile_name = assign_profile()
        profile_counts[profile_name] += 1

        # Determine if responder
        is_responder = random.random() < PROFILES[profile_name]['response_prob']
        if is_responder:
            responder_count += 1

        # Generate baseline scores
        baseline_phq9, baseline_gad7, baseline_who5 = generate_baseline_scores(profile_name)

        # Demographics
        age = random.randint(21, 68)
        gender = random.choice([1, 1, 1, 2, 2, 2, 2, 3, 4])  # More women
        sex = random.choice([1, 2])
        education = random.choices([2, 3, 4, 5], weights=[10, 25, 40, 25])[0]

        # Determine if dosing was rescheduled (15% of participants)
        dosing_rescheduled = random.random() < 0.15
        if dosing_rescheduled:
            rescheduled_count += 1

        # Store participant-level info
        participant_info.append({
            'record_id': record_id,
            'dosing_rescheduled': dosing_rescheduled,
            'profile': profile_name,
            'is_responder': is_responder,
        })

        # Assign timepoint pattern
        timepoints = assign_timepoint_pattern(record_id, 120, dosing_rescheduled)

        for event_name, logical_tp in timepoints:
            row = {}

            # Basic identifiers
            row['record_id'] = record_id
            row['redcap_event_name'] = event_name

            # Demographics (only at baseline)
            if logical_tp == 1:
                row['age'] = age
                row['gender'] = gender
                row['sex'] = sex
                row['education'] = education
                row['relat'] = random.choice([0, 1, 2, 3, 4])
                row['latino'] = random.choice([0, 0, 0, 1])
                row['income_est'] = random.choice([2, 3, 4, 5, 6])
                row['military_service'] = random.choice([0, 0, 0, 1])

                # Race
                race_choice = random.choices([5, 3, 2, 1, 4, 6],
                                            weights=[60, 15, 10, 5, 5, 5])[0]
                for i in range(1, 7):
                    row[f'race1___{i}'] = 1 if i == race_choice else 0

                # Employment (can select multiple)
                emp_options = random.sample(range(1, 10), random.randint(1, 2))
                for i in range(1, 10):
                    row[f'employ___{i}'] = 1 if i in emp_options else 0

                # Medical history
                n_conditions = random.choices([0, 1, 2, 3], weights=[40, 30, 20, 10])[0]
                med_hist = random.sample(range(1, 13), n_conditions) if n_conditions > 0 else []
                for i in range(1, 13):
                    row[f'medical_history___{i}'] = 1 if i in med_hist else 0

                # Psychiatric medications
                if 'severe' in profile_name or 'comorbid' in profile_name:
                    n_meds = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
                else:
                    n_meds = random.choices([0, 1, 2], weights=[50, 40, 10])[0]

                psych_meds = random.sample(range(1, 9), n_meds) if n_meds > 0 else []
                for i in range(1, 9):
                    row[f'psychiatric_medications___{i}'] = 1 if i in psych_meds else 0

                # Psychedelics used (most haven't used before)
                if random.random() < 0.30:  # 30% have prior experience
                    psychs_used = random.sample(range(1, 10), random.randint(1, 3))
                else:
                    psychs_used = []
                for i in range(1, 10):
                    row[f'psychedelics_used___{i}'] = 1 if i in psychs_used else 0

                # Consent info
                row['consent_nameprint'] = f"{first_name} {last_name}"
                row['consent_age'] = 1
                row['consent_psilocybintherapy'] = 1
                row['consent_consent'] = 1
                row['email'] = f"{first_name.lower()}.{last_name.lower()}@example.com"
                row['consent_date'] = (datetime.now() - timedelta(days=random.randint(30, 180))).strftime('%m/%d/%y')

                row['study_information_timestamp'] = (datetime.now() - timedelta(days=random.randint(30, 180))).strftime('%m/%d/%y %H:%M')
                row['informed_consent_timestamp'] = row['study_information_timestamp']
                row['medssupps_predosing_timestamp'] = row['study_information_timestamp']

                row['study_information_complete'] = 2
                row['informed_consent_complete'] = 2
                row['medssupps_predosing_complete'] = 2

            # Generate scores based on timepoint-questionnaire mapping

            # PHQ-9, GAD-7, WHO-5 - at t1 and t3-t6, NOT at t2
            if should_have_questionnaire('phq9', logical_tp):
                phq9_total, gad7_total, who5_total = generate_followup_scores(
                    baseline_phq9, baseline_gad7, baseline_who5,
                    logical_tp, profile_name, is_responder
                )

                # PHQ-9 items (reverse engineer from total)
                if random.random() < 0.90:  # 90% complete at this timepoint
                    phq9_items = []
                    remaining = phq9_total
                    for i in range(8):
                        max_val = min(3, remaining)
                        val = random.randint(0, max_val)
                        phq9_items.append(val)
                        remaining -= val
                    phq9_items.append(max(0, min(3, remaining)))
                    random.shuffle(phq9_items)

                    for i, val in enumerate(phq9_items, 1):
                        row[f'phq9_{i}'] = val
                    row['phq9_totalscore'] = sum(phq9_items)
                    row['patient_health_questionnaire_9_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['patient_health_questionnaire_9_complete'] = 2

            if should_have_questionnaire('gad7', logical_tp):
                _, gad7_total, _ = generate_followup_scores(
                    baseline_phq9, baseline_gad7, baseline_who5,
                    logical_tp, profile_name, is_responder
                )

                if random.random() < 0.88:  # 88% complete
                    gad7_items = []
                    remaining = gad7_total
                    for i in range(6):
                        max_val = min(3, remaining)
                        val = random.randint(0, max_val)
                        gad7_items.append(val)
                        remaining -= val
                    gad7_items.append(max(0, min(3, remaining)))
                    random.shuffle(gad7_items)

                    for i, val in enumerate(gad7_items, 1):
                        row[f'gad7_{i}'] = val
                    row['gad7_totalscore'] = sum(gad7_items)
                    row['gad7_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['gad7_complete'] = 2

            if should_have_questionnaire('who5', logical_tp):
                _, _, who5_total = generate_followup_scores(
                    baseline_phq9, baseline_gad7, baseline_who5,
                    logical_tp, profile_name, is_responder
                )

                if random.random() < 0.85:  # 85% complete
                    who5_raw_sum = who5_total / 4  # Convert back to raw sum (0-25)
                    who5_items = []
                    remaining = who5_raw_sum
                    for i in range(4):
                        max_val = min(5, remaining)
                        val = random.uniform(0, max_val)
                        who5_items.append(val)
                        remaining -= val
                    who5_items.append(max(0, min(5, remaining)))
                    random.shuffle(who5_items)

                    for i, val in enumerate(who5_items, 1):
                        row[f'who_5_{i}'] = round(val)
                    row['who5_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['who5_complete'] = 2

            # Psychological Flexibility - at t1 and t3-t6
            if should_have_questionnaire('psyflex', logical_tp):
                current_phq9 = phq9_total if should_have_questionnaire('phq9', logical_tp) else baseline_phq9

                if random.random() < 0.80:  # 80% complete
                    psyflex_total = generate_psyflex_score(baseline_phq9, current_phq9)
                    psyflex_items = []
                    remaining = psyflex_total
                    for i in range(5):
                        max_val = min(5, remaining - (5 - i))  # Ensure enough remaining for later items
                        min_val = max(1, remaining - 5 * (5 - i))  # Ensure we don't leave too much
                        val = random.randint(min_val, max_val)
                        psyflex_items.append(val)
                        remaining -= val
                    psyflex_items.append(max(1, min(5, remaining)))
                    random.shuffle(psyflex_items)

                    for i, val in enumerate(psyflex_items, 1):
                        row[f'psyflex_{i}'] = val
                    row['psyflex_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['psyflex_complete'] = 2

            # AUDIT-C - at t1 and t3-t6
            if should_have_questionnaire('auditc', logical_tp):
                if random.random() < 0.80:  # 80% complete
                    audit_total = generate_audit_score(age, profile_name)
                    audit_items = []
                    remaining = audit_total
                    for i in range(2):
                        max_val = min(4, remaining)
                        val = random.randint(0, max_val)
                        audit_items.append(val)
                        remaining -= val
                    audit_items.append(max(0, min(4, remaining)))
                    random.shuffle(audit_items)

                    for i, val in enumerate(audit_items, 1):
                        row[f'auditc_{i}'] = val
                    row['auditc_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['auditc_complete'] = 2

            # MEQ-4 - ONLY at t2 (dosing session)
            if should_have_questionnaire('meq4', logical_tp):
                if random.random() < 0.90:  # 90% complete at dosing
                    meq_mean = generate_meq_score(is_responder, profile_name)
                    if meq_mean >= 3.5:
                        mystical_exp_count += 1

                    for i in range(1, 5):
                        row[f'meq4_{i}'] = round(meq_mean + random.uniform(-0.5, 0.5), 1)
                    row['meq4_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['meq4_complete'] = 2

            # EBI (Emotional Breakthrough) - ONLY at t2
            if should_have_questionnaire('ebi', logical_tp):
                if random.random() < 0.85:  # 85% complete
                    ebi_total = generate_ebi_score(is_responder)
                    # Distribute across 6 items (0-5 each, but use 8 to allow for variations)
                    ebi_items = []
                    remaining = ebi_total
                    for i in range(5):
                        max_val = min(5, remaining)
                        val = random.randint(0, max_val)
                        ebi_items.append(val)
                        remaining -= val
                    ebi_items.append(max(0, min(5, remaining)))
                    random.shuffle(ebi_items)

                    for i, val in enumerate(ebi_items, 1):
                        row[f'ebi_{i}'] = val
                    row['ebi_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['ebi_complete'] = 2

            # CEQ (Challenging Experience) - ONLY at t2
            if should_have_questionnaire('ceq', logical_tp):
                if random.random() < 0.85:  # 85% complete
                    ceq_total = generate_ceq_score(is_responder)
                    ceq_items = []
                    remaining = ceq_total
                    for i in range(6):
                        max_val = min(5, remaining)
                        val = random.randint(0, max_val)
                        ceq_items.append(val)
                        remaining -= val
                    ceq_items.append(max(0, min(5, remaining)))
                    random.shuffle(ceq_items)

                    for i, val in enumerate(ceq_items, 1):
                        row[f'ceq_{i}'] = val
                    row['ceq_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['ceq_complete'] = 2

            # PIQ (Psychological Insight) - ONLY at t2
            if should_have_questionnaire('piq', logical_tp):
                if random.random() < 0.85:  # 85% complete
                    piq_total = generate_piq_score(is_responder)
                    piq_items = []
                    remaining = piq_total - 9  # Subtract minimum (9 items * 1)
                    for i in range(8):
                        max_add = min(4, remaining)  # 4 is max additional (5-1)
                        val = 1 + random.randint(0, max_add)
                        piq_items.append(val)
                        remaining -= (val - 1)
                    piq_items.append(max(1, min(5, 1 + remaining)))
                    random.shuffle(piq_items)

                    for i, val in enumerate(piq_items, 1):
                        row[f'piq_{i}'] = val
                    row['piq_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['piq_complete'] = 2

            # Expectancy (only at baseline)
            if should_have_questionnaire('expectancy', logical_tp):
                if random.random() < 0.70:  # 70% complete
                    row['expect_1'] = random.randint(5, 10)  # Generally high expectations
                    row['expectancy_measure_timestamp'] = (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%m/%d/%y %H:%M')
                    row['expectancy_measure_complete'] = 2

            # Treatment date (at t2)
            if logical_tp == 2:
                row['treatment_date'] = (datetime.now() - timedelta(days=random.randint(60, 150))).strftime('%m/%d/%y')
                row['treatment_status'] = 1

            rows.append(row)

        record_id += 1

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Add dosing_rescheduled at participant level to each row
    df_participant_info = pd.DataFrame(participant_info)
    df = df.merge(df_participant_info[['record_id', 'dosing_rescheduled']], on='record_id', how='left')

    # Reorder columns to put dosing_rescheduled near the front
    cols = df.columns.tolist()
    cols.remove('dosing_rescheduled')
    cols.insert(2, 'dosing_rescheduled')
    df = df[cols]

    # Save to data directory
    output_path = Path(__file__).parent.parent / 'data' / 'sample_data.xlsx'
    df.to_excel(output_path, index=False, engine='openpyxl')

    print(f"\nGenerated {len(df)} rows for {record_id-1} participants")
    print(f"\nProfile Distribution:")
    for profile, count in sorted(profile_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {profile:20s}: {count:3d} ({100*count/(record_id-1):.1f}%)")

    print(f"\nDosing Session Pattern:")
    print(f"  Standard (non-rescheduled): {record_id-1-rescheduled_count} ({100*(record_id-1-rescheduled_count)/(record_id-1):.1f}%)")
    print(f"  Rescheduled (_r timepoints): {rescheduled_count} ({100*rescheduled_count/(record_id-1):.1f}%)")

    print(f"\nTreatment Outcomes:")
    print(f"  Responders: {responder_count}/{record_id-1} ({100*responder_count/(record_id-1):.1f}%)")
    print(f"  Mystical experiences: ~{mystical_exp_count} reported")

    print(f"\nSaved to: {output_path}")
    print("\nKey features:")
    print("  - Consistent psychological profiles")
    print("  - 60-70% response rate (realistic for psychedelic therapy)")
    print("  - Mystical experiences correlate with better outcomes")
    print("  - Symptoms improve over time for responders")
    print("  - PHQ-9/GAD-7/WHO-5 NOT at t2 (per protocol)")
    print("  - MEQ-4/EBI/CEQ/PIQ ONLY at t2")
    print("  - Participants have ALL _r OR ALL non-_r timepoints")
    print("  - dosing_rescheduled column tracks rescheduled sessions")

    return df, df_participant_info


if __name__ == '__main__':
    df, df_info = generate_realistic_data()

    # Show sample data
    print("\n" + "=" * 70)
    print("Sample data preview:")
    print("=" * 70)

    # Show a rescheduled participant
    rescheduled_ids = df_info[df_info['dosing_rescheduled'] == True]['record_id'].tolist()
    if rescheduled_ids:
        sample_r = df[df['record_id'] == rescheduled_ids[0]][['record_id', 'redcap_event_name', 'dosing_rescheduled', 'consent_nameprint', 'phq9_totalscore', 'meq4_1']]
        print(f"\nRecord {rescheduled_ids[0]} (Rescheduled - all _r timepoints):")
        print(sample_r.to_string(index=False))

    # Show a standard participant
    standard_ids = df_info[df_info['dosing_rescheduled'] == False]['record_id'].tolist()
    if standard_ids:
        sample_std = df[df['record_id'] == standard_ids[0]][['record_id', 'redcap_event_name', 'dosing_rescheduled', 'consent_nameprint', 'phq9_totalscore', 'meq4_1']]
        print(f"\nRecord {standard_ids[0]} (Standard - no _r timepoints):")
        print(sample_std.to_string(index=False))

    # Verify no PHQ-9 at t2
    t2_events = df[df['redcap_event_name'].str.contains('timepoint_2', na=False)]
    phq9_at_t2 = t2_events['phq9_totalscore'].notna().sum()
    print(f"\nVerification: PHQ-9 scores at t2/t2_r: {phq9_at_t2} (should be 0)")

    # Verify MEQ-4 only at t2
    non_t2_events = df[~df['redcap_event_name'].str.contains('timepoint_2', na=False)]
    meq_outside_t2 = non_t2_events['meq4_1'].notna().sum()
    print(f"Verification: MEQ-4 scores outside t2/t2_r: {meq_outside_t2} (should be 0)")
