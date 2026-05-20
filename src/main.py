import argparse
import re
from collections import Counter
from pathlib import Path

import requests
from docx import Document
from pypdf import PdfReader
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

DEFAULT_RESUME = 'data/sample_resume.txt'
DEFAULT_JOB = 'data/sample_job_description.txt'
REPORTS_DIR = Path('reports')
REPORTS_DIR.mkdir(exist_ok=True)

EXTRA_STOP_WORDS = {
    'experience', 'responsibilities', 'requirements', 'skills',
    'work', 'using', 'strong', 'support', 'looking', 'candidate'
}

STOP_WORDS = set(ENGLISH_STOP_WORDS).union(EXTRA_STOP_WORDS)

COMMON_SECTIONS = [
    'summary', 'experience', 'education', 'skills', 'projects',
    'certifications', 'achievements'
]

SECTION_HEADERS = {
    'education': ['education', 'academic background', 'degree', 'university', 'college'],
    'certifications': ['certifications', 'certification', 'licenses', 'credentials', 'courses'],
}

ACTION_VERBS = {
    'built', 'created', 'developed', 'led', 'managed', 'improved', 'reduced',
    'increased', 'analyzed', 'implemented', 'automated', 'designed', 'delivered',
    'optimized', 'reported', 'launched', 'coordinated', 'trained'
}

HARD_SKILLS = {
    'python', 'pandas', 'sql', 'excel', 'powerbi', 'tableau', 'dashboard',
    'analytics', 'automation', 'api', 'fastapi', 'flask', 'git', 'github',
    'machine', 'learning', 'data', 'visualization', 'reporting', 'statistics',
    'risk', 'governance', 'compliance', 'cybersecurity', 'cloud', 'azure', 'aws',
    'project', 'management', 'agile', 'scrum', 'salesforce', 'sap', 'erp'
}

CERTIFICATION_SKILL_MAP = {
    'pmp': ['project management', 'stakeholder management', 'risk management', 'planning'],
    'capm': ['project management', 'project coordination', 'planning'],
    'scrum': ['agile', 'scrum', 'sprint planning', 'team facilitation'],
    'csm': ['agile', 'scrum', 'team facilitation'],
    'psm': ['agile', 'scrum', 'team facilitation'],
    'lean six sigma': ['process improvement', 'root cause analysis', 'quality improvement', 'dmaic'],
    'six sigma': ['process improvement', 'quality improvement', 'dmaic'],
    'black belt': ['process improvement', 'quality improvement', 'data-driven improvement'],
    'green belt': ['process improvement', 'quality improvement'],
    'cissp': ['cybersecurity', 'security governance', 'risk management', 'security architecture'],
    'cism': ['information security management', 'security governance', 'risk management'],
    'crisc': ['it risk management', 'governance', 'risk assessment'],
    'security+': ['cybersecurity', 'network security', 'incident response'],
    'ceh': ['ethical hacking', 'penetration testing', 'vulnerability assessment'],
    'oscp': ['penetration testing', 'exploit development', 'security testing'],
    'iso 27001': ['information security', 'compliance', 'security controls', 'audit'],
    'aws': ['cloud computing', 'aws', 'cloud architecture', 'infrastructure'],
    'azure': ['cloud computing', 'azure', 'cloud administration', 'identity management'],
    'google cloud': ['cloud computing', 'gcp', 'cloud architecture'],
    'ccna': ['networking', 'routing', 'switching', 'network troubleshooting'],
    'ccnp': ['advanced networking', 'routing', 'switching', 'network design'],
    'cdmp': ['data governance', 'data management', 'metadata management', 'data quality'],
    'dama': ['data governance', 'data management', 'data quality'],
    'dcam': ['data governance', 'data controls', 'data management'],
    'grcp': ['governance', 'risk management', 'compliance'],
    'salesforce': ['crm', 'salesforce administration', 'workflow automation', 'reporting'],
    'sap': ['erp', 'sap', 'business process management', 'enterprise systems'],
    'cfa': ['financial analysis', 'financial modeling', 'investment analysis'],
    'cpa': ['accounting', 'financial reporting', 'audit'],
    'power bi': ['dashboarding', 'data visualization', 'business intelligence'],
    'tableau': ['data visualization', 'dashboarding', 'business intelligence'],
    'google data analytics': ['data analysis', 'spreadsheet analysis', 'sql', 'dashboarding'],
}

