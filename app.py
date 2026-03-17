"""
PATH Lab REDCap Data Integration Pipeline — Web Interface

A Streamlit app that provides a user-friendly interface for:
1. Running the REDCap data integration (upload → process → download)
2. Generating individual participant PDF reports
3. Generating clinic quarterly PDF reports
"""

import streamlit as st
import pandas as pd
import tempfile
import io
import sys
from pathlib import Path

# Add scripts directory to path so we can import the existing modules
SCRIPTS_DIR = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

# -- Page config --
st.set_page_config(
    page_title='PATH Lab Data Pipeline',
    page_icon='🧬',
    layout='wide',
)

# -- Brand colors --
PRIMARY = '#394F79'
DARK = '#253D6C'
SAGE = '#7E846F'
CREAM = '#FFEFDD'

# -- Custom CSS --
st.markdown(f"""
<style>
    .stApp {{
        background-color: #fafafa;
    }}
    h1, h2, h3 {{
        color: {DARK};
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {SAGE};
    }}
    .stTabs [aria-selected="true"] {{
        color: {PRIMARY};
    }}
    div.stDownloadButton > button {{
        background-color: {PRIMARY};
        color: white;
        border: none;
    }}
    div.stDownloadButton > button:hover {{
        background-color: {DARK};
        color: white;
        border: none;
    }}
    .success-box {{
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }}
    .info-box {{
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: {CREAM};
        border: 1px solid #e0d5c5;
        color: {DARK};
        margin: 1rem 0;
    }}
</style>
""", unsafe_allow_html=True)


# -- Header --
logo_path = Path(__file__).parent / 'reports' / 'PATHLogo.png'
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=80)
with col_title:
    st.title('PATH Lab Data Pipeline')
    st.caption('REDCap Data Integration & Report Generation')

st.divider()

# -- Tabs --
tab_integrate, tab_individual, tab_clinic = st.tabs([
    '1. Data Integration',
    '2. Individual Reports',
    '3. Clinic Reports',
])


