"""Simple CSV-based job application tracker.

This module keeps application tracking lightweight and local.
It stores applications in data/applications.csv.
"""

import csv
from datetime import date
from pathlib import Path

TRACKER_FILE = Path('data/applications.csv')
TRACKER_FILE.parent.mkdir(exist_ok=True)

FIELDNAMES = [
    'application_id',
    'company',
    'role',
    'job_url',
    'status',
    'applied_date',
    'deadline',
    'resume_version',
    'cover_letter_file',
    'notes',
]

STATUSES = [
    'Saved',
    'Applied',
    'Screening',
    'Interview',
    'Offer',
    'Rejected',
    'Withdrawn',
]


def initialize_tracker():
    if not TRACKER_FILE.exists():
        with TRACKER_FILE.open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def read_applications():
    initialize_tracker()

    with TRACKER_FILE.open('r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)


def get_next_application_id(applications):
    if not applications:
        return 'APP-001'

    numbers = []
    for application in applications:
        raw_id = application.get('application_id', '')
        if raw_id.startswith('APP-'):
            try:
                numbers.append(int(raw_id.replace('APP-', '')))
            except ValueError:
                continue

    next_number = max(numbers, default=0) + 1
    return f'APP-{next_number:03d}'


def add_application(
    company,
    role,
    job_url='',
    status='Saved',
    applied_date=None,
    deadline='',
    resume_version='',
    cover_letter_file='',
    notes='',
):
    initialize_tracker()
    applications = read_applications()

    if status not in STATUSES:
        raise ValueError(f'Invalid status. Use one of: {", ".join(STATUSES)}')

    record = {
        'application_id': get_next_application_id(applications),
        'company': company,
        'role': role,
        'job_url': job_url,
        'status': status,
        'applied_date': applied_date or str(date.today()),
        'deadline': deadline,
        'resume_version': resume_version,
        'cover_letter_file': cover_letter_file,
        'notes': notes,
    }

    with TRACKER_FILE.open('a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(record)

    return record


def update_application_status(application_id, new_status):
    if new_status not in STATUSES:
        raise ValueError(f'Invalid status. Use one of: {", ".join(STATUSES)}')

    applications = read_applications()
    updated = False

    for application in applications:
        if application['application_id'] == application_id:
            application['status'] = new_status
            updated = True
            break

    if not updated:
        raise ValueError(f'Application not found: {application_id}')

    with TRACKER_FILE.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(applications)

    return application_id


def summarize_pipeline():
    applications = read_applications()
    summary = {status: 0 for status in STATUSES}

    for application in applications:
        status = application.get('status', 'Saved')
        if status in summary:
            summary[status] += 1

    return summary