EDUCATION_SKILL_MAP = {
    'computer science': ['programming', 'software development', 'algorithms', 'data structures'],
    'information systems': ['business systems', 'data analysis', 'systems analysis'],
    'information technology': ['it support', 'networking', 'systems administration'],
    'cybersecurity': ['cybersecurity', 'risk assessment', 'security controls'],
    'data science': ['machine learning', 'statistics', 'python', 'data analysis'],
    'statistics': ['statistics', 'data analysis', 'probability'],
    'business administration': ['business analysis', 'operations management', 'strategy'],
    'management information systems': ['systems analysis', 'data analysis', 'business technology'],
    'finance': ['financial analysis', 'budgeting', 'forecasting'],
    'accounting': ['accounting', 'financial reporting', 'audit'],
    'marketing': ['market research', 'digital marketing', 'campaign analysis'],
    'industrial engineering': ['process improvement', 'operations research', 'quality management'],
    'engineering': ['problem solving', 'technical analysis', 'project coordination'],
}

WEIGHTS = {
    'keyword_match': 35,
    'hard_skills': 25,
    'required_sections': 15,
    'contact_info': 10,
    'measurable_impact': 10,
    'action_verbs': 5,
}


def read_text(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')

    suffix = path.suffix.lower()

    if suffix == '.txt':
        return path.read_text(encoding='utf-8')

    if suffix == '.pdf':
        return read_pdf(path)

    if suffix == '.docx':
        return read_docx(path)

    raise ValueError('Unsupported file type. Use .txt, .pdf, or .docx files.')


def read_pdf(path):
    reader = PdfReader(str(path))
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or '')

    text = '\n'.join(pages).strip()

    if not text:
        raise ValueError('No readable text found in PDF. Scanned PDFs need OCR before analysis.')

    return text


def read_docx(path):
    document = Document(str(path))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    text = '\n'.join(paragraphs).strip()

    if not text:
        raise ValueError('No readable text found in DOCX file.')

    return text


