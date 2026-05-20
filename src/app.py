"""Streamlit GUI for Resume Optimizer.

Run with:
    streamlit run src/app.py
"""

import tempfile
from pathlib import Path

import streamlit as st

from main import analyze_ats, build_report, fetch_job_description_from_url, read_text

try:
    from cover_letter_generator import generate_cover_letter, save_cover_letter
except Exception:
    generate_cover_letter = None
    save_cover_letter = None


st.set_page_config(
    page_title='Resume Optimizer',
    page_icon='📄',
    layout='wide'
)


st.title('Resume Optimizer')
st.caption('ATS scoring, resume analysis, job matching, and cover letter generation.')


with st.sidebar:
    st.header('Inputs')
    resume_file = st.file_uploader('Upload Resume', type=['txt', 'pdf', 'docx'])
    job_file = st.file_uploader('Upload Job Description', type=['txt', 'pdf', 'docx'])
    job_url = st.text_input('Or paste job posting URL')

    st.divider()
    st.header('Cover Letter')
    generate_letter = st.checkbox('Generate cover letter')
    company_name = st.text_input('Company name', value='the company')
    role_title = st.text_input('Role title', value='the role')
    language = st.selectbox('Language', ['en', 'ar'])
    tone = st.selectbox('Arabic tone', ['modern', 'formal', 'executive'])

    run_button = st.button('Analyze Resume', type='primary')


def save_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def load_resume_text(uploaded_file):
    if uploaded_file is None:
        st.error('Please upload a resume file.')
        return None

    path = save_uploaded_file(uploaded_file)
    return read_text(path)


def load_job_text(uploaded_file, url):
    if url:
        return fetch_job_description_from_url(url)

    if uploaded_file is None:
        st.error('Please upload a job description file or paste a job URL.')
        return None

    path = save_uploaded_file(uploaded_file)
    return read_text(path)


if run_button:
    try:
        resume_text = load_resume_text(resume_file)
        job_text = load_job_text(job_file, job_url)

        if resume_text and job_text:
            results = analyze_ats(resume_text, job_text)
            report = build_report(results)

            score = results['ats_score']

            st.subheader('ATS Score')
            st.metric('Overall Score', f'{score} / 100')

            st.subheader('Score Breakdown')
            st.dataframe(
                [
                    {'Category': key.replace('_', ' ').title(), 'Score': value}
                    for key, value in results['component_scores'].items()
                ],
                use_container_width=True
            )

            col1, col2 = st.columns(2)

            with col1:
                st.subheader('Matched Keywords')
                st.write(', '.join(results['matched_keywords']) or 'No strong matches found.')

                st.subheader('Matched Hard Skills')
                st.write(', '.join(results['matched_skills']) or 'No matched hard skills found.')

            with col2:
                st.subheader('Missing Keywords')
                st.write(', '.join(results['missing_keywords'][:25]) or 'No major missing keywords found.')

                st.subheader('Missing Hard Skills')
                st.write(', '.join(results['missing_skills']) or 'No missing hard skills found.')

            st.subheader('Suggestions')
            for suggestion in results['suggestions']:
                st.write(f'- {suggestion}')

            st.download_button(
                label='Download ATS Report',
                data=report,
                file_name='ats_resume_report.txt',
                mime='text/plain'
            )

            if generate_letter:
                if generate_cover_letter is None:
                    st.warning('Cover letter module is unavailable.')
                else:
                    with st.spinner('Generating cover letter...'):
                        letter = generate_cover_letter(
                            resume_text=resume_text,
                            job_description=job_text,
                            company_name=company_name,
                            role_title=role_title,
                            language=language,
                            tone=tone,
                        )

                    st.subheader('Generated Cover Letter')
                    st.text_area('Cover Letter', letter, height=300)
                    st.download_button(
                        label='Download Cover Letter',
                        data=letter,
                        file_name='cover_letter_ar.txt' if language == 'ar' else 'cover_letter_en.txt',
                        mime='text/plain'
                    )

    except Exception as error:
        st.error(f'Error: {error}')
else:
    st.info('Upload a resume and job description, or paste a job posting URL, then click Analyze Resume.')
