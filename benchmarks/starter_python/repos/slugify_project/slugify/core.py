"""Convert text to URL-friendly slugs."""


def slugify(text: str) -> str:
    """Return a lowercase slug with spaces replaced by hyphens.

    Intentionally buggy: strips non-ASCII characters instead of transliterating.
    """
    lowered = text.lower().strip()
    ascii_only = lowered.encode("ascii", errors="ignore").decode("ascii")
    return "-".join(ascii_only.split())
