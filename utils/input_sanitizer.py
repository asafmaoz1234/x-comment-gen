# input_sanitizer.py
import re
import html
from typing import Optional


class ContentSanitizer:
    @staticmethod
    def sanitize_text(text: Optional[str]) -> str:
        if not text:
            return ""

        # Remove potential XSS
        text = html.escape(text)

        # Remove potential command injection
        text = re.sub(r'[;&|`]', '', text)

        # Remove potential SQL injection patterns
        text = re.sub(r'[\[\]\'\"\\]', '', text)

        return text.strip()