def fetch_job_description_from_url(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    html = response.text

    text = re.sub(r'<script.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style.*?</style>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def clean_text(text):
    text = text.lower()
    words = re.findall(r'[a-zA-Z][a-zA-Z+#.]*', text)
    return [word for word in words if word not in STOP_WORDS and len(word) > 2]


def extract_keywords(text, limit=40):
    words = clean_text(text)
    counts = Counter(words)
    return [word for word, _ in counts.most_common(limit)]


def score_ratio(matched_items, target_items):
    if not target_items:
        return 0

    return len(set(matched_items)) / len(set(target_items))


def extract_section_text(text, section_name):
    lines = text.splitlines()
    headers = SECTION_HEADERS.get(section_name, [])
    collected = []
    collecting = False

    all_possible_headers = set(COMMON_SECTIONS + ['courses', 'licenses', 'credentials'])

    for line in lines:
        cleaned = line.strip()
        lowered = cleaned.lower()

        if any(header in lowered for header in headers):
            collecting = True
            continue

        if collecting and lowered in all_possible_headers:
            break

        if collecting:
            collected.append(cleaned)

    return '\n'.join(collected).strip()


def infer_skills_from_text(text, skill_map):
    lowered = text.lower()
    inferred = []

    for trigger, skills in skill_map.items():
        if trigger in lowered:
            inferred.extend(skills)

    return sorted(set(inferred))


def infer_skills_from_education_and_certifications(resume_text):
    education_text = extract_section_text(resume_text, 'education')
    certification_text = extract_section_text(resume_text, 'certifications')

    if not education_text:
        education_text = resume_text
    if not certification_text:
        certification_text = resume_text

    education_skills = infer_skills_from_text(education_text, EDUCATION_SKILL_MAP)
    certification_skills = infer_skills_from_text(certification_text, CERTIFICATION_SKILL_MAP)

    return {
        'education_skills': education_skills,
        'certification_skills': certification_skills,
        'all_inferred_skills': sorted(set(education_skills + certification_skills)),
    }


def find_contact_info(text):
    email_found = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    phone_found = bool(re.search(r'(\+?\d[\d\s\-()]{7,}\d)', text))
    linkedin_found = 'linkedin.com' in text.lower() or 'linkedin' in text.lower()
    github_found = 'github.com' in text.lower() or 'github' in text.lower()

    found = {
        'email': email_found,
        'phone': phone_found,
        'linkedin': linkedin_found,
        'github': github_found,
    }

    score = sum(found.values()) / len(found)
    return score, found


def find_sections(text):
    lower_text = text.lower()
    found_sections = [section for section in COMMON_SECTIONS if section in lower_text]
    return found_sections


def find_measurable_impact(text):
    numbers = re.findall(r'\b\d+%?|\$\d+|\d+x\b', text.lower())
    return numbers


def find_action_verbs(text):
    words = set(clean_text(text))
    return sorted(words.intersection(ACTION_VERBS))


def analyze_ats(resume_text, job_text):
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_text)

    matched_keywords = sorted(set(resume_keywords).intersection(set(job_keywords)))
    missing_keywords = sorted(set(job_keywords).difference(set(resume_keywords)))

    inferred_skills = infer_skills_from_education_and_certifications(resume_text)
    inferred_skill_tokens = set(clean_text(' '.join(inferred_skills['all_inferred_skills'])))

    resume_skill_tokens = set(clean_text(resume_text)).intersection(HARD_SKILLS)
    resume_skill_tokens = resume_skill_tokens.union(inferred_skill_tokens.intersection(HARD_SKILLS))

    job_skills = sorted(set(clean_text(job_text)).intersection(HARD_SKILLS))
    matched_skills = sorted(resume_skill_tokens.intersection(set(job_skills)))
    missing_skills = sorted(set(job_skills).difference(resume_skill_tokens))

    sections_found = find_sections(resume_text)
    contact_score, contact_info = find_contact_info(resume_text)
    impact_numbers = find_measurable_impact(resume_text)
    action_verbs = find_action_verbs(resume_text)

    component_scores = {
        'keyword_match': round(score_ratio(matched_keywords, job_keywords) * WEIGHTS['keyword_match'], 1),
        'hard_skills': round(score_ratio(matched_skills, job_skills) * WEIGHTS['hard_skills'], 1),
        'required_sections': round(score_ratio(sections_found, COMMON_SECTIONS) * WEIGHTS['required_sections'], 1),
        'contact_info': round(contact_score * WEIGHTS['contact_info'], 1),
        'measurable_impact': WEIGHTS['measurable_impact'] if impact_numbers else 0,
        'action_verbs': round(min(len(action_verbs) / 8, 1) * WEIGHTS['action_verbs'], 1),
    }

    ats_score = round(sum(component_scores.values()), 1)

    return {
        'ats_score': ats_score,
        'component_scores': component_scores,
        'matched_keywords': matched_keywords,
        'missing_keywords': missing_keywords,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'education_skills': inferred_skills['education_skills'],
        'certification_skills': inferred_skills['certification_skills'],
        'inferred_skills': inferred_skills['all_inferred_skills'],
        'sections_found': sections_found,
        'missing_sections': sorted(set(COMMON_SECTIONS).difference(set(sections_found))),
        'contact_info': contact_info,
        'impact_numbers': impact_numbers,
        'action_verbs': action_verbs,
        'suggestions': generate_ats_suggestions(missing_keywords, missing_skills, sections_found, contact_info, impact_numbers, action_verbs, inferred_skills['all_inferred_skills']),
    }


def generate_ats_suggestions(missing_keywords, missing_skills, sections_found, contact_info, impact_numbers, action_verbs, inferred_skills=None):
    suggestions = []
    inferred_skills = inferred_skills or []

    if missing_keywords:
        suggestions.append('Add relevant job-description keywords naturally into your experience and skills sections.')

    if missing_skills:
        suggestions.append(f"Highlight missing hard skills if accurate: {', '.join(missing_skills[:8])}.")

    if inferred_skills:
        suggestions.append('Move inferred skills from education/certifications into the dedicated skills section for better ATS visibility.')

    if 'summary' not in sections_found:
        suggestions.append('Add a short professional summary tailored to the target role.')

    if 'skills' not in sections_found:
        suggestions.append('Add a dedicated skills section for ATS readability.')

    if not all(contact_info.values()):
        suggestions.append('Include complete contact information: email, phone, LinkedIn, and GitHub if available.')

    if not impact_numbers:
        suggestions.append('Add measurable achievements such as percentages, revenue impact, time saved, or volume handled.')

    if len(action_verbs) < 5:
        suggestions.append('Start more bullet points with action verbs such as built, improved, automated, analyzed, or led.')

    if not suggestions:
        suggestions.append('Resume is well aligned with this job description. Review wording and formatting manually before applying.')

    return suggestions


def build_report(results):
    lines = []

    lines.append('ATS Resume Analysis Report')
    lines.append('=' * 26)
    lines.append('')
    lines.append(f"ATS Score: {results['ats_score']} / 100")
    lines.append('')

    lines.append('Score Breakdown')
    lines.append('-' * 15)
    for category, score in results['component_scores'].items():
        lines.append(f"{category.replace('_', ' ').title()}: {score}")
    lines.append('')

    lines.append('Matched Keywords')
    lines.append('-' * 16)
    lines.append(', '.join(results['matched_keywords']) or 'No strong matches found.')
    lines.append('')

    lines.append('Missing Keywords')
    lines.append('-' * 16)
    lines.append(', '.join(results['missing_keywords'][:20]) or 'No major missing keywords found.')
    lines.append('')

    lines.append('Matched Hard Skills')
    lines.append('-' * 19)
    lines.append(', '.join(results['matched_skills']) or 'No matched hard skills found.')
    lines.append('')

    lines.append('Missing Hard Skills')
    lines.append('-' * 19)
    lines.append(', '.join(results['missing_skills']) or 'No missing hard skills found.')
    lines.append('')

    lines.append('Inferred Skills From Education')
    lines.append('-' * 30)
    lines.append(', '.join(results.get('education_skills', [])) or 'No education-based skills inferred.')
    lines.append('')

    lines.append('Inferred Skills From Certifications')
    lines.append('-' * 36)
    lines.append(', '.join(results.get('certification_skills', [])) or 'No certification-based skills inferred.')
    lines.append('')

    lines.append('Suggestions')
    lines.append('-' * 11)
    for suggestion in results['suggestions']:
        lines.append(f'- {suggestion}')

    return '\n'.join(lines)


def save_report(report):
    output_path = REPORTS_DIR / 'ats_resume_report.txt'
    output_path.write_text(report, encoding='utf-8')
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(description='Run an ATS-style resume analysis against a job description.')
    parser.add_argument('--resume', default=DEFAULT_RESUME, help='Path to resume file. Supports .txt, .pdf, and .docx.')
    parser.add_argument('--job', default=DEFAULT_JOB, help='Path to job description file. Supports .txt, .pdf, and .docx.')
    parser.add_argument('--job-url', help='Fetch job description directly from a webpage URL.')
    return parser.parse_args()


def main():
    args = parse_args()

    resume_text = read_text(args.resume)

    if args.job_url:
        print('Fetching job description from URL...')
        job_text = fetch_job_description_from_url(args.job_url)
    else:
        job_text = read_text(args.job)

    results = analyze_ats(resume_text, job_text)
    report = build_report(results)

    print(report)

    output_path = save_report(report)
    print(f'\nReport saved to: {output_path}')


if __name__ == '__main__':
    main()
