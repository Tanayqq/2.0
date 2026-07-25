"""
Phase 4: PHI-Safe Logging & Security Filter.
Sanitizes patient names, MRNs, dates of birth, social security numbers, and phone numbers
before query text is logged to telemetry or audit trails.
"""
import re

PHI_PATTERNS = [
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]'),
    (r'\bMRN:?\s*\d{6,10}\b', '[MRN-REDACTED]'),
    (r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE-REDACTED]'),
    (r'\bDOB:?\s*\d{1,2}/\d{1,2}/\d{2,4}\b', '[DOB-REDACTED]'),
    (r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+\(Patient\)\b', '[PATIENT-NAME-REDACTED]')
]

class PHISanitizer:
    @staticmethod
    def sanitize_text(text: str) -> str:
        if not text:
            return ""

        sanitized = text
        for pattern, replacement in PHI_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized
