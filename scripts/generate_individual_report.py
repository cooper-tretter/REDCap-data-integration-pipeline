"""
Individual Participant Report Generator
=======================================

Generates personalized PDF reports for study participants showing their
outcomes across timepoints with visualizations and interpretations.

Design: "Analog Maximalism" — warm, textured, authored feel.
Uses PATH Lab branding:
- Colors: #394F79 (primary), #253D6C (dark), #7E846F (sage), #FFEFDD (cream)
- Warm neutrals as ground: cream (#F5F0E8), putty, warm grays
- Font: Montserrat
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

# PATH Lab Brand Colors — Analog Maximalism palette
COLORS = {
    'primary': '#394F79',      # Primary blue
    'dark': '#253D6C',         # Dark blue
    'sage': '#7E846F',         # Sage green
    'cream': '#FFEFDD',        # Brand cream
    'warm_bg': '#F5F0E8',      # Warm page background
    'putty': '#E0D8CC',        # Putty — borders and dividers
    'warm_dark': '#2C2418',    # Near-black warm brown — for hard edges
    'warm_gray': '#8C8477',    # Warm gray text
    'success': '#4A7C59',      # Green for improvement
    'neutral': '#7E846F',      # Sage for no change
    'danger': '#A85454',       # Red for worsening
    'band_green': '#4A7C59',
    'band_light_green': '#6B8E5B',
    'band_sage': '#7E846F',
    'band_orange': '#A07050',
    'band_red': '#A85454',
}

# Timepoint labels — clarify pre/post
TIMEPOINT_LABELS = {
    'bl': 'Baseline\n(Pre-Session)',
    '3d': '3 Days',
    '1mo': '1 Month\n(Post-Session)',
    '3mo': '3 Months\n(Post-Session)',
    '6mo': '6 Months\n(Post-Session)',
    '12mo': '12 Months\n(Post-Session)',
}

# Score interpretations
PHQ9_SEVERITY = [
    (0, 4, 'None-Minimal', COLORS['band_green']),
    (5, 9, 'Mild', COLORS['band_light_green']),
    (10, 14, 'Moderate', COLORS['band_sage']),
    (15, 19, 'Moderately Severe', COLORS['band_orange']),
    (20, 27, 'Severe', COLORS['band_red']),
]

GAD7_SEVERITY = [
    (0, 4, 'Minimal', COLORS['band_green']),
    (5, 9, 'Mild', COLORS['band_light_green']),
    (10, 14, 'Moderate', COLORS['band_sage']),
    (15, 21, 'Severe', COLORS['band_red']),
]

WHO5_SEVERITY = [
    (0, 28, 'Poor Wellbeing', COLORS['band_red']),
    (29, 50, 'Low Wellbeing', COLORS['band_sage']),
    (51, 100, 'Good Wellbeing', COLORS['band_green']),
]

# Published norms for acute experience measures
ACUTE_NORMS = {
    'meq4': {
        'name': 'Mystical\nExperience (MEQ-4)',
        'definition': 'Measures the intensity of mystical-type\nexperiences during the session',
        'range': (0, 5),
        'scoring': 'mean',
        'complete_threshold': 3.0,
        'complete_label': 'Complete Mystical Experience',
        'published_mean': 3.5,
        'published_source': 'Barrett et al., 2015',
    },
    'ceq': {
        'name': 'Challenging\nExperience (CEQ-7)',
        'definition': 'Measures the intensity of challenging\nexperiences during the session',
        'range': (0, 35),
        'scoring': 'sum',
        'published_mean': 14.0,
        'published_source': 'Barrett et al., 2016',
    },
    'piq': {
        'name': 'Psychological\nInsight (PIQ)',
        'definition': 'Measures the degree of psychological\ninsight gained during the session',
        'range': (0, 115),
        'scoring': 'sum',
        'published_mean': 80.0,
        'published_source': 'Davis et al., 2021',
    },
    'ebi': {
        'name': 'Emotional\nBreakthrough (EBI)',
        'definition': 'Measures the degree of emotional\nrelease experienced during the session',
        'range': (0, 30),
        'scoring': 'sum',
        'published_mean': 20.0,
        'published_source': 'Roseman et al., 2019',
    },
}


def setup_figure_style():
    """Set up matplotlib style for Analog Maximalism aesthetic."""
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Montserrat', 'Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.edgecolor'] = COLORS['warm_dark']
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['axes.labelcolor'] = COLORS['dark']
    plt.rcParams['xtick.color'] = COLORS['dark']
    plt.rcParams['ytick.color'] = COLORS['dark']
    plt.rcParams['figure.facecolor'] = COLORS['warm_bg']
    plt.rcParams['axes.facecolor'] = COLORS['warm_bg']


def create_header(fig, report_type, report_date, logo_dir=None):
    """Create report header with PATH Lab branding, prominent logo, no participant ID."""
    # Header background — cream bar
    header_ax = fig.add_axes([0, 0.91, 1, 0.09])
    header_ax.set_facecolor(COLORS['cream'])
    header_ax.set_xlim(0, 1)
    header_ax.set_ylim(0, 1)
    header_ax.axis('off')

    # Bottom border — intentional, thick warm dark line
    header_ax.plot([0, 1], [0, 0], color=COLORS['warm_dark'], linewidth=3,
                   transform=header_ax.transAxes, clip_on=False)

    # Try to load and display logo — BIGGER
    if logo_dir:
        try:
            logo = mpimg.imread(logo_dir / 'PATHLogo.png')
            logo_ax = fig.add_axes([0.02, 0.915, 0.22, 0.08])
            logo_ax.imshow(logo)
            logo_ax.axis('off')
        except Exception:
            pass

    # Report info on right
    header_ax.text(0.97, 0.65, f'{report_type} Outcomes Report', fontsize=14,
                   color=COLORS['dark'], va='center', ha='right', fontweight='bold')
    header_ax.text(0.97, 0.28, report_date, fontsize=9,
                   color=COLORS['warm_gray'], va='center', ha='right')


def create_footer_with_logos(fig, logo_dir):
    """Create footer with logos and attribution."""
    footer_ax = fig.add_axes([0, 0, 1, 0.055])
    footer_ax.set_facecolor(COLORS['cream'])
    footer_ax.set_xlim(0, 1)
    footer_ax.set_ylim(0, 1)
    footer_ax.axis('off')

    # Top border — intentional, thick warm dark line
    footer_ax.plot([0, 1], [1, 1], color=COLORS['warm_dark'], linewidth=3,
                   transform=footer_ax.transAxes, clip_on=False)

    # Try to load and display logos
    try:
        path_logo = mpimg.imread(logo_dir / 'PATHLogo.png')
        logo_ax = fig.add_axes([0.02, 0.006, 0.12, 0.042])
        logo_ax.imshow(path_logo)
        logo_ax.axis('off')
    except Exception:
        pass

    # Try New School logo (PNG version)
    try:
        ns_logo = mpimg.imread(logo_dir / 'newschool_logo.png')
        ns_ax = fig.add_axes([0.15, 0.006, 0.12, 0.042])
        ns_ax.imshow(ns_logo)
        ns_ax.axis('off')
    except Exception:
        pass

    # Attribution text
    footer_ax.text(0.5, 0.7,
                   'This report was generated by the PATH Lab at the New School for Social Research',
                   ha='center', va='center', fontsize=7, color=COLORS['dark'], style='italic')
    footer_ax.text(0.5, 0.25,
                   'For informational purposes only. Please discuss with your healthcare provider.',
                   ha='center', va='center', fontsize=6, color=COLORS['warm_gray'], style='italic')


def create_score_chart(ax, show_timepoints, scores, scale_name, y_range, severity_bands,
                       y_ticks=None):
    """Create a line chart showing score progression with severity bands.

    Bands are flush/continuous with higher alpha. Y-axis uses whole-number ticks.
    Max y value = max value on survey.
    """
    valid_data = [(tp, score) for tp, score in zip(show_timepoints, scores)
                  if not pd.isna(score)]
    if not valid_data:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                fontsize=12, color=COLORS['sage'])
        ax.set_title(scale_name, fontweight='bold', color=COLORS['dark'])
        return

    tps, vals = zip(*valid_data)
    x_positions = [show_timepoints.index(tp) for tp in tps]

    # Draw severity bands — flush/continuous, no gaps between bands, higher alpha
    sorted_bands = sorted(severity_bands, key=lambda b: b[0])
    for i, (low, high, label, color) in enumerate(sorted_bands):
        # Make bands flush: each band starts exactly where the previous ended
        band_low = low if i == 0 else sorted_bands[i - 1][1] + 1
        # But for the very first band, start at y_range minimum
        if i == 0:
            band_low = y_range[0]
        band_high = high + 1 if i < len(sorted_bands) - 1 else y_range[1]
        ax.axhspan(band_low, band_high, alpha=0.28, color=color, linewidth=0)

    # Plot line and points
    ax.plot(x_positions, vals, '-', color=COLORS['dark'], linewidth=2.5)
    ax.scatter(x_positions, vals, s=90, color=COLORS['primary'], zorder=5,
               edgecolors=COLORS['warm_dark'], linewidths=1.5)

    # Add value labels
    for x, y in zip(x_positions, vals):
        ax.annotate(f'{y:.0f}', (x, y), textcoords="offset points",
                    xytext=(0, 12), ha='center', fontsize=10, fontweight='bold',
                    color=COLORS['warm_dark'])

    # X-axis
    ax.set_xlim(-0.5, len(show_timepoints) - 0.5)
    ax.set_ylim(y_range)
    ax.set_xticks(range(len(show_timepoints)))
    ax.set_xticklabels([TIMEPOINT_LABELS[tp] for tp in show_timepoints], fontsize=7)
    ax.set_title(scale_name, fontweight='bold', color=COLORS['dark'], pad=10)

    # Left y-axis: whole-number round ticks
    if y_ticks is not None:
        ax.set_yticks(y_ticks)
    ax.yaxis.set_visible(True)
    ax.tick_params(axis='y', labelsize=8)

    # Right y-axis: severity labels
    ax2 = ax.twinx()
    ax2.set_ylim(y_range)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    sev_ticks = []
    sev_labels = []
    for low, high, label, color in severity_bands:
        mid = (low + high) / 2
        sev_ticks.append(mid)
        sev_labels.append(label)
    ax2.set_yticks(sev_ticks)
    ax2.set_yticklabels(sev_labels, fontsize=7, color=COLORS['warm_gray'])
    ax2.tick_params(axis='y', length=0)

    ax.grid(True, axis='y', alpha=0.15, color=COLORS['putty'])


def create_change_summary(ax, baseline, current, label, higher_is_worse=True):
    """Create a change summary box — arrow, points change, percent. No status labels."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    if pd.isna(baseline) or pd.isna(current):
        ax.text(0.5, 0.5, f'{label}\nNo data', ha='center', va='center',
                fontsize=10, color=COLORS['sage'])
        return

    change = current - baseline
    pct_change = (change / baseline * 100) if baseline != 0 else 0

    # Determine direction and color
    if higher_is_worse:
        improved = change < 0
        arrow = '\u2193' if change < 0 else ('\u2191' if change > 0 else '\u2192')
    else:
        improved = change > 0
        arrow = '\u2191' if change > 0 else ('\u2193' if change < 0 else '\u2192')

    if abs(pct_change) < 5:
        color = COLORS['neutral']
    elif improved:
        color = COLORS['success']
    else:
        color = COLORS['danger']

    # Box with warm background and intentional border
    box = FancyBboxPatch((0.05, 0.1), 0.9, 0.8, boxstyle="round,pad=0.02",
                         facecolor=color, alpha=0.08, edgecolor=COLORS['putty'],
                         linewidth=2)
    ax.add_patch(box)

    # Arrow and change in points
    sign = '+' if change > 0 else ''
    ax.text(0.5, 0.6, f'{arrow} {sign}{change:.0f} pts', fontsize=14,
            ha='center', va='center', color=color, fontweight='bold')
    # Percent change
    sign_pct = '+' if pct_change > 0 else ''
    ax.text(0.5, 0.35, f'({sign_pct}{pct_change:.0f}%)', fontsize=10,
            ha='center', va='center', color=COLORS['warm_dark'])


