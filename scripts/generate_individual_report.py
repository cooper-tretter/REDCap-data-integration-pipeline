"""
Individual Participant Report Generator
=======================================

Generates personalized PDF reports for study participants showing their
progress across timepoints with visualizations and interpretations.

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

# Standardized questionnaire items (for notable changes section)
PHQ9_ITEMS = {
    1: "Little interest or pleasure in doing things",
    2: "Feeling down, depressed, or hopeless",
    3: "Trouble falling or staying asleep, or sleeping too much",
    4: "Feeling tired or having little energy",
    5: "Poor appetite or overeating",
    6: "Feeling bad about yourself",
    7: "Trouble concentrating on things",
    8: "Moving or speaking slowly (or being fidgety/restless)",
    9: "Thoughts of self-harm",
}

GAD7_ITEMS = {
    1: "Feeling nervous, anxious, or on edge",
    2: "Not being able to stop or control worrying",
    3: "Worrying too much about different things",
    4: "Trouble relaxing",
    5: "Being so restless it's hard to sit still",
    6: "Becoming easily annoyed or irritable",
    7: "Feeling afraid something awful might happen",
}

WHO5_ITEMS = {
    1: "I have felt cheerful and in good spirits",
    2: "I have felt calm and relaxed",
    3: "I have felt active and vigorous",
    4: "I woke up feeling fresh and rested",
    5: "My daily life has been filled with things that interest me",
}

# Item score ranges
ITEM_RANGES = {
    'phq9': (0, 3),  # 0-3 scale
    'gad7': (0, 3),  # 0-3 scale
    'who5': (0, 5),  # 0-5 scale (raw, before x4)
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


def create_header(fig, participant_id, report_type, report_date, clinic_name='Example Clinic', logo_dir=None):
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
    header_ax.text(0.97, 0.70, f'{report_type} Progress Report', fontsize=12,
                   color=COLORS['primary'], va='center', ha='right', fontweight='bold')
    header_ax.text(0.97, 0.45, f'{clinic_name}', fontsize=9,
                   color=COLORS['primary'], va='center', ha='right')
    header_ax.text(0.97, 0.20, f'Participant: {participant_id}  |  {report_date}', fontsize=8,
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


def create_score_chart(ax, timepoints, scores, scale_name, y_range, severity_bands):
    """Create a line chart showing score progression with severity bands."""
    valid_data = [(tp, score) for tp, score in zip(timepoints, scores) if not pd.isna(score)]
    if not valid_data:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                fontsize=12, color=COLORS['sage'])
        ax.set_title(scale_name, fontweight='bold', color=COLORS['dark'])
        return

    tps, vals = zip(*valid_data)
    x_positions = [list(TIMEPOINT_LABELS.keys()).index(tp) for tp in tps]

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

    # Formatting with y-axis severity labels
    ax.set_xlim(-0.5, len(TIMEPOINT_LABELS) - 0.5)
    ax.set_ylim(y_range)
    ax.set_xticks(range(len(TIMEPOINT_LABELS)))
    ax.set_xticklabels(list(TIMEPOINT_LABELS.values()), fontsize=8)
    ax.set_title(scale_name, fontweight='bold', color=COLORS['dark'], pad=8)

    # Y-axis with severity labels instead of legend
    y_ticks = []
    y_labels = []
    for low, high, label, color in severity_bands:
        mid = (low + high) / 2
        y_ticks.append(mid)
        y_labels.append(label)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=7)

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


def find_notable_item_changes(participant, measure, items_dict, item_range,
                               baseline_tp='bl', current_tp='1mo', only_positive=True):
    """
    Find items where participant had drastic positive change (top 75% to bottom 25% or vice versa).

    Returns list of tuples: (item_num, question_text, baseline_score, current_score, improved)
    Only returns improvements by default.
    """
    notable = []
    min_score, max_score = item_range
    score_range = max_score - min_score

    # Thresholds: top 25% and bottom 25%
    low_threshold = min_score + 0.25 * score_range
    high_threshold = min_score + 0.75 * score_range

    for item_num, question in items_dict.items():
        bl_col = f'{measure}_{item_num}_{baseline_tp}'
        curr_col = f'{measure}_{item_num}_{current_tp}'

        bl_score = participant.get(bl_col, np.nan)
        curr_score = participant.get(curr_col, np.nan)

        if pd.isna(bl_score) or pd.isna(curr_score):
            continue

        # Check for drastic change
        was_high = bl_score >= high_threshold
        was_low = bl_score <= low_threshold
        now_high = curr_score >= high_threshold
        now_low = curr_score <= low_threshold

        # Determine if this is improvement
        # For PHQ9/GAD7: lower is better. For WHO5: higher is better
        if measure in ['phq9', 'gad7']:
            improved = curr_score < bl_score
            is_positive_drastic = was_high and now_low  # High symptoms -> low symptoms
        else:
            improved = curr_score > bl_score
            is_positive_drastic = was_low and now_high  # Low wellbeing -> high wellbeing

        if is_positive_drastic and (not only_positive or improved):
            notable.append((item_num, question, bl_score, curr_score, improved))

    return notable


def create_notable_changes_section(ax, notable_changes, measure_name, higher_is_worse=True):
    """Create a section showing notable item-level changes."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    if not notable_changes:
        return

    y_pos = 0.9
    ax.text(0, y_pos, f'Notable Changes in {measure_name}:', fontsize=9,
            fontweight='bold', color=COLORS['dark'], va='top')

    y_pos -= 0.15
    for item_num, question, bl_score, curr_score, improved in notable_changes[:2]:  # Max 2 items
        color = COLORS['success'] if improved else COLORS['danger']
        arrow = '\u2193' if (higher_is_worse and curr_score < bl_score) or \
                           (not higher_is_worse and curr_score > bl_score) else '\u2191'

        # Truncate question if too long
        if len(question) > 50:
            question = question[:47] + '...'

        ax.text(0.02, y_pos, f'"{question}"', fontsize=8,
                color=COLORS['dark'], va='top', style='italic')
        y_pos -= 0.12
        ax.text(0.02, y_pos, f'{arrow} {bl_score:.0f} \u2192 {curr_score:.0f}',
                fontsize=9, color=color, fontweight='bold', va='top')
        y_pos -= 0.18


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
        Name of the clinic for the report header
    study_averages : dict, optional
        Average scores across the study for comparison
    """
    setup_figure_style()

    participant = df[df['record_id'] == participant_id]
    if len(participant) == 0:
        raise ValueError(f"Participant {participant_id} not found")
    participant = participant.iloc[0]

    # Determine timepoints to show
    timepoint_map = {
        '1mo': (['bl', '3d', '1mo'], '1-Month'),
        '3mo': (['bl', '3d', '1mo', '3mo'], '3-Month'),
        '6mo': (['bl', '3d', '1mo', '3mo', '6mo'], '6-Month'),
        '12mo': (list(TIMEPOINT_LABELS.keys()), '12-Month'),
    }
    show_timepoints, report_title = timepoint_map.get(timepoint, timepoint_map['12mo'])
    report_date = datetime.now().strftime('%B %d, %Y')
    logo_dir = Path(output_path).parent

    # Find notable item changes
    phq9_notable = find_notable_item_changes(participant, 'phq9', PHQ9_ITEMS,
                                              ITEM_RANGES['phq9'], 'bl', timepoint)
    gad7_notable = find_notable_item_changes(participant, 'gad7', GAD7_ITEMS,
                                              ITEM_RANGES['gad7'], 'bl', timepoint)
    who5_notable = find_notable_item_changes(participant, 'who5', WHO5_ITEMS,
                                              ITEM_RANGES['who5'], 'bl', timepoint)

    has_notable = phq9_notable or gad7_notable or who5_notable

    # Create figure
    fig = plt.figure(figsize=(8.5, 11))
    create_header(fig, f'ID-{participant_id:04d}', report_title, report_date, clinic_name, logo_dir)

    # Introduction
    intro_ax = fig.add_axes([0.05, 0.86, 0.9, 0.05])
    intro_ax.axis('off')
    intro_text = (
        f"This report summarizes your progress in the PATH Lab Psilocybin Therapy Study through "
        f"your {report_title.lower()} follow-up."
    )
    intro_ax.text(0, 0.5, intro_text, fontsize=9, color=COLORS['dark'], va='center')

    # Layout adjustments based on whether we have notable changes
    # Footer is 0.06 tall, so content starts at 0.07
    if has_notable:
        chart_height = 0.15
        phq9_bottom = 0.66
        gad7_bottom = 0.46
        who5_bottom = 0.26
        notable_bottom = 0.07
    else:
        chart_height = 0.18
        phq9_bottom = 0.62
        gad7_bottom = 0.40
        who5_bottom = 0.18

    # === PHQ-9 Section ===
    phq9_scores = [participant.get(f'phq9_total_{tp}', np.nan) for tp in show_timepoints]
    ax_phq9 = fig.add_axes([0.08, phq9_bottom, 0.60, chart_height])
    create_score_chart(ax_phq9, show_timepoints, phq9_scores,
                       'Depression (PHQ-9)', (0, 27), PHQ9_SEVERITY)

    ax_phq9_change = fig.add_axes([0.72, phq9_bottom + 0.02, 0.24, chart_height - 0.04])
    baseline_phq9 = participant.get('phq9_total_bl', np.nan)
    current_phq9 = participant.get(f'phq9_total_{timepoint}', np.nan)
    create_change_summary(ax_phq9_change, baseline_phq9, current_phq9, 'PHQ-9', higher_is_worse=True)

    # === GAD-7 Section ===
    gad7_scores = [participant.get(f'gad7_total_{tp}', np.nan) for tp in show_timepoints]
    ax_gad7 = fig.add_axes([0.08, gad7_bottom, 0.60, chart_height])
    create_score_chart(ax_gad7, show_timepoints, gad7_scores,
                       'Anxiety (GAD-7)', (0, 21), GAD7_SEVERITY)

    ax_gad7_change = fig.add_axes([0.72, gad7_bottom + 0.02, 0.24, chart_height - 0.04])
    baseline_gad7 = participant.get('gad7_total_bl', np.nan)
    current_gad7 = participant.get(f'gad7_total_{timepoint}', np.nan)
    create_change_summary(ax_gad7_change, baseline_gad7, current_gad7, 'GAD-7', higher_is_worse=True)

    # === WHO-5 Section ===
    who5_scores = [participant.get(f'who5_total_{tp}', np.nan) for tp in show_timepoints]
    ax_who5 = fig.add_axes([0.08, who5_bottom, 0.60, chart_height])
    create_score_chart(ax_who5, show_timepoints, who5_scores,
                       'Wellbeing (WHO-5)', (0, 100), WHO5_SEVERITY)

    ax_who5_change = fig.add_axes([0.72, who5_bottom + 0.02, 0.24, chart_height - 0.04])
    baseline_who5 = participant.get('who5_total_bl', np.nan)
    current_who5 = participant.get(f'who5_total_{timepoint}', np.nan)
    create_change_summary(ax_who5_change, baseline_who5, current_who5, 'WHO-5', higher_is_worse=False)

    # === Notable Changes Section ===
    if has_notable:
        notable_ax = fig.add_axes([0.05, notable_bottom, 0.9, 0.16])
        notable_ax.set_xlim(0, 1)
        notable_ax.set_ylim(0, 1)
        notable_ax.axis('off')

        # Section header
        notable_ax.fill([0, 1, 1, 0], [0.85, 0.85, 1, 1], color=COLORS['cream'])
        notable_ax.text(0.02, 0.92, 'Notable Improvements', fontsize=11,
                       fontweight='bold', color=COLORS['dark'], va='center')

        # Display notable changes in columns
        col_width = 0.32
        col_positions = [0.02, 0.35, 0.68]

        # (measure_name, notable_changes, higher_is_worse, max_score)
        all_notable = [
            ('Depression', phq9_notable, True, 3),
            ('Anxiety', gad7_notable, True, 3),
            ('Wellbeing', who5_notable, False, 5),
        ]

        for i, (measure_name, changes, higher_is_worse, max_score) in enumerate(all_notable):
            if not changes:
                continue
            x_start = col_positions[i]
            y_pos = 0.75

            notable_ax.text(x_start, y_pos, f'{measure_name}:', fontsize=9,
                           fontweight='bold', color=COLORS['primary'], va='top')
            y_pos -= 0.12

            for item_num, question, bl_score, curr_score, improved in changes[:1]:
                color = COLORS['success']  # Only showing positive changes

                # Show full question with text wrapping
                notable_ax.text(x_start, y_pos, f'"{question}"', fontsize=7,
                               color=COLORS['dark'], va='top', style='italic')
                y_pos -= 0.25

                if higher_is_worse:
                    arrow = '\u2193'  # Down arrow for PHQ9/GAD7 improvement
                else:
                    arrow = '\u2191'  # Up arrow for WHO5 improvement

                # Show scores with "out of X" below each number
                notable_ax.text(x_start, y_pos, f'{bl_score:.0f}', fontsize=12,
                               color=color, fontweight='bold', va='top', ha='left')
                notable_ax.text(x_start, y_pos - 0.08, f'out of {max_score}', fontsize=6,
                               color=COLORS['sage'], va='top', ha='left')
                notable_ax.text(x_start + 0.06, y_pos, f' {arrow} ', fontsize=12,
                               color=color, fontweight='bold', va='top', ha='left')
                notable_ax.text(x_start + 0.12, y_pos, f'{curr_score:.0f}', fontsize=12,
                               color=color, fontweight='bold', va='top', ha='left')
                notable_ax.text(x_start + 0.12, y_pos - 0.08, f'out of {max_score}', fontsize=6,
                               color=COLORS['sage'], va='top', ha='left')

    # Footer with logos
    create_footer_with_logos(fig, logo_dir)

    plt.savefig(output_path, format='pdf', bbox_inches='tight', dpi=150,
                facecolor=COLORS['white'])
    plt.close()

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
