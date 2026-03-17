"""
Individual Participant Report Generator
=======================================

Generates personalized PDF reports for study participants showing their
outcomes across timepoints with visualizations and interpretations.

Uses PATH Lab branding:
- Colors: #394F79 (primary), #253D6C (dark), #7E846F (sage), #FFEFDD (cream)
- Font: Montserrat
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

# PATH Lab Brand Colors
COLORS = {
    'primary': '#394F79',      # Primary blue
    'dark': '#253D6C',         # Dark blue
    'sage': '#7E846F',         # Sage green
    'cream': '#FFEFDD',        # Cream background
    'white': '#FFFFFF',
    'light_gray': '#E8E8E8',
    'success': '#4A7C59',      # Green for improvement
    'neutral': '#7E846F',      # Sage for no change (was yellow, now visible)
    'danger': '#A85454',       # Red for worsening
}

# Timepoint labels
TIMEPOINT_LABELS = {
    'bl': 'Baseline',
    '3d': '3 Days',
    '1mo': '1 Month',
    '3mo': '3 Months',
    '6mo': '6 Months',
    '12mo': '12 Months',
}

# Score interpretations with better color contrast
PHQ9_SEVERITY = [
    (0, 4, 'None-Minimal', '#4A7C59'),
    (5, 9, 'Mild', '#6B8E5B'),
    (10, 14, 'Moderate', '#7E846F'),
    (15, 19, 'Moderately Severe', '#A07050'),
    (20, 27, 'Severe', '#A85454'),
]

GAD7_SEVERITY = [
    (0, 4, 'Minimal', '#4A7C59'),
    (5, 9, 'Mild', '#6B8E5B'),
    (10, 14, 'Moderate', '#7E846F'),
    (15, 21, 'Severe', '#A85454'),
]

WHO5_SEVERITY = [
    (0, 28, 'Poor Wellbeing', '#A85454'),
    (29, 50, 'Low Wellbeing', '#7E846F'),
    (51, 100, 'Good Wellbeing', '#4A7C59'),
]

# Published norms for acute experience measures
# MEQ-4: Complete mystical experience threshold >= 3.0 (Griffiths et al., 2006, 2011)
# Published study norms (Barrett et al., 2015; Davis et al., 2020)
ACUTE_NORMS = {
    'meq4': {
        'name': 'Mystical Experience (MEQ-4)',
        'range': (0, 5),
        'scoring': 'mean',
        'complete_threshold': 3.0,
        'complete_label': 'Complete Mystical Experience',
        'published_mean': 3.5,
        'published_source': 'Barrett et al., 2015',
    },
    'ceq': {
        'name': 'Challenging Experience (CEQ-7)',
        'range': (0, 35),
        'scoring': 'sum',
        'published_mean': 14.0,
        'published_source': 'Barrett et al., 2016',
    },
    'piq': {
        'name': 'Psychological Insight (PIQ)',
        'range': (23, 115),
        'scoring': 'sum',
        'published_mean': 80.0,
        'published_source': 'Peill et al., 2022',
    },
}


def setup_figure_style():
    """Set up matplotlib style for PATH Lab branding."""
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Montserrat', 'Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.edgecolor'] = COLORS['sage']
    plt.rcParams['axes.labelcolor'] = COLORS['dark']
    plt.rcParams['xtick.color'] = COLORS['dark']
    plt.rcParams['ytick.color'] = COLORS['dark']
    plt.rcParams['figure.facecolor'] = COLORS['white']
    plt.rcParams['axes.facecolor'] = COLORS['white']


def create_header(fig, participant_id, report_type, report_date, logo_dir=None):
    """Create report header with PATH Lab branding and logo."""
    header_ax = fig.add_axes([0, 0.92, 1, 0.08])
    header_ax.set_facecolor(COLORS['cream'])
    header_ax.set_xlim(0, 1)
    header_ax.set_ylim(0, 1)
    header_ax.axis('off')

    # Try to load and display logo
    if logo_dir:
        try:
            logo = mpimg.imread(logo_dir / 'PATHLogo.png')
            logo_ax = fig.add_axes([0.02, 0.925, 0.15, 0.065])
            logo_ax.imshow(logo)
            logo_ax.axis('off')
        except Exception:
            pass

    # Report info on right
    header_ax.text(0.97, 0.70, f'{report_type} Outcomes Report', fontsize=12,
                   color=COLORS['primary'], va='center', ha='right', fontweight='bold')
    header_ax.text(0.97, 0.35, f'Participant: {participant_id}  |  {report_date}', fontsize=8,
                   color=COLORS['dark'], va='center', ha='right')


def create_footer_with_logos(fig, logo_dir):
    """Create footer with logos and attribution."""
    footer_ax = fig.add_axes([0, 0, 1, 0.06])
    footer_ax.set_facecolor(COLORS['cream'])
    footer_ax.set_xlim(0, 1)
    footer_ax.set_ylim(0, 1)
    footer_ax.axis('off')

    # Try to load and display logos
    try:
        path_logo = mpimg.imread(logo_dir / 'PATHLogo.png')
        logo_ax = fig.add_axes([0.02, 0.008, 0.12, 0.045])
        logo_ax.imshow(path_logo)
        logo_ax.axis('off')
    except Exception:
        pass

    # Try New School logo (PNG version)
    try:
        ns_logo = mpimg.imread(logo_dir / 'newschool_logo.png')
        ns_ax = fig.add_axes([0.15, 0.008, 0.12, 0.045])
        ns_ax.imshow(ns_logo)
        ns_ax.axis('off')
    except Exception:
        pass

    # Attribution text
    footer_ax.text(0.5, 0.7, 'This report was generated by the PATH Lab at the New School for Social Research',
                   ha='center', va='center', fontsize=7, color=COLORS['dark'], style='italic')
    footer_ax.text(0.5, 0.25, 'For informational purposes only. Please discuss with your healthcare provider.',
                   ha='center', va='center', fontsize=6, color=COLORS['sage'], style='italic')


def create_score_chart(ax, show_timepoints, scores, scale_name, y_range, severity_bands):
    """Create a line chart showing score progression with severity bands.

    Only shows x-axis ticks for timepoints the participant has reached.
    Numeric values on left y-axis, severity labels on right.
    """
    valid_data = [(tp, score) for tp, score in zip(show_timepoints, scores) if not pd.isna(score)]
    if not valid_data:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                fontsize=12, color=COLORS['sage'])
        ax.set_title(scale_name, fontweight='bold', color=COLORS['dark'])
        return

    tps, vals = zip(*valid_data)
    # Only use timepoints in show_timepoints for x positions
    x_positions = [show_timepoints.index(tp) for tp in tps]

    # Draw severity bands (simple fills, no outlines)
    for low, high, label, color in severity_bands:
        ax.axhspan(low, high, alpha=0.15, color=color)

    # Plot line and points (simple filled circles)
    ax.plot(x_positions, vals, '-', color=COLORS['primary'], linewidth=2.5)
    ax.scatter(x_positions, vals, s=80, color=COLORS['primary'], zorder=5)

    # Add value labels
    for x, y in zip(x_positions, vals):
        ax.annotate(f'{y:.0f}', (x, y), textcoords="offset points",
                    xytext=(0, 10), ha='center', fontsize=10, fontweight='bold',
                    color=COLORS['dark'])

    # X-axis: only show timepoints participant has reached
    ax.set_xlim(-0.5, len(show_timepoints) - 0.5)
    ax.set_ylim(y_range)
    ax.set_xticks(range(len(show_timepoints)))
    ax.set_xticklabels([TIMEPOINT_LABELS[tp] for tp in show_timepoints], fontsize=8)
    ax.set_title(scale_name, fontweight='bold', color=COLORS['dark'], pad=8)

    # Left y-axis: numeric values
    ax.yaxis.set_visible(True)
    ax.tick_params(axis='y', labelsize=8)

    # Right y-axis: severity labels
    ax2 = ax.twinx()
    ax2.set_ylim(y_range)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    y_ticks = []
    y_labels = []
    for low, high, label, color in severity_bands:
        mid = (low + high) / 2
        y_ticks.append(mid)
        y_labels.append(label)
    ax2.set_yticks(y_ticks)
    ax2.set_yticklabels(y_labels, fontsize=7, color=COLORS['sage'])
    ax2.tick_params(axis='y', length=0)

    ax.grid(True, axis='y', alpha=0.2, color=COLORS['sage'])


def create_change_summary(ax, baseline, current, label, higher_is_worse=True):
    """Create a simple change summary box."""
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
        status = 'Stable'
    elif improved:
        color = COLORS['success']
        status = 'Improved'
    else:
        color = COLORS['danger']
        status = 'Needs attention'

    # Simple box background
    ax.fill([0.05, 0.95, 0.95, 0.05], [0.1, 0.1, 0.9, 0.9],
            color=color, alpha=0.1)

    # Arrow and change
    ax.text(0.5, 0.7, f'{arrow} {abs(change):.0f} pts', fontsize=14,
            ha='center', va='center', color=color, fontweight='bold')
    ax.text(0.5, 0.4, f'({abs(pct_change):.0f}%)', fontsize=10,
            ha='center', va='center', color=COLORS['dark'])
    ax.text(0.5, 0.15, status, fontsize=9, ha='center', va='center',
            color=color, fontweight='bold')


def create_acute_bar(ax, participant_score, measure_key, norm_info):
    """Create a horizontal bar for an acute experience measure with published norm comparison."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    score_min, score_max = norm_info['range']
    name = norm_info['name']
    published_mean = norm_info.get('published_mean')
    published_source = norm_info.get('published_source', '')

    if pd.isna(participant_score):
        ax.text(0.5, 0.5, f'{name}\nNo data', ha='center', va='center',
                fontsize=10, color=COLORS['sage'])
        return

    # Normalize score to 0-1 for bar width
    normalized = (participant_score - score_min) / (score_max - score_min)
    normalized = max(0, min(1, normalized))

    bar_left = 0.25
    bar_width = 0.70
    bar_bottom = 0.30
    bar_height = 0.20

    # Background bar
    ax.fill([bar_left, bar_left + bar_width, bar_left + bar_width, bar_left],
            [bar_bottom, bar_bottom, bar_bottom + bar_height, bar_bottom + bar_height],
            color=COLORS['light_gray'], alpha=0.5)

    # Score bar
    ax.fill([bar_left, bar_left + bar_width * normalized, bar_left + bar_width * normalized, bar_left],
            [bar_bottom, bar_bottom, bar_bottom + bar_height, bar_bottom + bar_height],
            color=COLORS['primary'], alpha=0.7)

    # Published norm line
    if published_mean is not None:
        norm_x = bar_left + bar_width * ((published_mean - score_min) / (score_max - score_min))
        ax.plot([norm_x, norm_x], [bar_bottom - 0.05, bar_bottom + bar_height + 0.05],
                color=COLORS['sage'], linewidth=2, linestyle='--')
        ax.text(norm_x, bar_bottom - 0.12, f'Published avg\n({published_source})',
                ha='center', va='top', fontsize=6, color=COLORS['sage'])

    # Complete mystical threshold (MEQ only)
    if 'complete_threshold' in norm_info:
        thresh = norm_info['complete_threshold']
        thresh_x = bar_left + bar_width * ((thresh - score_min) / (score_max - score_min))
        ax.plot([thresh_x, thresh_x], [bar_bottom - 0.05, bar_bottom + bar_height + 0.05],
                color=COLORS['success'], linewidth=2, linestyle=':')
        is_complete = participant_score >= thresh
        label = norm_info['complete_label']
        ax.text(thresh_x, bar_bottom + bar_height + 0.12,
                f'{label}: {"Yes" if is_complete else "No"}',
                ha='center', va='bottom', fontsize=7,
                color=COLORS['success'] if is_complete else COLORS['sage'],
                fontweight='bold')

    # Title and score
    ax.text(0.0, 0.85, name, fontsize=10, fontweight='bold', color=COLORS['dark'], va='center')
    ax.text(0.0, 0.55, f'Score: {participant_score:.1f}', fontsize=11,
            color=COLORS['primary'], fontweight='bold', va='center')


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
        The timepoint for this report ('1mo', '3mo', '6mo', '12mo')
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
        '1mo': (['bl', '1mo'], '1-Month'),
        '3mo': (['bl', '1mo', '3mo'], '3-Month'),
        '6mo': (['bl', '1mo', '3mo', '6mo'], '6-Month'),
        '12mo': (all_outcome_timepoints, '12-Month'),
    }
    show_timepoints, report_title = timepoint_map.get(timepoint, timepoint_map['12mo'])
    report_date = datetime.now().strftime('%B %d, %Y')
    logo_dir = Path(output_path).parent

    # === PAGE 1: Clinical Outcomes ===
    fig1 = plt.figure(figsize=(8.5, 11))
    create_header(fig1, f'ID-{participant_id:04d}', report_title, report_date, logo_dir)

    # Introduction
    intro_ax = fig1.add_axes([0.05, 0.86, 0.9, 0.05])
    intro_ax.axis('off')
    intro_text = (
        f"This report summarizes your outcomes in the PATH Lab Psilocybin Therapy Study through "
        f"your {report_title.lower()} follow-up."
    )
    intro_ax.text(0, 0.5, intro_text, fontsize=9, color=COLORS['dark'], va='center')

    chart_height = 0.20
    # Lead with WHO-5 (wellbeing), then PHQ-9, then GAD-7
    who5_bottom = 0.62
    phq9_bottom = 0.38
    gad7_bottom = 0.14

    # === WHO-5 Section (first — wellbeing is relevant across individuals) ===
    who5_scores = [participant.get(f'who5_total_{tp}', np.nan) for tp in show_timepoints]
    ax_who5 = fig1.add_axes([0.08, who5_bottom, 0.58, chart_height])
    create_score_chart(ax_who5, show_timepoints, who5_scores,
                       'Wellbeing (WHO-5)', (0, 100), WHO5_SEVERITY)

    ax_who5_change = fig1.add_axes([0.72, who5_bottom + 0.02, 0.24, chart_height - 0.04])
    baseline_who5 = participant.get('who5_total_bl', np.nan)
    current_who5 = participant.get(f'who5_total_{timepoint}', np.nan)
    create_change_summary(ax_who5_change, baseline_who5, current_who5, 'WHO-5', higher_is_worse=False)

    # === PHQ-9 Section ===
    phq9_scores = [participant.get(f'phq9_total_{tp}', np.nan) for tp in show_timepoints]
    ax_phq9 = fig1.add_axes([0.08, phq9_bottom, 0.58, chart_height])
    create_score_chart(ax_phq9, show_timepoints, phq9_scores,
                       'Depression (PHQ-9)', (0, 27), PHQ9_SEVERITY)

    ax_phq9_change = fig1.add_axes([0.72, phq9_bottom + 0.02, 0.24, chart_height - 0.04])
    baseline_phq9 = participant.get('phq9_total_bl', np.nan)
    current_phq9 = participant.get(f'phq9_total_{timepoint}', np.nan)
    create_change_summary(ax_phq9_change, baseline_phq9, current_phq9, 'PHQ-9', higher_is_worse=True)

    # === GAD-7 Section ===
    gad7_scores = [participant.get(f'gad7_total_{tp}', np.nan) for tp in show_timepoints]
    ax_gad7 = fig1.add_axes([0.08, gad7_bottom, 0.58, chart_height])
    create_score_chart(ax_gad7, show_timepoints, gad7_scores,
                       'Anxiety (GAD-7)', (0, 21), GAD7_SEVERITY)

    ax_gad7_change = fig1.add_axes([0.72, gad7_bottom + 0.02, 0.24, chart_height - 0.04])
    baseline_gad7 = participant.get('gad7_total_bl', np.nan)
    current_gad7 = participant.get(f'gad7_total_{timepoint}', np.nan)
    create_change_summary(ax_gad7_change, baseline_gad7, current_gad7, 'GAD-7', higher_is_worse=True)

    # Footer with logos
    create_footer_with_logos(fig1, logo_dir)

    # === PAGE 2: Acute Experience ===
    fig2 = plt.figure(figsize=(8.5, 11))
    create_header(fig2, f'ID-{participant_id:04d}', report_title, report_date, logo_dir)

    # Intro
    acute_intro = fig2.add_axes([0.05, 0.86, 0.9, 0.05])
    acute_intro.axis('off')
    acute_intro.text(0, 0.5,
                     'Your acute dosing session experience, compared to published study norms.',
                     fontsize=9, color=COLORS['dark'], va='center')

    # Section title
    acute_title = fig2.add_axes([0.05, 0.80, 0.9, 0.04])
    acute_title.axis('off')
    acute_title.text(0, 0.5, 'Acute Experience Measures', fontsize=14, fontweight='bold',
                     color=COLORS['dark'], va='center')

    # MEQ-4
    meq_col = 'meq4_mean_3d' if 'meq4_mean_3d' in df.columns else 'meq4_total_3d'
    meq_score = participant.get(meq_col, np.nan)
    ax_meq = fig2.add_axes([0.05, 0.58, 0.9, 0.20])
    create_acute_bar(ax_meq, meq_score, 'meq4', ACUTE_NORMS['meq4'])

    # CEQ
    ceq_score = participant.get('ceq_total_3d', np.nan)
    ax_ceq = fig2.add_axes([0.05, 0.36, 0.9, 0.20])
    create_acute_bar(ax_ceq, ceq_score, 'ceq', ACUTE_NORMS['ceq'])

    # PIQ
    piq_score = participant.get('piq_total_3d', np.nan)
    ax_piq = fig2.add_axes([0.05, 0.14, 0.9, 0.20])
    create_acute_bar(ax_piq, piq_score, 'piq', ACUTE_NORMS['piq'])

    create_footer_with_logos(fig2, logo_dir)

    # Save both pages to PDF
    with PdfPages(output_path) as pdf:
        pdf.savefig(fig1, bbox_inches='tight', dpi=150,
                    facecolor=COLORS['white'], edgecolor='none')
        pdf.savefig(fig2, bbox_inches='tight', dpi=150,
                    facecolor=COLORS['white'], edgecolor='none')

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
