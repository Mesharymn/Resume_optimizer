"""LLM-powered resume rewriting utilities.

This module rewrites resumes to better align with ATS systems and job descriptions.
Requires OPENAI_API_KEY in the environment.
"""

import os
from openai import OpenAI


client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def rewrite_resume_section(section_name, section_text, job_description, model='gpt-4o-mini'):
    prompt = f"""
You are an ATS resume optimization assistant.

Rewrite the following resume section to better align with the provided job description.

Rules:
- Keep the information truthful.
- Improve ATS keyword alignment.
- Use strong action verbs.
- Keep the writing professional.
- Preserve readability.
- Do not invent fake experience.
- Optimize for recruiter readability.

Section Name:
{section_name}

Original Resume Section:
{section_text}

Target Job Description:
{job_description}

Return ONLY the rewritten section text.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def rewrite_full_resume(resume_text, job_description, model='gpt-4o-mini'):
    prompt = f"""
You are an ATS resume optimization assistant.

Rewrite this resume to better align with the provided job description.

Rules:
- Keep all information truthful.
- Improve ATS compatibility.
- Add relevant keywords naturally.
- Improve bullet points.
- Use measurable language when possible.
- Keep formatting clean.
- Do not fabricate certifications, companies, or experience.
- Maintain a professional tone.

Resume:
{resume_text}

Job Description:
{job_description}

Return ONLY the rewritten resume.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
