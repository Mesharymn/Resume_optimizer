# Resume Optimizer

The idea behind the project is simple:

Most people apply to jobs with the same resume every time, even though different roles prioritize different keywords, skills, and experience.

This project helps bridge that gap by analyzing resumes, identifying missing skills and keywords, generating ATS-style feedback, rewriting sections with AI assistance, and creating tailored cover letters.

## Features

### ATS Resume Analysis

- ATS-style scoring system
- Keyword matching
- Hard skill detection
- Resume section analysis
- Contact information validation
- Action verb detection
- Measurable achievement checks
- Resume improvement suggestions

### File Support

The analyzer supports:

- TXT resumes
- PDF resumes
- DOCX resumes
- Live job posting URLs

### AI-Powered Resume Rewriting

The project includes optional LLM-based rewriting features using OpenAI.

It can:

- Rewrite professional summaries
- Improve experience bullet points
- Optimize resumes for ATS systems
- Align resumes with specific job descriptions
- Improve wording while keeping content truthful

### Cover Letter Generation

The repository also includes an AI-powered cover letter generator.

Supported languages:

- English
- Arabic

Arabic mode supports different writing tones including:

- formal
- modern
- executive

### Resume Templates

The repository contains multiple ATS-friendly templates for different career paths including:

- Data Analyst
- Software Engineer
- Project Manager
- Account Executive
- Cybersecurity Consultant
- Cloud Engineer
- Business Analyst
- Solutions Consultant
- Data Governance Specialist
- DevOps Engineer
- AI Engineer
- Product Manager
- UX/UI Designer
- Financial Analyst
- Scrum Master
- Compliance Officer
- Retail Store Manager
- and many more

## Project Structure

```text
Resume_optimizer/
├── cover_letters/
├── data/
├── reports/
├── src/
│   ├── main.py
│   ├── llm_rewriter.py
│   └── cover_letter_generator.py
├── templates/
├── requirements.txt
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

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running The Analyzer

Analyze local resume and job description files:

```bash
python src/main.py \
  --resume my_resume.pdf \
  --job job_description.docx
```

Analyze against a live job posting:

```bash
python src/main.py \
  --resume my_resume.docx \
  --job-url "https://company.com/careers/job-posting"
```

## OpenAI Setup

Some features use OpenAI models for rewriting and cover letter generation.

macOS/Linux:

```bash
export OPENAI_API_KEY=your_api_key
```

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key"
```

## Example Use Cases

- Improve ATS compatibility before applying to jobs
- Compare resumes against enterprise job postings
- Generate tailored cover letters
- Create role-specific resume versions
- Experiment with AI-assisted career tools
- Build resume variants for different industries

## Tech Stack

- Python
- OpenAI API
- scikit-learn
- pandas
- requests
- python-docx
- pypdf

## Notes

This project is intentionally built as a practical toolkit 
