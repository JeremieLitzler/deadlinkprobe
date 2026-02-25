"""BFS crawl logic; produces link/referrer pairs."""

from collections import deque

from fetcher import fetch_html
from normaliser import is_internal, normalise
from web_parser import extract_links


def crawl(start_url: str, timeout: int, user_agent: str) -> list[tuple[str, str]]:
    """BFS crawl starting from `start_url`.

    Returns a list of (link, referrer) tuples for every discovered link.
    The start URL itself is included with referrer set to "" (empty string).
    Internal links are followed recursively; external links are collected but
    not crawled.
    """
    normalised_start = normalise(start_url, start_url)
    if normalised_start is None:
        return []

    queue: deque[str] = deque([normalised_start])
    visited: set[str] = {normalised_start}
    results: list[tuple[str, str]] = [(normalised_start, "")]
    print(f"DISCOVERED {normalised_start}")

    while queue:
        current_url = queue.popleft()
        html = fetch_html(current_url, timeout, user_agent)
        if html is None:
            continue

        raw_links = extract_links(html)
        for raw in raw_links:
            norm = normalise(raw, current_url)
            if norm is None:
                continue
            if norm in visited:
                continue
            visited.add(norm)
            results.append((norm, current_url))
            print(f"DISCOVERED {norm}")
            if is_internal(norm, start_url):
                queue.append(norm)

    return results
