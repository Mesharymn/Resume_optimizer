# Resume Optimizer

A simple Python tool for comparing a resume against a job description.

The project gives a first-pass analysis of how well a resume matches a role by checking relevant keywords, missing terms, and basic improvement suggestions.

## What it does

- Reads a resume text file
- Reads a job description text file
- Extracts important keywords
- Calculates a match score
- Shows matched and missing keywords
- Generates improvement suggestions
- Exports a text report

## Project structure

```text
Resume_optimizer/
├── data/
│   ├── sample_resume.txt
│   └── sample_job_description.txt
├── reports/
├── src/
│   └── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

```bash
git clone https://github.com/Mesharymn/Resume_optimizer.git
cd Resume_optimizer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run with sample files:

```bash
python src/main.py
```

Run with your own files:

```bash
python src/main.py --resume data/my_resume.txt --job data/job_description.txt
```

## Output

The report is saved to:

```text
reports/resume_analysis_report.txt
```

## Current limitations

- This is keyword-based, not a full ATS engine
- It works best with plain text files
- It does not make hiring decisions
- Suggestions should be reviewed manually before editing a resume

## Tech stack

- Python
- scikit-learn
- pandas
