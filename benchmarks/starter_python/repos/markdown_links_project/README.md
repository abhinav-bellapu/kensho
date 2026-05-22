# Markdown link parser benchmark

`extract_links(text)` returns all `[label](url)` markdown links as `(label, url)` tuples.

**Intentional bug:** uses `re.search`, so only the first link in a string is returned.