# ============================================================
# TAB 1: Data Integration
# ============================================================
with tab_integrate:
    st.header('Run Data Integration')
    st.markdown(
        'Upload a REDCap export file (Excel or CSV) and the pipeline will transform it '
        'into a clean, wide-format dataset with calculated scores and analytical tabs.'
    )

    uploaded_file = st.file_uploader(
        'Upload REDCap export',
        type=['xlsx', 'csv'],
        key='integrate_upload',
        help='Export from REDCap as Excel or CSV (raw data format).',
    )

    if uploaded_file:
        st.markdown(f'<div class="info-box">File loaded: <strong>{uploaded_file.name}</strong></div>',
                    unsafe_allow_html=True)

        if st.button('Run Integration', type='primary', key='run_integrate'):
            with st.spinner('Processing data... this may take a moment.'):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        tmpdir = Path(tmpdir)
                        input_path = tmpdir / uploaded_file.name
                        input_path.write_bytes(uploaded_file.getvalue())

                        from integrate import integrate_full
                        df_wide = integrate_full(str(input_path), str(tmpdir))

                        excel_path = tmpdir / 'insights.xlsx'
                        csv_path = tmpdir / 'insights.csv'

                        st.markdown('<div class="success-box">Integration complete!</div>',
                                    unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric('Participants', df_wide['record_id'].nunique())
                        with col2:
                            st.metric('Columns', len(df_wide.columns))

                        st.subheader('Preview')
                        preview_cols = [c for c in ['record_id', 'consent_nameprint', 'age', 'gender',
                                                     'phq9_total_bl', 'gad7_total_bl', 'who5_total_bl']
                                        if c in df_wide.columns]
                        st.dataframe(df_wide[preview_cols].head(15), use_container_width=True)

                        st.subheader('Download Results')
                        dl_col1, dl_col2 = st.columns(2)
                        with dl_col1:
                            if excel_path.exists():
                                st.download_button(
                                    'Download insights.xlsx',
                                    data=excel_path.read_bytes(),
                                    file_name='insights.xlsx',
                                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                )
                        with dl_col2:
                            if csv_path.exists():
                                st.download_button(
                                    'Download insights.csv',
                                    data=csv_path.read_bytes(),
                                    file_name='insights.csv',
                                    mime='text/csv',
                                )

                        # Store in session state for use in other tabs
                        st.session_state['insights_df'] = df_wide
                        st.session_state['insights_xlsx'] = excel_path.read_bytes() if excel_path.exists() else None
                        st.session_state['insights_csv'] = csv_path.read_bytes() if csv_path.exists() else None

                except Exception as e:
                    st.error(f'Integration failed: {e}')
                    st.exception(e)

    else:
        st.info('Upload a REDCap export file to get started, or use the sample data below.')
        if st.button('Use Sample Data', key='use_sample'):
            sample_path = Path(__file__).parent / 'data' / 'sample_data.xlsx'
            if sample_path.exists():
                with st.spinner('Processing sample data...'):
                    try:
                        with tempfile.TemporaryDirectory() as tmpdir:
                            tmpdir = Path(tmpdir)
                            from integrate import integrate_full
                            df_wide = integrate_full(str(sample_path), str(tmpdir))

                            excel_path = tmpdir / 'insights.xlsx'
                            csv_path = tmpdir / 'insights.csv'

                            st.markdown('<div class="success-box">Integration complete!</div>',
                                        unsafe_allow_html=True)

                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric('Participants', df_wide['record_id'].nunique())
                            with col2:
                                st.metric('Columns', len(df_wide.columns))

                            st.subheader('Preview')
                            preview_cols = [c for c in ['record_id', 'consent_nameprint', 'age', 'gender',
                                                         'phq9_total_bl', 'gad7_total_bl', 'who5_total_bl']
                                            if c in df_wide.columns]
                            st.dataframe(df_wide[preview_cols].head(15), use_container_width=True)

                            st.subheader('Download Results')
                            dl_col1, dl_col2 = st.columns(2)
                            with dl_col1:
                                if excel_path.exists():
                                    st.download_button(
                                        'Download insights.xlsx',
                                        data=excel_path.read_bytes(),
                                        file_name='insights.xlsx',
                                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                    )
                            with dl_col2:
                                if csv_path.exists():
                                    st.download_button(
                                        'Download insights.csv',
                                        data=csv_path.read_bytes(),
                                        file_name='insights.csv',
                                        mime='text/csv',
                                    )

                            st.session_state['insights_df'] = df_wide
                            st.session_state['insights_xlsx'] = excel_path.read_bytes() if excel_path.exists() else None
                            st.session_state['insights_csv'] = csv_path.read_bytes() if csv_path.exists() else None

                    except Exception as e:
                        st.error(f'Integration failed: {e}')
                        st.exception(e)
            else:
                st.warning('Sample data file not found. Generate it first with `python scripts/generate_sample_data.py`.')


# ============================================================
# TAB 2: Individual Participant Reports
# ============================================================
with tab_individual:
    st.header('Generate Individual Participant Report')
    st.markdown(
        'Create a personalized PDF progress report for a participant. '
        'Reports include PHQ-9, GAD-7, and WHO-5 score trajectories, '
        'change from baseline, and notable improvements.'
    )

    # Data source
    ind_data_source = st.radio(
        'Data source',
        ['Upload insights.csv', 'Use data from Tab 1', 'Use existing file on disk'],
        key='ind_data_source',
        horizontal=True,
    )

    ind_df = None

    if ind_data_source == 'Upload insights.csv':
        ind_upload = st.file_uploader('Upload insights.csv', type=['csv'], key='ind_upload')
        if ind_upload:
            ind_df = pd.read_csv(ind_upload)
    elif ind_data_source == 'Use data from Tab 1':
        if 'insights_df' in st.session_state:
            ind_df = st.session_state['insights_df']
            st.success('Using data from the integration tab.')
        else:
            st.warning('Run the integration in Tab 1 first.')
    else:
        disk_path = Path(__file__).parent / 'data' / 'insights.csv'
        if disk_path.exists():
            ind_df = pd.read_csv(disk_path)
            st.success(f'Loaded {disk_path.name} from disk.')
        else:
            st.warning('No insights.csv found on disk. Run integration first.')

    if ind_df is not None:
        col_id, col_tp, col_clinic = st.columns(3)

        participant_ids = sorted(ind_df['record_id'].unique())

        with col_id:
            selected_id = st.selectbox('Participant ID', participant_ids, key='ind_id')
        with col_tp:
            selected_tp = st.selectbox('Timepoint', ['1mo', '3mo', '6mo', '12mo'], key='ind_tp')
        with col_clinic:
            clinic_name = st.text_input('Clinic Name (optional)', value='', key='ind_clinic')

        if st.button('Generate Report', type='primary', key='gen_individual'):
            with st.spinner('Generating PDF report...'):
                try:
                    from generate_individual_report import generate_individual_report

                    with tempfile.TemporaryDirectory() as tmpdir:
                        output_path = Path(tmpdir) / f'report_{selected_id}_{selected_tp}.pdf'

                        generate_individual_report(
                            df=ind_df,
                            participant_id=selected_id,
                            timepoint=selected_tp,
                            output_path=output_path,
                            clinic_name=clinic_name if clinic_name else 'Study Clinic',
                        )

                        if output_path.exists():
                            st.markdown('<div class="success-box">Report generated!</div>',
                                        unsafe_allow_html=True)
                            st.download_button(
                                f'Download Report (Participant {selected_id}, {selected_tp})',
                                data=output_path.read_bytes(),
                                file_name=f'individual_report_{selected_id}_{selected_tp}.pdf',
                                mime='application/pdf',
                            )
                        else:
                            st.error('Report file was not created. The participant may not have data at this timepoint.')

                except Exception as e:
                    st.error(f'Report generation failed: {e}')
                    st.exception(e)


# ============================================================
# TAB 3: Clinic Quarterly Reports
# ============================================================
with tab_clinic:
    st.header('Generate Clinic Quarterly Report')
    st.markdown(
        'Create a quarterly PDF report for a clinic showing key metrics, '
        'comparison to study-wide averages, score trajectories, and MEQ-4 distribution.'
    )

    # Data source
    clinic_data_source = st.radio(
        'Data source',
        ['Upload insights.csv', 'Use data from Tab 1', 'Use existing file on disk'],
        key='clinic_data_source',
        horizontal=True,
    )

    clinic_df = None

    if clinic_data_source == 'Upload insights.csv':
        clinic_upload = st.file_uploader('Upload insights.csv', type=['csv'], key='clinic_upload')
        if clinic_upload:
            clinic_df = pd.read_csv(clinic_upload)
    elif clinic_data_source == 'Use data from Tab 1':
        if 'insights_df' in st.session_state:
            clinic_df = st.session_state['insights_df']
            st.success('Using data from the integration tab.')
        else:
            st.warning('Run the integration in Tab 1 first.')
    else:
        disk_path = Path(__file__).parent / 'data' / 'insights.csv'
        if disk_path.exists():
            clinic_df = pd.read_csv(disk_path)
            st.success(f'Loaded {disk_path.name} from disk.')
        else:
            st.warning('No insights.csv found on disk. Run integration first.')

    if clinic_df is not None:
        col_name, col_type = st.columns(2)

        with col_name:
            clinic_name_input = st.text_input('Clinic Name', value='', key='clinic_name_input')
        with col_type:
            report_type = st.selectbox('Report Type', ['Q2 (Mid-Year)', 'Q4 (Annual)'], key='clinic_type')

        st.markdown('**Filter participants** (optional) — select specific participant IDs for this clinic, '
                    'or leave blank to use all participants in the dataset.')

        participant_ids = sorted(clinic_df['record_id'].unique())
        selected_ids = st.multiselect(
            'Participant IDs (leave empty for all)',
            options=participant_ids,
            key='clinic_ids',
        )

        if st.button('Generate Report', type='primary', key='gen_clinic'):
            with st.spinner('Generating PDF report...'):
                try:
                    from generate_clinic_report import generate_clinic_report

                    report_type_code = 'Q2' if 'Q2' in report_type else 'Q4'

                    if selected_ids:
                        filtered_df = clinic_df[clinic_df['record_id'].isin(selected_ids)]
                    else:
                        filtered_df = clinic_df

                    with tempfile.TemporaryDirectory() as tmpdir:
                        output_path = Path(tmpdir) / f'clinic_report_{report_type_code}.pdf'

                        generate_clinic_report(
                            df=filtered_df,
                            clinic_name=clinic_name_input if clinic_name_input else 'Study Clinic',
                            report_type=report_type_code,
                            output_path=output_path,
                            study_df=clinic_df,
                        )

                        if output_path.exists():
                            st.markdown('<div class="success-box">Report generated!</div>',
                                        unsafe_allow_html=True)
                            st.download_button(
                                f'Download Clinic Report ({report_type_code})',
                                data=output_path.read_bytes(),
                                file_name=f'clinic_report_{report_type_code}.pdf',
                                mime='application/pdf',
                            )
                        else:
                            st.error('Report file was not created.')

                except Exception as e:
                    st.error(f'Report generation failed: {e}')
                    st.exception(e)


# -- Footer --
st.divider()
st.caption('PATH Lab — Real World Safety and Effectiveness Study of Psilocybin Therapy')
