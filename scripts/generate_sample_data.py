"""
Generate REALISTIC sample dataset with consistent psychological profiles
and typical psychedelic therapy outcomes.

KEY FEATURES:
- All 72 instruments from the REDCap codebook
- Consistent psychological profiles
- Realistic treatment responses (60-70% responders)
- Correct questionnaire-timepoint mapping per protocol
- Proper handling of rescheduled dosing sessions

TIMEPOINT-QUESTIONNAIRE MAPPING (per codebook):
- t1 (baseline): Demographics, consent, PHQ-9, GAD-7, WHO-5, PsyFlex, AUDIT-C, Expectancy,
                 EPDS, Specific Phobias, PDSS, SPIN, PCL-S, PG-13-R, IES-R, LPFS-BF, BSL-23,
                 IAT, SOGS, YMRS, PANSS, HRS, Y-BOCS, ASQ, ASRS, CPIB-SF, ATQ, DSS-B, EDE-QS,
                 PSQI, CFQ, PEG, NIDA-ASSIST scales, RRS, BCSS, BIS, BFI-10, MPoD-T
- t2 (dosing): MEQ-4, EBI, CEQ, PIQ, SSCS-S, MPoD-S, Swiss Side Effects,
               RRS, BCSS, BIS, BFI-10, MPoD-T
- t3 (1-week follow-up): Same as t1 + CSQ-8 + Swiss Side Effects
- t4-t6 (follow-ups): Same as t1 + Swiss Side Effects
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

while len(PSYCHONAUT_NAMES) < 120:
    PSYCHONAUT_NAMES.append((f"Researcher{len(PSYCHONAUT_NAMES)}", f"Name{len(PSYCHONAUT_NAMES)}"))


# =============================================================================
# QUESTIONNAIRE DEFINITIONS - All 72 instruments
# =============================================================================

QUESTIONNAIRES = {
    # === PRIMARY OUTCOME MEASURES (t1, t3-t6) ===
    'phq9': {
        'name': 'PHQ-9 (Depression)',
        'items': 9, 'item_range': (0, 3), 'total_range': (0, 27),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.90, 'higher_is_worse': True,
    },
    'gad7': {
        'name': 'GAD-7 (Anxiety)',
        'items': 7, 'item_range': (0, 3), 'total_range': (0, 21),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.88, 'higher_is_worse': True,
    },
    'who5': {
        'name': 'WHO-5 (Wellbeing)',
        'items': 5, 'item_range': (0, 5), 'total_range': (0, 100),
        'scoring': 'sum_x4', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.85, 'higher_is_worse': False,
    },
    'psyflex': {
        'name': 'PsyFlex (Psychological Flexibility)',
        'items': 6, 'item_range': (1, 5), 'total_range': (6, 30),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.80, 'higher_is_worse': False,
    },
    'auditc': {
        'name': 'AUDIT-C (Alcohol Use)',
        'items': 3, 'item_range': (0, 4), 'total_range': (0, 12),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.80, 'higher_is_worse': True,
    },

    # === DOSING SESSION MEASURES (t2 only) ===
    'meq4': {
        'name': 'MEQ-4 (Mystical Experience)',
        'items': 4, 'item_range': (0, 5), 'total_range': (0, 5),
        'scoring': 'mean', 'timepoints': [2],
        'completion_rate': 0.90, 'higher_is_worse': False,
    },
    'ebi': {
        'name': 'EBI (Emotional Breakthrough)',
        'items': 6, 'item_range': (0, 5), 'total_range': (0, 30),
        'scoring': 'sum', 'timepoints': [2],
        'completion_rate': 0.85, 'higher_is_worse': False,
    },
    'ceq': {
        'name': 'CEQ-7 (Challenging Experience)',
        'items': 7, 'item_range': (0, 5), 'total_range': (0, 35),
        'scoring': 'sum', 'timepoints': [2],
        'completion_rate': 0.85, 'higher_is_worse': True,
    },
    'piq': {
        'name': 'PIQ (Psychological Insight)',
        'items': 23, 'item_range': (1, 5), 'total_range': (23, 115),
        'scoring': 'sum', 'timepoints': [2],
        'completion_rate': 0.85, 'higher_is_worse': False,
    },
    'sscs': {
        'name': 'SSCS-S (State Self-Compassion)',
        'items': 6, 'item_range': (1, 5), 'total_range': (6, 30),
        'scoring': 'sum', 'timepoints': [2],
        'completion_rate': 0.80, 'higher_is_worse': False,
    },
    'mpod_s': {
        'name': 'MPoD-S (State Decentering)',
        'items': 3, 'item_range': (1, 5), 'total_range': (3, 15),
        'scoring': 'sum', 'timepoints': [2],
        'completion_rate': 0.80, 'higher_is_worse': False,
    },

    # === DEPRESSION/MOOD MEASURES (t1, t3-t6) ===
    'epds': {
        'name': 'EPDS (Edinburgh Postnatal Depression)',
        'items': 10, 'item_range': (0, 3), 'total_range': (0, 30),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.75, 'higher_is_worse': True,
    },
    'ymrs': {
        'name': 'YMRS (Young Mania Rating)',
        'items': 11, 'item_range': (0, 4), 'total_range': (0, 60),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },

    # === ANXIETY MEASURES (t1, t3-t6) ===
    'pdss': {
        'name': 'PDSS (Panic Disorder Severity)',
        'items': 7, 'item_range': (0, 4), 'total_range': (0, 28),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'spin': {
        'name': 'SPIN (Social Phobia Inventory)',
        'items': 17, 'item_range': (0, 4), 'total_range': (0, 68),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'specific_phobia': {
        'name': 'APA Specific Phobia Severity',
        'items': 10, 'item_range': (0, 4), 'total_range': (0, 40),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },

    # === TRAUMA MEASURES (t1, t3-t6) ===
    'pcl': {
        'name': 'PCL-S (PTSD Checklist)',
        'items': 20, 'item_range': (1, 5), 'total_range': (20, 100),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'ies_r': {
        'name': 'IES-R (Impact of Events)',
        'items': 22, 'item_range': (0, 4), 'total_range': (0, 88),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'pg13': {
        'name': 'PG-13-R (Prolonged Grief)',
        'items': 13, 'item_range': (1, 5), 'total_range': (13, 65),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },

    # === PERSONALITY/FUNCTIONING MEASURES (t1, t3-t6) ===
    'lpfs': {
        'name': 'LPFS-BF (Personality Functioning)',
        'items': 12, 'item_range': (1, 4), 'total_range': (12, 48),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'bsl23': {
        'name': 'BSL-23 (Borderline Symptoms)',
        'items': 23, 'item_range': (0, 4), 'total_range': (0, 92),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },

    # === BEHAVIORAL ADDICTIONS (t1, t3-t6) ===
    'iat': {
        'name': 'IAT (Internet Addiction)',
        'items': 20, 'item_range': (1, 5), 'total_range': (20, 100),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'sogs': {
        'name': 'SOGS (South Oaks Gambling)',
        'items': 20, 'item_range': (0, 1), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'hrs': {
        'name': 'HRS (Hoarding Rating)',
        'items': 5, 'item_range': (0, 8), 'total_range': (0, 40),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },

    # === OCD/COMPULSIVE MEASURES (t1, t3-t6) ===
    'ybocs': {
        'name': 'Y-BOCS (OCD Severity)',
        'items': 10, 'item_range': (0, 4), 'total_range': (0, 40),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },

    # === NEURODEVELOPMENTAL (t1, t3-t6) ===
    'asq': {
        'name': 'ASQ (Autism Spectrum Quotient)',
        'items': 28, 'item_range': (0, 1), 'total_range': (0, 28),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'asrs': {
        'name': 'ASRS (ADHD Self-Report)',
        'items': 18, 'item_range': (0, 4), 'total_range': (0, 72),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'atq': {
        'name': 'ATQ (Adult Tic Questionnaire)',
        'items': 20, 'item_range': (0, 4), 'total_range': (0, 80),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.60, 'higher_is_worse': True,
    },
    'cpib': {
        'name': 'CPIB-SF (Communicative Participation)',
        'items': 10, 'item_range': (0, 3), 'total_range': (0, 30),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': False,
    },

    # === PSYCHOTIC SYMPTOMS (t1, t3-t6) ===
    'panss': {
        'name': 'PANSS (Positive/Negative Syndrome)',
        'items': 30, 'item_range': (1, 7), 'total_range': (30, 210),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.65, 'higher_is_worse': True,
    },

    # === DISSOCIATIVE/EATING (t1, t3-t6) ===
    'dss': {
        'name': 'DSS-B (Dissociative Symptoms)',
        'items': 8, 'item_range': (0, 4), 'total_range': (0, 32),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'edeqs': {
        'name': 'EDE-QS (Eating Disorder)',
        'items': 12, 'item_range': (0, 3), 'total_range': (0, 36),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },

    # === SLEEP/COGNITIVE (t1, t3-t6) ===
    'psqi': {
        'name': 'PSQI (Sleep Quality)',
        'items': 7, 'item_range': (0, 3), 'total_range': (0, 21),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.75, 'higher_is_worse': True,
    },
    'cfq': {
        'name': 'CFQ (Cognitive Failures)',
        'items': 25, 'item_range': (0, 4), 'total_range': (0, 100),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },

    # === PAIN (t1, t3-t6) ===
    'peg': {
        'name': 'PEG (Pain Scale)',
        'items': 3, 'item_range': (0, 10), 'total_range': (0, 30),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.75, 'higher_is_worse': True,
    },

    # === ALL TIMEPOINTS (t1-t6) ===
    'rrs': {
        'name': 'RRS (Rumination)',
        'items': 22, 'item_range': (1, 4), 'total_range': (22, 88),
        'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'completion_rate': 0.75, 'higher_is_worse': True,
    },
    'bcss': {
        'name': 'BCSS (Brief Core Schema)',
        'items': 24, 'item_range': (0, 4), 'total_range': (0, 96),
        'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'completion_rate': 0.75, 'higher_is_worse': True,
    },
    'bis': {
        'name': 'BIS (Impulsiveness)',
        'items': 8, 'item_range': (1, 4), 'total_range': (8, 32),
        'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'completion_rate': 0.75, 'higher_is_worse': True,
    },
    'bfi10': {
        'name': 'BFI-10 (Big Five Personality)',
        'items': 10, 'item_range': (1, 5), 'total_range': (10, 50),
        'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'completion_rate': 0.75, 'higher_is_worse': False,
    },
    'mpod_t': {
        'name': 'MPoD-T (Trait Decentering)',
        'items': 15, 'item_range': (1, 5), 'total_range': (15, 75),
        'scoring': 'sum', 'timepoints': [1, 2, 3, 4, 5, 6],
        'completion_rate': 0.75, 'higher_is_worse': False,
    },

    # === SATISFACTION (t3 only) ===
    'csq8': {
        'name': 'CSQ-8 (Client Satisfaction)',
        'items': 8, 'item_range': (1, 4), 'total_range': (8, 32),
        'scoring': 'sum', 'timepoints': [3],
        'completion_rate': 0.80, 'higher_is_worse': False,
    },

    # === BASELINE ONLY ===
    'expectancy': {
        'name': 'Expectancy Measure',
        'items': 1, 'item_range': (0, 10), 'total_range': (0, 10),
        'scoring': 'single', 'timepoints': [1],
        'completion_rate': 0.70, 'higher_is_worse': False,
    },

    # === SIDE EFFECTS (t2-t6) ===
    'swiss_se': {
        'name': 'Swiss Psychedelic Side Effects',
        'items': 32, 'item_range': (0, 5), 'total_range': (0, 160),
        'scoring': 'sum', 'timepoints': [2, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },

    # === SUBSTANCE USE - NIDA ASSIST (t1, t3-t6) ===
    'nida_cannabis': {
        'name': 'NIDA-ASSIST Cannabis',
        'items': 5, 'item_range': (0, 4), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'nida_cocaine': {
        'name': 'NIDA-ASSIST Cocaine',
        'items': 5, 'item_range': (0, 4), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'nida_stimulants': {
        'name': 'NIDA-ASSIST Stimulants',
        'items': 5, 'item_range': (0, 4), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'nida_meth': {
        'name': 'NIDA-ASSIST Methamphetamine',
        'items': 5, 'item_range': (0, 4), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'nida_inhalants': {
        'name': 'NIDA-ASSIST Inhalants',
        'items': 5, 'item_range': (0, 4), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'nida_sedatives': {
        'name': 'NIDA-ASSIST Sedatives',
        'items': 5, 'item_range': (0, 4), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'nida_hallucinogens': {
        'name': 'NIDA-ASSIST Hallucinogens',
        'items': 5, 'item_range': (0, 4), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'nida_street_opioids': {
        'name': 'NIDA-ASSIST Street Opioids',
        'items': 5, 'item_range': (0, 4), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
    'nida_rx_opioids': {
        'name': 'NIDA-ASSIST Prescription Opioids',
        'items': 5, 'item_range': (0, 4), 'total_range': (0, 20),
        'scoring': 'sum', 'timepoints': [1, 3, 4, 5, 6],
        'completion_rate': 0.70, 'higher_is_worse': True,
    },
}


# =============================================================================
# PSYCHOLOGICAL PROFILES
# =============================================================================

PROFILES = {
    'severe_depression': {
        'weight': 20,
        'phq9_baseline': (15, 23),
        'gad7_baseline': (8, 14),
        'who5_baseline': (8, 24),
        'response_prob': 0.65,
    },
    'moderate_depression': {
        'weight': 25,
        'phq9_baseline': (10, 18),
        'gad7_baseline': (5, 12),
        'who5_baseline': (16, 40),
        'response_prob': 0.75,
    },
    'high_anxiety': {
        'weight': 20,
        'phq9_baseline': (8, 15),
        'gad7_baseline': (12, 19),
        'who5_baseline': (20, 44),
        'response_prob': 0.70,
    },
    'comorbid': {
        'weight': 15,
        'phq9_baseline': (14, 22),
        'gad7_baseline': (13, 20),
        'who5_baseline': (8, 28),
        'response_prob': 0.55,
    },
    'mild_symptoms': {
        'weight': 15,
        'phq9_baseline': (5, 11),
        'gad7_baseline': (4, 10),
        'who5_baseline': (32, 56),
        'response_prob': 0.80,
    },
    'subclinical': {
        'weight': 5,
        'phq9_baseline': (0, 6),
        'gad7_baseline': (0, 6),
        'who5_baseline': (48, 76),
        'response_prob': 0.50,
    },
}


def assign_profile():
    profiles = list(PROFILES.keys())
    weights = [PROFILES[p]['weight'] for p in profiles]
    return random.choices(profiles, weights=weights)[0]


def generate_baseline_scores(profile_name):
    profile = PROFILES[profile_name]
    phq9 = random.randint(*profile['phq9_baseline'])
    gad7 = random.randint(*profile['gad7_baseline'])
    who5 = random.randint(*profile['who5_baseline'])
    phq9 = max(0, min(27, phq9 + random.randint(-2, 2)))
    gad7 = max(0, min(21, gad7 + random.randint(-2, 2)))
    who5 = max(0, min(100, who5 + random.randint(-4, 4)))
    return phq9, gad7, who5


def generate_score_for_questionnaire(q_key, timepoint, baseline_severity, is_responder, profile_name):
    """Generate a realistic score for any questionnaire."""
    q = QUESTIONNAIRES[q_key]

    # Skip if questionnaire not at this timepoint
    if timepoint not in q['timepoints']:
        return None

    # Random completion based on rate
    if random.random() > q['completion_rate']:
        return None

    item_min, item_max = q['item_range']
    n_items = q['items']
    total_min, total_max = q['total_range']

    # Base severity factor (0-1) from profile
    severity_factor = baseline_severity / 27  # normalize based on PHQ-9 max

    # Adjust for responder status over time
    if is_responder and timepoint > 1:
        if timepoint == 2:
            reduction = random.uniform(0.1, 0.2)
        elif timepoint == 3:
            reduction = random.uniform(0.35, 0.50)
        elif timepoint == 4:
            reduction = random.uniform(0.45, 0.60)
        else:
            reduction = random.uniform(0.40, 0.55)
        severity_factor = severity_factor * (1 - reduction)
    elif not is_responder and timepoint > 1:
        severity_factor = severity_factor * random.uniform(0.85, 1.10)

    # Calculate target score
    if q['higher_is_worse']:
        target_score = total_min + (total_max - total_min) * severity_factor
    else:
        target_score = total_max - (total_max - total_min) * severity_factor

    # Add noise
    noise_range = (total_max - total_min) * 0.1
    target_score += random.uniform(-noise_range, noise_range)
    target_score = max(total_min, min(total_max, target_score))

    return round(target_score)


def generate_items_from_total(total, n_items, item_min, item_max):
    """Distribute a total score across individual items."""
    items = []
    remaining = total - (n_items * item_min)
    item_range = item_max - item_min

    for i in range(n_items - 1):
        max_for_item = min(item_range, remaining - (item_range * (n_items - i - 1)))
        max_for_item = max(0, max_for_item)
        val = random.randint(0, int(max_for_item))
        items.append(item_min + val)
        remaining -= val

    items.append(item_min + max(0, min(item_range, int(remaining))))
    random.shuffle(items)
    return items


def assign_timepoint_pattern(participant_num, total_participants, dosing_rescheduled):
    """Assign timepoint pattern for a participant."""
    n_followups = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 30, 35, 15])[0]
    followup_options = [3, 4, 5, 6]
    selected_followups = sorted(random.sample(followup_options, min(n_followups, len(followup_options))))
    timepoints_to_use = [1, 2] + selected_followups

    if dosing_rescheduled:
        events = []
        for tp in timepoints_to_use:
            if tp == 1:
                events.append(('timepoint_1_arm_1', 1))
            else:
                events.append((f'timepoint_{tp}_r_arm_1', tp))
    else:
        events = [(f'timepoint_{tp}_arm_1', tp) for tp in timepoints_to_use]

    return events


# =============================================================================
# GENERATE DATASET
# =============================================================================

def generate_realistic_data():
    """Generate realistic sample dataset with all questionnaires."""

    print("Generating realistic sample dataset with ALL questionnaires...")
    print("=" * 70)
    print(f"Total questionnaires: {len(QUESTIONNAIRES)}")
    print("=" * 70)

    rows = []
    participant_info = []
    record_id = 1

    profile_counts = {p: 0 for p in PROFILES.keys()}
    responder_count = 0
    rescheduled_count = 0

    for first_name, last_name in PSYCHONAUT_NAMES[:120]:
        profile_name = assign_profile()
        profile_counts[profile_name] += 1

        is_responder = random.random() < PROFILES[profile_name]['response_prob']
        if is_responder:
            responder_count += 1

        baseline_phq9, baseline_gad7, baseline_who5 = generate_baseline_scores(profile_name)

        age = random.randint(21, 68)
        gender = random.choice([1, 1, 1, 2, 2, 2, 2, 3, 4])
        sex = random.choice([1, 2])
        education = random.choices([2, 3, 4, 5], weights=[10, 25, 40, 25])[0]

        dosing_rescheduled = random.random() < 0.15
        if dosing_rescheduled:
            rescheduled_count += 1

        participant_info.append({
            'record_id': record_id,
            'dosing_rescheduled': dosing_rescheduled,
            'profile': profile_name,
            'is_responder': is_responder,
        })

        timepoints = assign_timepoint_pattern(record_id, 120, dosing_rescheduled)

        for event_name, logical_tp in timepoints:
            row = {
                'record_id': record_id,
                'redcap_event_name': event_name,
            }

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

                race_choice = random.choices([5, 3, 2, 1, 4, 6], weights=[60, 15, 10, 5, 5, 5])[0]
                for i in range(1, 7):
                    row[f'race1___{i}'] = 1 if i == race_choice else 0

                emp_options = random.sample(range(1, 10), random.randint(1, 2))
                for i in range(1, 10):
                    row[f'employ___{i}'] = 1 if i in emp_options else 0

                n_conditions = random.choices([0, 1, 2, 3], weights=[40, 30, 20, 10])[0]
                med_hist = random.sample(range(1, 13), n_conditions) if n_conditions > 0 else []
                for i in range(1, 13):
                    row[f'medical_history___{i}'] = 1 if i in med_hist else 0

                if 'severe' in profile_name or 'comorbid' in profile_name:
                    n_meds = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
                else:
                    n_meds = random.choices([0, 1, 2], weights=[50, 40, 10])[0]

                psych_meds = random.sample(range(1, 9), n_meds) if n_meds > 0 else []
                for i in range(1, 9):
                    row[f'psychiatric_medications___{i}'] = 1 if i in psych_meds else 0

                if random.random() < 0.30:
                    psychs_used = random.sample(range(1, 10), random.randint(1, 3))
                else:
                    psychs_used = []
                for i in range(1, 10):
                    row[f'psychedelics_used___{i}'] = 1 if i in psychs_used else 0

                row['consent_nameprint'] = f"{first_name} {last_name}"
                row['consent_age'] = 1
                row['consent_psilocybintherapy'] = 1
                row['consent_consent'] = 1
                row['email'] = f"{first_name.lower()}.{last_name.lower()}@example.com"
                row['consent_date'] = (datetime.now() - timedelta(days=random.randint(30, 180))).strftime('%m/%d/%y')

            # Generate scores for all questionnaires at this timepoint
            for q_key, q_info in QUESTIONNAIRES.items():
                if logical_tp not in q_info['timepoints']:
                    continue

                total_score = generate_score_for_questionnaire(
                    q_key, logical_tp, baseline_phq9, is_responder, profile_name
                )

                if total_score is None:
                    continue

                # Generate individual items
                items = generate_items_from_total(
                    total_score, q_info['items'],
                    q_info['item_range'][0], q_info['item_range'][1]
                )

                for i, val in enumerate(items, 1):
                    row[f'{q_key}_{i}'] = val

                # Store total score
                if q_info['scoring'] == 'mean':
                    row[f'{q_key}_mean'] = round(sum(items) / len(items), 2)
                else:
                    row[f'{q_key}_total'] = sum(items)

            # Treatment date (at t2)
            if logical_tp == 2:
                row['treatment_date'] = (datetime.now() - timedelta(days=random.randint(60, 150))).strftime('%m/%d/%y')
                row['treatment_status'] = 1

            rows.append(row)

        record_id += 1

    df = pd.DataFrame(rows)

    df_participant_info = pd.DataFrame(participant_info)
    df = df.merge(df_participant_info[['record_id', 'dosing_rescheduled']], on='record_id', how='left')

    cols = df.columns.tolist()
    cols.remove('dosing_rescheduled')
    cols.insert(2, 'dosing_rescheduled')
    df = df[cols]

    output_path = Path(__file__).parent.parent / 'data' / 'sample_data.xlsx'
    df.to_excel(output_path, index=False, engine='openpyxl')

    print(f"\nGenerated {len(df)} rows for {record_id-1} participants")
    print(f"Columns: {len(df.columns)}")

    print(f"\nProfile Distribution:")
    for profile, count in sorted(profile_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {profile:20s}: {count:3d} ({100*count/(record_id-1):.1f}%)")

    print(f"\nDosing Session Pattern:")
    print(f"  Standard: {record_id-1-rescheduled_count} ({100*(record_id-1-rescheduled_count)/(record_id-1):.1f}%)")
    print(f"  Rescheduled: {rescheduled_count} ({100*rescheduled_count/(record_id-1):.1f}%)")

    print(f"\nTreatment Outcomes:")
    print(f"  Responders: {responder_count}/{record_id-1} ({100*responder_count/(record_id-1):.1f}%)")

    print(f"\nSaved to: {output_path}")

    return df, df_participant_info


if __name__ == '__main__':
    df, df_info = generate_realistic_data()

    print("\n" + "=" * 70)
    print("Questionnaire coverage by timepoint:")
    print("=" * 70)

    for tp in [1, 2, 3, 4, 5, 6]:
        q_at_tp = [k for k, v in QUESTIONNAIRES.items() if tp in v['timepoints']]
        print(f"t{tp}: {len(q_at_tp)} questionnaires")
