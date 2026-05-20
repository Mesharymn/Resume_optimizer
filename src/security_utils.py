"""Security helpers for Resume Optimizer.

The app handles user-uploaded resumes, job URLs, and optional API keys.
These helpers keep the checks in one place so the GUI and CLI stay cleaner.
"""

from __future__ import annotations

import ipaddress
import re
import socket
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_FILE_EXTENSIONS = {'.txt', '.pdf', '.docx'}
MAX_UPLOAD_SIZE_MB = 10
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

BLOCKED_HOSTS = {'localhost', '127.0.0.1', '0.0.0.0'}


def validate_uploaded_file_name(filename: str) -> None:
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_FILE_EXTENSIONS:
        raise ValueError(f'Unsupported file type: {suffix}. Allowed: .txt, .pdf, .docx')

    if '..' in filename or '/' in filename or '\\' in filename:
        raise ValueError('Unsafe file name detected.')


def validate_uploaded_file_size(size_bytes: int) -> None:
    if size_bytes > MAX_UPLOAD_SIZE_BYTES:
        raise ValueError(f'File is too large. Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB.')


def validate_job_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme not in {'http', 'https'}:
        raise ValueError('Only http and https URLs are allowed.')

    hostname = parsed.hostname

    if not hostname:
        raise ValueError('Invalid URL hostname.')

    if hostname.lower() in BLOCKED_HOSTS:
        raise ValueError('Localhost URLs are not allowed.')

    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise ValueError('Private or internal IP URLs are not allowed.')
    except ValueError:
        # Hostname is not a raw IP. Resolve it and check resulting addresses.
        try:
            resolved_addresses = socket.getaddrinfo(hostname, None)
            for item in resolved_addresses:
                resolved_ip = ipaddress.ip_address(item[4][0])
                if resolved_ip.is_private or resolved_ip.is_loopback or resolved_ip.is_link_local or resolved_ip.is_reserved:
                    raise ValueError('Resolved URL points to a private or internal address.')
        except socket.gaierror:
            raise ValueError('Could not resolve URL hostname.')


def sanitize_text_for_report(text: str, max_length: int = 20000) -> str:
    text = text or ''
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', text)
    return text[:max_length]


def mask_secret(value: str | None) -> str:
    if not value:
        return ''

    if len(value) <= 8:
        return '*' * len(value)

    return f'{value[:4]}...{value[-4:]}'
