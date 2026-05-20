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
    'work', 'using', 'strong', 'support'
}

STOP_WORDS = set(ENGLISH_STOP_WORDS).union(EXTRA_STOP_WORDS)


def read_text(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')

    return path.read_text(encoding='utf-8')


def clean_text(text):
    text = text.lower()
    words = re.findall(r'[a-zA-Z][a-zA-Z+#.]*', text)
    return [word for word in words if word not in STOP_WORDS and len(word) > 2]


def extract_keywords(text, limit=30):
    words = clean_text(text)
    counts = Counter(words)
    return [word for word, _ in counts.most_common(limit)]


def calculate_match_score(resume_keywords, job_keywords):
    if not job_keywords:
        return 0

    matched = set(resume_keywords).intersection(set(job_keywords))
    score = (len(matched) / len(set(job_keywords))) * 100

    return round(score, 1)


def generate_suggestions(missing_keywords):
    suggestions = []

    if not missing_keywords:
        return ['The resume already covers most of the important keywords.']

    suggestions.append('Add role-specific keywords where they are accurate and relevant.')
    suggestions.append('Rewrite experience bullets to better reflect the job description language.')
    suggestions.append('Use measurable achievements instead of generic tasks.')

    top_missing = ', '.join(missing_keywords[:8])
    suggestions.append(f'Consider naturally adding: {top_missing}')

    return suggestions


def analyze_resume(resume_text, job_text):
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_text)

    matched_keywords = sorted(set(resume_keywords).intersection(set(job_keywords)))
    missing_keywords = sorted(set(job_keywords).difference(set(resume_keywords)))

    score = calculate_match_score(resume_keywords, job_keywords)
    suggestions = generate_suggestions(missing_keywords)

    return {
        'score': score,
        'matched_keywords': matched_keywords,
        'missing_keywords': missing_keywords,
        'suggestions': suggestions,
    }


def build_report(results):
    lines = []

    lines.append('Resume Analysis Report')
    lines.append('=' * 24)
    lines.append('')
    lines.append(f"Match Score: {results['score']}%")
    lines.append('')

    lines.append('Matched Keywords')
    lines.append('-' * 16)
    lines.append(', '.join(results['matched_keywords']) or 'No strong matches found.')
    lines.append('')

    lines.append('Missing Keywords')
    lines.append('-' * 16)
    lines.append(', '.join(results['missing_keywords']) or 'No major missing keywords found.')
    lines.append('')

    lines.append('Suggestions')
    lines.append('-' * 11)

    for suggestion in results['suggestions']:
        lines.append(f'- {suggestion}')

    lines.append('')
    lines.append('Note: This is a keyword-based analysis tool, not a hiring decision system.')

    return '\n'.join(lines)


def save_report(report):
    output_path = REPORTS_DIR / 'resume_analysis_report.txt'
    output_path.write_text(report, encoding='utf-8')
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(description='Compare a resume against a job description.')
    parser.add_argument('--resume', default=DEFAULT_RESUME, help='Path to resume text file.')
    parser.add_argument('--job', default=DEFAULT_JOB, help='Path to job description text file.')
    return parser.parse_args()


def main():
    args = parse_args()

    resume_text = read_text(args.resume)
    job_text = read_text(args.job)

    results = analyze_resume(resume_text, job_text)
    report = build_report(results)

    print(report)

    output_path = save_report(report)
    print(f'\nReport saved to: {output_path}')


if __name__ == '__main__':
    main()
