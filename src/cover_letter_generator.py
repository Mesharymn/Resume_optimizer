"""LLM-powered cover letter generation.

Requires OPENAI_API_KEY in the environment.
The generator uses a resume and job description to create a tailored cover letter.
Supports English and Arabic outputs.
"""

import os
from pathlib import Path

from openai import OpenAI

OUTPUT_DIR = Path('cover_letters')
OUTPUT_DIR.mkdir(exist_ok=True)

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'ar': 'Arabic',
}

ARABIC_TONES = {
    'formal': 'استخدم أسلوبًا عربيًا رسميًا مناسبًا للجهات الحكومية والشركات الكبرى.',
    'modern': 'استخدم أسلوبًا عربيًا مهنيًا حديثًا وواضحًا بدون مبالغة.',
    'executive': 'استخدم أسلوبًا عربيًا تنفيذيًا واثقًا يركز على الأثر والنتائج.',
}


def get_client():
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise EnvironmentError('Missing OPENAI_API_KEY environment variable.')

    return OpenAI(api_key=api_key)


def generate_cover_letter(
    resume_text,
    job_description,
    company_name='the company',
    role_title='the role',
    language='en',
    tone='modern',
    model='gpt-4o-mini'
):
    client = get_client()
    language_name = SUPPORTED_LANGUAGES.get(language, 'English')

    if language == 'ar':
        tone_instruction = ARABIC_TONES.get(tone, ARABIC_TONES['modern'])
        prompt = f"""
أنت مساعد محترف في كتابة الخطابات الوظيفية.

اكتب خطاب تقديم باللغة العربية بناءً على السيرة الذاتية والوصف الوظيفي أدناه.

التعليمات:
- اجعل الخطاب صادقًا ومبنيًا فقط على معلومات السيرة الذاتية.
- لا تخترع شركات أو شهادات أو خبرات أو إنجازات غير موجودة.
- اجعل الخطاب مناسبًا لأنظمة ATS وسهل القراءة لمسؤول التوظيف.
- استخدم لغة عربية مهنية وواضحة.
- {tone_instruction}
- اجعل الخطاب من 3 إلى 5 فقرات فقط.
- اذكر اسم الشركة والمسمى الوظيفي بشكل طبيعي.
- ركّز على الملاءمة، المهارات، والأثر العملي.
- لا تضع حقولًا وهمية أو placeholders إلا إذا كانت المعلومات ناقصة فعلًا.

الشركة:
{company_name}

المسمى الوظيفي:
{role_title}

السيرة الذاتية:
{resume_text}

الوصف الوظيفي:
{job_description}

أعد نص خطاب التقديم فقط.
"""
    else:
        prompt = f"""
You are a professional career writing assistant.

Write a tailored cover letter in {language_name} using the resume and job description below.

Rules:
- Keep it truthful and based only on the resume.
- Do not invent companies, degrees, certifications, or achievements.
- Make it ATS-friendly and recruiter-friendly.
- Use a confident but natural tone.
- Keep it concise: 3 to 5 paragraphs.
- Mention the company and role naturally.
- Focus on fit, impact, and relevant skills.
- Do not include placeholders unless information is missing.

Company:
{company_name}

Role:
{role_title}

Resume:
{resume_text}

Job Description:
{job_description}

Return ONLY the cover letter text.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


def save_cover_letter(content, output_file=None, language='en'):
    if output_file is None:
        output_file = 'cover_letters/cover_letter_ar.txt' if language == 'ar' else 'cover_letters/cover_letter_en.txt'

    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(content, encoding='utf-8')
    return output_path
