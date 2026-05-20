"""Arabic Streamlit GUI for Resume Optimizer.

Run with:
    streamlit run src/app.py
"""

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from main import analyze_ats, build_report, fetch_job_description_from_url, read_text

try:
    from cover_letter_generator import generate_cover_letter
except Exception:
    generate_cover_letter = None

try:
    from application_tracker import (
        STATUSES,
        add_application,
        read_applications,
        summarize_pipeline,
        update_application_status,
    )
except Exception:
    STATUSES = []
    add_application = None
    read_applications = None
    summarize_pipeline = None
    update_application_status = None

STATUS_AR = {
    'Saved': 'محفوظة',
    'Applied': 'تم التقديم',
    'Screening': 'فرز أولي',
    'Interview': 'مقابلة',
    'Offer': 'عرض وظيفي',
    'Rejected': 'مرفوضة',
    'Withdrawn': 'منسحبة',
}

CATEGORY_AR = {
    'keyword_match': 'مطابقة الكلمات المفتاحية',
    'hard_skills': 'المهارات التقنية',
    'required_sections': 'أقسام السيرة',
    'contact_info': 'بيانات التواصل',
    'measurable_impact': 'الأثر القابل للقياس',
    'action_verbs': 'أفعال الإنجاز',
}

st.set_page_config(
    page_title='محسّن السيرة الذاتية',
    page_icon='📄',
    layout='wide'
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], [class*="st-"] {
        font-family: 'IBM Plex Sans Arabic', 'Tajawal', 'Noto Sans Arabic', sans-serif !important;
    }

    .stApp {
        direction: rtl;
        text-align: right;
        background: #fafafa;
    }

    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
        background: #ffffff;
        border-left: 1px solid #e8e8e8;
    }

    h1, h2, h3, h4 {
        color: #1f2937;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .stButton > button,
    .stDownloadButton > button,
    button[kind="primary"] {
        border-radius: 12px !important;
        border: 1px solid #111827 !important;
        background: #111827 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 0.6rem 1rem !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div,
    .stDateInput input {
        border-radius: 12px !important;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 18px;
    }

    div[data-testid="stDataFrame"] {
        direction: rtl;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1180px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title('محسّن السيرة الذاتية')
st.caption('تحليل ATS، مطابقة الوظائف، توليد خطابات التقديم، وتتبع طلبات التوظيف.')

analysis_tab, tracker_tab = st.tabs(['تحليل السيرة', 'متابعة التقديمات'])


def save_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def load_resume_text(uploaded_file):
    if uploaded_file is None:
        st.error('فضلاً ارفع ملف السيرة الذاتية.')
        return None

    path = save_uploaded_file(uploaded_file)
    return read_text(path)


def load_job_text(uploaded_file, url):
    if url:
        return fetch_job_description_from_url(url)

    if uploaded_file is None:
        st.error('فضلاً ارفع ملف الوصف الوظيفي أو أضف رابط إعلان الوظيفة.')
        return None

    path = save_uploaded_file(uploaded_file)
    return read_text(path)


with analysis_tab:
    with st.sidebar:
        st.header('المدخلات')
        resume_file = st.file_uploader('ارفع السيرة الذاتية', type=['txt', 'pdf', 'docx'])
        job_file = st.file_uploader('ارفع الوصف الوظيفي', type=['txt', 'pdf', 'docx'])
        job_url = st.text_input('أو أضف رابط إعلان الوظيفة')

        st.divider()
        st.header('خطاب التقديم')
        generate_letter = st.checkbox('توليد خطاب تقديم')
        company_name = st.text_input('اسم الشركة', value='الشركة')
        role_title = st.text_input('المسمى الوظيفي', value='الوظيفة')
        language = st.selectbox('لغة الخطاب', ['ar', 'en'], format_func=lambda x: 'العربية' if x == 'ar' else 'الإنجليزية')
        tone = st.selectbox('أسلوب الخطاب العربي', ['modern', 'formal', 'executive'], format_func=lambda x: {'modern': 'مهني حديث', 'formal': 'رسمي', 'executive': 'تنفيذي'}[x])

        run_button = st.button('تحليل السيرة', type='primary')

    if run_button:
        try:
            resume_text = load_resume_text(resume_file)
            job_text = load_job_text(job_file, job_url)

            if resume_text and job_text:
                results = analyze_ats(resume_text, job_text)
                report = build_report(results)
                score = results['ats_score']

                st.subheader('نتيجة ATS')
                st.metric('النتيجة الإجمالية', f'{score} / 100')

                st.subheader('تفصيل النتيجة')
                st.dataframe(
                    [
                        {'البند': CATEGORY_AR.get(key, key), 'الدرجة': value}
                        for key, value in results['component_scores'].items()
                    ],
                    use_container_width=True
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader('الكلمات المطابقة')
                    st.write('، '.join(results['matched_keywords']) or 'لا توجد كلمات مطابقة قوية.')

                    st.subheader('المهارات المطابقة')
                    st.write('، '.join(results['matched_skills']) or 'لا توجد مهارات مطابقة واضحة.')

                with col2:
                    st.subheader('الكلمات الناقصة')
                    st.write('، '.join(results['missing_keywords'][:25]) or 'لا توجد كلمات ناقصة مهمة.')

                    st.subheader('المهارات الناقصة')
                    st.write('، '.join(results['missing_skills']) or 'لا توجد مهارات ناقصة.')

                st.subheader('التوصيات')
                for suggestion in results['suggestions']:
                    st.write(f'- {suggestion}')

                st.download_button(
                    label='تحميل تقرير ATS',
                    data=report,
                    file_name='ats_resume_report.txt',
                    mime='text/plain'
                )

                if generate_letter:
                    if generate_cover_letter is None:
                        st.warning('وحدة توليد خطاب التقديم غير متاحة حالياً.')
                    else:
                        with st.spinner('جاري توليد خطاب التقديم...'):
                            letter = generate_cover_letter(
                                resume_text=resume_text,
                                job_description=job_text,
                                company_name=company_name,
                                role_title=role_title,
                                language=language,
                                tone=tone,
                            )

                        st.subheader('خطاب التقديم')
                        st.text_area('النص الناتج', letter, height=300)
                        st.download_button(
                            label='تحميل خطاب التقديم',
                            data=letter,
                            file_name='cover_letter_ar.txt' if language == 'ar' else 'cover_letter_en.txt',
                            mime='text/plain'
                        )

        except Exception as error:
            st.error(f'حدث خطأ: {error}')
    else:
        st.info('ارفع السيرة والوصف الوظيفي، أو أضف رابط إعلان الوظيفة، ثم اضغط تحليل السيرة.')


with tracker_tab:
    st.subheader('متابعة طلبات التوظيف')

    if add_application is None:
        st.warning('وحدة متابعة الطلبات غير متاحة حالياً.')
    else:
        with st.form('add_application_form'):
            col1, col2 = st.columns(2)

            with col1:
                company = st.text_input('الشركة')
                role = st.text_input('المسمى الوظيفي')
                job_link = st.text_input('رابط الوظيفة')
                status = st.selectbox('الحالة', STATUSES, index=0, format_func=lambda x: STATUS_AR.get(x, x))

            with col2:
                applied_date = st.date_input('تاريخ التقديم')
                deadline = st.text_input('آخر موعد')
                resume_version = st.text_input('نسخة السيرة')
                cover_letter_file = st.text_input('ملف خطاب التقديم')

            notes = st.text_area('ملاحظات')
            submitted = st.form_submit_button('إضافة الطلب')

            if submitted:
                if not company or not role:
                    st.error('اسم الشركة والمسمى الوظيفي مطلوبان.')
                else:
                    record = add_application(
                        company=company,
                        role=role,
                        job_url=job_link,
                        status=status,
                        applied_date=str(applied_date),
                        deadline=deadline,
                        resume_version=resume_version,
                        cover_letter_file=cover_letter_file,
                        notes=notes,
                    )
                    st.success(f"تمت إضافة الطلب: {record['application_id']}")

        applications = read_applications()

        if applications:
            df = pd.DataFrame(applications)
            display_df = df.rename(columns={
                'application_id': 'رقم الطلب',
                'company': 'الشركة',
                'role': 'المسمى',
                'job_url': 'رابط الوظيفة',
                'status': 'الحالة',
                'applied_date': 'تاريخ التقديم',
                'deadline': 'آخر موعد',
                'resume_version': 'نسخة السيرة',
                'cover_letter_file': 'خطاب التقديم',
                'notes': 'ملاحظات',
            })
            if 'الحالة' in display_df.columns:
                display_df['الحالة'] = display_df['الحالة'].map(lambda x: STATUS_AR.get(x, x))

            st.subheader('ملخص المسار')
            summary = summarize_pipeline()
            st.dataframe(
                [{'الحالة': STATUS_AR.get(status, status), 'العدد': count} for status, count in summary.items()],
                use_container_width=True
            )

            st.subheader('طلبات التقديم')
            st.dataframe(display_df, use_container_width=True)

            st.download_button(
                label='تحميل ملف الطلبات CSV',
                data=df.to_csv(index=False).encode('utf-8-sig'),
                file_name='applications.csv',
                mime='text/csv'
            )

            st.subheader('تحديث حالة الطلب')
            update_col1, update_col2 = st.columns(2)
            with update_col1:
                application_id = st.selectbox('رقم الطلب', df['application_id'].tolist())
            with update_col2:
                new_status = st.selectbox('الحالة الجديدة', STATUSES, index=0, key='new_status', format_func=lambda x: STATUS_AR.get(x, x))

            if st.button('تحديث الحالة'):
                update_application_status(application_id, new_status)
                st.success(f'تم تحديث {application_id} إلى {STATUS_AR.get(new_status, new_status)}. حدّث الصفحة لعرض التغيير.')
        else:
            st.info('لا توجد طلبات محفوظة حتى الآن.')