def normalize_to_100(score, score_min, score_max):
    """Normalize a raw score to 0-100 scale."""
    if pd.isna(score):
        return np.nan
    return ((score - score_min) / (score_max - score_min)) * 100


def create_acute_vertical_bar(ax, participant_score, measure_key, norm_info):
    """Create a vertical bar for an acute experience measure.

    Shows normalized 0-100 score, published norm comparison, definition.
    Designed to sit in a column layout (4 across).
    """
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    score_min, score_max = norm_info['range']
    name = norm_info['name']
    definition = norm_info.get('definition', '')
    published_mean = norm_info.get('published_mean')
    published_source = norm_info.get('published_source', '')

    # Title at top
    ax.text(0.5, 0.98, name, fontsize=8.5, fontweight='bold', color=COLORS['dark'],
            va='top', ha='center', linespacing=1.2)

    # Definition below title
    ax.text(0.5, 0.82, definition, fontsize=6, color=COLORS['warm_gray'],
            va='top', ha='center', style='italic', linespacing=1.2)

    if pd.isna(participant_score):
        ax.text(0.5, 0.4, 'No data', ha='center', va='center',
                fontsize=10, color=COLORS['sage'])
        return

    # Normalize score to 0-100
    normalized_100 = normalize_to_100(participant_score, score_min, score_max)
    normalized_frac = max(0, min(1, normalized_100 / 100))

    # Vertical bar dimensions
    bar_left = 0.30
    bar_right = 0.70
    bar_bottom = 0.18
    bar_top = 0.70
    bar_height = bar_top - bar_bottom

    # Background bar — putty
    ax.fill([bar_left, bar_right, bar_right, bar_left],
            [bar_bottom, bar_bottom, bar_top, bar_top],
            color=COLORS['putty'], alpha=0.5)

    # Score fill — from bottom up
    fill_top = bar_bottom + bar_height * normalized_frac
    ax.fill([bar_left, bar_right, bar_right, bar_left],
            [bar_bottom, bar_bottom, fill_top, fill_top],
            color=COLORS['primary'], alpha=0.75)

    # Intentional border around bar
    ax.plot([bar_left, bar_right, bar_right, bar_left, bar_left],
            [bar_bottom, bar_bottom, bar_top, bar_top, bar_bottom],
            color=COLORS['warm_dark'], linewidth=1.5)

    # 0 and 100 labels on y-axis
    ax.text(bar_left - 0.05, bar_bottom, '0', fontsize=7, ha='right', va='center',
            color=COLORS['warm_gray'])
    ax.text(bar_left - 0.05, bar_top, '100', fontsize=7, ha='right', va='center',
            color=COLORS['warm_gray'])

    # Published norm line (horizontal dashed line across bar)
    if published_mean is not None:
        norm_frac = (published_mean - score_min) / (score_max - score_min)
        norm_y = bar_bottom + bar_height * norm_frac
        ax.plot([bar_left - 0.08, bar_right + 0.08], [norm_y, norm_y],
                color=COLORS['warm_dark'], linewidth=1.2, linestyle='--')
        ax.text(bar_right + 0.10, norm_y, f'Avg\n({published_source})',
                fontsize=5, color=COLORS['warm_gray'], va='center', ha='left',
                linespacing=1.1)

    # Complete mystical threshold (MEQ only)
    if 'complete_threshold' in norm_info:
        thresh = norm_info['complete_threshold']
        thresh_frac = (thresh - score_min) / (score_max - score_min)
        thresh_y = bar_bottom + bar_height * thresh_frac
        ax.plot([bar_left - 0.05, bar_right + 0.05], [thresh_y, thresh_y],
                color=COLORS['success'], linewidth=1.2, linestyle=':')
        is_complete = participant_score >= thresh
        ax.text(0.5, thresh_y + 0.02,
                f'Complete: {"Yes" if is_complete else "No"}',
                ha='center', va='bottom', fontsize=6,
                color=COLORS['success'] if is_complete else COLORS['warm_gray'],
                fontweight='bold')

    # Normalized score — large, centered above bar
    ax.text(0.5, 0.74, f'{normalized_100:.0f}', fontsize=18, fontweight='bold',
            color=COLORS['primary'], ha='center', va='bottom')

    # Raw score below bar
    scoring_label = 'mean' if norm_info['scoring'] == 'mean' else 'sum'
    ax.text(0.5, 0.12, f'Raw: {participant_score:.1f}', fontsize=7,
            color=COLORS['warm_gray'], ha='center', va='top')
    ax.text(0.5, 0.06, f'({scoring_label}, 0\u2013{score_max})', fontsize=6,
            color=COLORS['warm_gray'], ha='center', va='top')


