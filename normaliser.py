"""URL normalisation utilities."""

import urllib.parse


def normalise(url: str, base: str) -> str | None:
    """Resolve `url` relative to `base` and apply normalisation rules.

    Returns the normalised absolute URL string, or None if the URL must be
    filtered out (non-http/https scheme).
    """
    url = url.strip()
    resolved = urllib.parse.urljoin(base, url)
    parsed = urllib.parse.urlparse(resolved)

    if parsed.scheme not in ("http", "https"):
        return None

    normalised = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        "",  # strip fragment
    ))
    return normalised


def is_internal(url: str, base_url: str) -> bool:
    """Return True if `url` shares the same scheme and netloc as `base_url`."""
    parsed_url = urllib.parse.urlparse(url)
    parsed_base = urllib.parse.urlparse(base_url)
    return parsed_url.scheme == parsed_base.scheme and parsed_url.netloc == parsed_base.netloc
