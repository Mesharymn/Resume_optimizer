"""LLM-powered cover letter generation.

Requires OPENAI_API_KEY in the environment.
The generator uses a resume and job description to create a tailored cover letter.
"""

import os
from pathlib import Path

from openai import OpenAI

OUTPUT_DIR = Path('cover_letters')
OUTPUT_DIR.mkdir(exist_ok=True)


def get_client():
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise EnvironmentError('Missing OPENAI_API_KEY environment variable.')

    return OpenAI(api_key=api_key)


def generate_cover_letter(resume_text, job_description, company_name='the company', role_title='the role', model='gpt-4o-mini'):
    client = get_client()

    prompt = f"""
You are a professional career writing assistant.

Write a tailored cover letter using the resume and job description below.

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


def save_cover_letter(content, output_file='cover_letters/cover_letter.txt'):
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(content, encoding='utf-8')
    return output_path