def generate_individual_report(df, participant_id, timepoint, output_path,
                                clinic_name='Example Clinic', study_averages=None):
    """
    Generate a PDF report for an individual participant.

    Parameters:
    -----------
    df : DataFrame
        The insights data (wide format)
    participant_id : int
        The record_id of the participant
    timepoint : str
        The timepoint for this report ('3d', '1mo', '3mo', '6mo', '12mo')
    output_path : Path
        Where to save the PDF
    clinic_name : str
        Name of the clinic (kept for API compatibility, not shown in report)
    study_averages : dict, optional
        Average scores across the study for comparison
    """
    setup_figure_style()

    participant = df[df['record_id'] == participant_id]
    if len(participant) == 0:
        raise ValueError(f"Participant {participant_id} not found")
    participant = participant.iloc[0]

    # Determine timepoints to show (only up to current timepoint)
    all_outcome_timepoints = ['bl', '1mo', '3mo', '6mo', '12mo']
    timepoint_map = {
        '3d': (['bl'], '3-Day'),
        '1mo': (['bl', '1mo'], '1-Month'),
        '3mo': (['bl', '1mo', '3mo'], '3-Month'),
        '6mo': (['bl', '1mo', '3mo', '6mo'], '6-Month'),
        '12mo': (all_outcome_timepoints, '12-Month'),
    }
    show_timepoints, report_title = timepoint_map.get(timepoint, timepoint_map['12mo'])
    report_date = datetime.now().strftime('%B %d, %Y')
    logo_dir = Path(output_path).parent

    # =====================================================================
    # PAGE 1: Clinical Outcomes
    # =====================================================================
    fig1 = plt.figure(figsize=(8.5, 11))
    fig1.set_facecolor(COLORS['warm_bg'])
    create_header(fig1, report_title, report_date, logo_dir)

    # Introduction text
    intro_ax = fig1.add_axes([0.06, 0.855, 0.88, 0.045])
    intro_ax.set_facecolor(COLORS['warm_bg'])
    intro_ax.axis('off')
    intro_text = (
        f"This report summarizes your outcomes in the PATH Lab Psilocybin Therapy Study "
        f"through your {report_title.lower()} follow-up."
    )
    intro_ax.text(0, 0.5, intro_text, fontsize=9, color=COLORS['dark'], va='center',
                  wrap=True)

    # Divider line under intro
    div_ax = fig1.add_axes([0.06, 0.853, 0.88, 0.002])
    div_ax.set_facecolor(COLORS['putty'])
    div_ax.axis('off')

    # Chart positions — generous vertical space between sections
    chart_height = 0.18
    who5_bottom = 0.63
    phq9_bottom = 0.38
    gad7_bottom = 0.13

    # === WHO-5 Section ===
    who5_scores = [participant.get(f'who5_total_{tp}', np.nan) for tp in show_timepoints]
    ax_who5 = fig1.add_axes([0.08, who5_bottom, 0.56, chart_height])
    create_score_chart(ax_who5, show_timepoints, who5_scores,
                       'Wellbeing (WHO-5)', (0, 100), WHO5_SEVERITY,
                       y_ticks=[0, 25, 50, 75, 100])

    ax_who5_change = fig1.add_axes([0.70, who5_bottom + 0.03, 0.24, chart_height - 0.06])
    baseline_who5 = participant.get('who5_total_bl', np.nan)
    current_who5 = participant.get(f'who5_total_{timepoint}', np.nan)
    create_change_summary(ax_who5_change, baseline_who5, current_who5, 'WHO-5',
                          higher_is_worse=False)

    # === PHQ-9 Section ===
    phq9_scores = [participant.get(f'phq9_total_{tp}', np.nan) for tp in show_timepoints]
    ax_phq9 = fig1.add_axes([0.08, phq9_bottom, 0.56, chart_height])
    create_score_chart(ax_phq9, show_timepoints, phq9_scores,
                       'Depression Severity (PHQ-9)', (0, 27), PHQ9_SEVERITY,
                       y_ticks=[0, 5, 10, 15, 20, 25])

    ax_phq9_change = fig1.add_axes([0.70, phq9_bottom + 0.03, 0.24, chart_height - 0.06])
    baseline_phq9 = participant.get('phq9_total_bl', np.nan)
    current_phq9 = participant.get(f'phq9_total_{timepoint}', np.nan)
    create_change_summary(ax_phq9_change, baseline_phq9, current_phq9, 'PHQ-9',
                          higher_is_worse=True)

    # === GAD-7 Section ===
    gad7_scores = [participant.get(f'gad7_total_{tp}', np.nan) for tp in show_timepoints]
    ax_gad7 = fig1.add_axes([0.08, gad7_bottom, 0.56, chart_height])
    create_score_chart(ax_gad7, show_timepoints, gad7_scores,
                       'Anxiety (GAD-7)', (0, 21), GAD7_SEVERITY,
                       y_ticks=[0, 5, 10, 15, 20])

    ax_gad7_change = fig1.add_axes([0.70, gad7_bottom + 0.03, 0.24, chart_height - 0.06])
    baseline_gad7 = participant.get('gad7_total_bl', np.nan)
    current_gad7 = participant.get(f'gad7_total_{timepoint}', np.nan)
    create_change_summary(ax_gad7_change, baseline_gad7, current_gad7, 'GAD-7',
                          higher_is_worse=True)

    # Thank-you / encouragement text
    thanks_ax = fig1.add_axes([0.06, 0.06, 0.88, 0.05])
    thanks_ax.set_facecolor(COLORS['warm_bg'])
    thanks_ax.axis('off')
    thanks_text = (
        "Thank you for your ongoing participation in our study. Your involvement helps us "
        "better understand how and for whom psychedelics work, as well as associated "
        "real-world benefits and risks."
    )
    thanks_ax.text(0.5, 0.5, thanks_text, fontsize=7.5, color=COLORS['warm_gray'],
                   va='center', ha='center', style='italic', wrap=True)

    # Footer with logos
    create_footer_with_logos(fig1, logo_dir)

    # =====================================================================
    # PAGE 2: Acute Experience
    # =====================================================================
    fig2 = plt.figure(figsize=(8.5, 11))
    fig2.set_facecolor(COLORS['warm_bg'])
    create_header(fig2, report_title, report_date, logo_dir)

    # Intro
    acute_intro = fig2.add_axes([0.06, 0.855, 0.88, 0.045])
    acute_intro.set_facecolor(COLORS['warm_bg'])
    acute_intro.axis('off')
    acute_intro.text(0, 0.5,
                     'Your acute dosing session experience, compared to published study norms. '
                     'All scores are normalized to a 0\u2013100 scale for comparison.',
                     fontsize=9, color=COLORS['dark'], va='center')

    # Divider
    div_ax2 = fig2.add_axes([0.06, 0.853, 0.88, 0.002])
    div_ax2.set_facecolor(COLORS['putty'])
    div_ax2.axis('off')

    # Section title
    acute_title = fig2.add_axes([0.05, 0.80, 0.9, 0.04])
    acute_title.set_facecolor(COLORS['warm_bg'])
    acute_title.axis('off')
    acute_title.text(0, 0.5, 'Acute Experience Measures', fontsize=14, fontweight='bold',
                     color=COLORS['dark'], va='center')
    acute_title.text(1.0, 0.5, 'Normalized to 0\u2013100 scale', fontsize=8,
                     color=COLORS['warm_gray'], va='center', ha='right', style='italic')

    # 4 measures in columns: MEQ-4, CEQ-7, PIQ, EBI
    col_width = 0.20
    col_gap = 0.03
    col_start = 0.06
    bar_bottom = 0.14
    bar_height = 0.64

    # MEQ-4
    meq_col = 'meq4_mean_3d' if 'meq4_mean_3d' in df.columns else 'meq4_total_3d'
    meq_score = participant.get(meq_col, np.nan)
    ax_meq = fig2.add_axes([col_start, bar_bottom, col_width, bar_height])
    create_acute_vertical_bar(ax_meq, meq_score, 'meq4', ACUTE_NORMS['meq4'])

    # CEQ-7
    ceq_x = col_start + col_width + col_gap
    ceq_score = participant.get('ceq_total_3d', np.nan)
    ax_ceq = fig2.add_axes([ceq_x, bar_bottom, col_width, bar_height])
    create_acute_vertical_bar(ax_ceq, ceq_score, 'ceq', ACUTE_NORMS['ceq'])

    # PIQ
    piq_x = ceq_x + col_width + col_gap
    piq_score = participant.get('piq_total_3d', np.nan)
    ax_piq = fig2.add_axes([piq_x, bar_bottom, col_width, bar_height])
    create_acute_vertical_bar(ax_piq, piq_score, 'piq', ACUTE_NORMS['piq'])

    # EBI
    ebi_x = piq_x + col_width + col_gap
    ebi_score = participant.get('ebi_total_3d', np.nan)
    ax_ebi = fig2.add_axes([ebi_x, bar_bottom, col_width, bar_height])
    create_acute_vertical_bar(ax_ebi, ebi_score, 'ebi', ACUTE_NORMS['ebi'])

    # Encouragement text for acute page
    encourage_ax = fig2.add_axes([0.06, 0.06, 0.88, 0.05])
    encourage_ax.set_facecolor(COLORS['warm_bg'])
    encourage_ax.axis('off')
    encourage_text = (
        "As you continue to complete follow-up surveys, we will be able to share more about "
        "how your wellbeing, depression severity, and anxiety change over time. We are grateful "
        "for the time you dedicate to this research."
    )
    encourage_ax.text(0.5, 0.5, encourage_text, fontsize=7.5, color=COLORS['warm_gray'],
                      va='center', ha='center', style='italic', wrap=True)

    create_footer_with_logos(fig2, logo_dir)

    # Save both pages to PDF
    with PdfPages(output_path) as pdf:
        pdf.savefig(fig1, bbox_inches='tight', dpi=150,
                    facecolor=COLORS['warm_bg'], edgecolor='none')
        pdf.savefig(fig2, bbox_inches='tight', dpi=150,
                    facecolor=COLORS['warm_bg'], edgecolor='none')

    plt.close('all')

    print(f"Generated report: {output_path}")
    return output_path


def main():
    """Generate example individual reports with positive outcomes."""
    data_path = Path(__file__).parent.parent / 'data' / 'insights.csv'
    df = pd.read_csv(data_path)

    output_dir = Path(__file__).parent.parent / 'reports'
    output_dir.mkdir(exist_ok=True)

    # Use participants with positive changes across all measures
    # ID 31: PHQ9 -7, GAD7 -4, WHO5 +24 at 1mo
    # ID 30: PHQ9 -6, GAD7 -2, WHO5 +48 at 6mo
    generate_individual_report(
        df, 31, '3d',
        output_dir / 'individual_report_example_3d.pdf'
    )

    generate_individual_report(
        df, 31, '1mo',
        output_dir / 'individual_report_example_1mo.pdf'
    )

    generate_individual_report(
        df, 30, '6mo',
        output_dir / 'individual_report_example_6mo.pdf'
    )

    print(f"\nReports saved to: {output_dir}")


if __name__ == '__main__':
    main()
