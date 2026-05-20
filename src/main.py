import argparse
import re
from collections import Counter
from pathlib import Path

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

ACTION_VERBS = {
    'built', 'created', 'developed', 'led', 'managed', 'improved', 'reduced',
    'increased', 'analyzed', 'implemented', 'automated', 'designed', 'delivered',
    'optimized', 'reported', 'launched', 'coordinated', 'trained'
}

HARD_SKILLS = {
    'python', 'pandas', 'sql', 'excel', 'powerbi', 'tableau', 'dashboard',
    'analytics', 'automation', 'api', 'fastapi', 'flask', 'git', 'github',
    'machine', 'learning', 'data', 'visualization', 'reporting', 'statistics'
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

    return path.read_text(encoding='utf-8')


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

    resume_skills = sorted(set(clean_text(resume_text)).intersection(HARD_SKILLS))
    job_skills = sorted(set(clean_text(job_text)).intersection(HARD_SKILLS))
    matched_skills = sorted(set(resume_skills).intersection(set(job_skills)))
    missing_skills = sorted(set(job_skills).difference(set(resume_skills)))

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
        'sections_found': sections_found,
        'missing_sections': sorted(set(COMMON_SECTIONS).difference(set(sections_found))),
        'contact_info': contact_info,
        'impact_numbers': impact_numbers,
        'action_verbs': action_verbs,
        'suggestions': generate_ats_suggestions(missing_keywords, missing_skills, sections_found, contact_info, impact_numbers, action_verbs),
    }


def generate_ats_suggestions(missing_keywords, missing_skills, sections_found, contact_info, impact_numbers, action_verbs):
    suggestions = []

    if missing_keywords:
        suggestions.append('Add relevant job-description keywords naturally into your experience and skills sections.')

    if missing_skills:
        suggestions.append(f"Highlight missing hard skills if accurate: {', '.join(missing_skills[:8])}.")

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

    lines.append('Resume Structure')
    lines.append('-' * 16)
    lines.append('Sections found: ' + (', '.join(results['sections_found']) or 'None detected'))
    lines.append('Missing sections: ' + (', '.join(results['missing_sections']) or 'None'))
    lines.append('')

    lines.append('Contact Info Check')
    lines.append('-' * 18)
    for item, found in results['contact_info'].items():
        lines.append(f"{item.title()}: {'Found' if found else 'Missing'}")
    lines.append('')

    lines.append('Measurable Impact')
    lines.append('-' * 17)
    lines.append(', '.join(results['impact_numbers']) or 'No measurable achievements detected.')
    lines.append('')

    lines.append('Action Verbs Found')
    lines.append('-' * 18)
    lines.append(', '.join(results['action_verbs']) or 'No strong action verbs detected.')
    lines.append('')

    lines.append('Suggestions')
    lines.append('-' * 11)
    for suggestion in results['suggestions']:
        lines.append(f'- {suggestion}')

    lines.append('')
    lines.append('Note: This is an ATS-style scoring model for resume review. It is not a hiring decision system.')

    return '\n'.join(lines)


def save_report(report):
    output_path = REPORTS_DIR / 'ats_resume_report.txt'
    output_path.write_text(report, encoding='utf-8')
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(description='Run an ATS-style resume analysis against a job description.')
    parser.add_argument('--resume', default=DEFAULT_RESUME, help='Path to resume text file.')
    parser.add_argument('--job', default=DEFAULT_JOB, help='Path to job description text file.')
    return parser.parse_args()


def main():
    args = parse_args()

    resume_text = read_text(args.resume)
    job_text = read_text(args.job)

    results = analyze_ats(resume_text, job_text)
    report = build_report(results)

    print(report)

    output_path = save_report(report)
    print(f'\nReport saved to: {output_path}')


if __name__ == '__main__':
    main()
