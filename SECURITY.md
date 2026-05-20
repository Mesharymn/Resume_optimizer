# Security Notes

## Overview

Resume Optimizer processes resumes, job descriptions, uploaded documents, and external job links.

The project includes basic protections to reduce common risks when handling user-controlled input.

## Current Security Controls

### File Upload Validation

The application validates:

- allowed file extensions
- upload size limits
- unsafe file names
- path traversal attempts

Supported file types:

- TXT
- PDF
- DOCX

Maximum upload size:

- 10 MB

---

### URL Validation

External job posting URLs are validated before fetching.

Blocked targets include:

- localhost
- loopback addresses
- private IP ranges
- link-local addresses
- reserved/internal addresses

This helps reduce SSRF-style abuse.

---

### Secret Handling

The project uses environment variables for API keys.

Example:

```bash
export OPENAI_API_KEY=your_key
```

Secrets should never be:

- hardcoded
- committed to GitHub
- stored in plaintext config files

---

### Text Sanitization

User-controlled text is sanitized before reports are generated.

This helps reduce:

- malformed output
- control character injection
- oversized payloads

---

### Dependencies

Recommended:

```bash
pip install safety pip-audit
```

Run:

```bash
pip-audit
safety check
```

---

## Deployment Recommendations

For production deployments:

- place the app behind a reverse proxy
- enable HTTPS
- add rate limiting
- isolate uploads in dedicated storage
- avoid running as root
- enable logging and monitoring
- use a WAF if exposed publicly
- add authentication before enabling multi-user access

---

## AI Safety Considerations

LLM-based rewriting features should not:

- invent fake experience
- fabricate certifications
- generate misleading claims

Prompts in this repository attempt to keep generated output truthful.
