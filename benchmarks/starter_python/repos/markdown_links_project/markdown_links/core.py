"""Extract markdown links from text."""

import re

# Bug: search() returns only the first link in the string
_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def extract_links(text: str) -> list[tuple[str, str]]:
    """Return (label, url) pairs for markdown links like [text](url)."""
    match = _LINK_PATTERN.search(text)
    if not match:
        return []
    return [(match.group(1), match.group(2))]
