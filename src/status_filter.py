"""Status code filter — controls which results appear in output."""


def _is_3xx(status: str) -> bool:
    return len(status) == 3 and status.startswith("3") and status.isdigit()


class StatusFilter:
    """Determines which HTTP status codes pass through to output."""

    def __init__(self, codes: frozenset, include_3xx_compat: bool) -> None:
        self._codes = codes
        self._include_3xx_compat = include_3xx_compat

    def matches(self, status: str) -> bool:
        return (
            status.startswith("ERROR:")
            or not self._codes
            or status in self._codes
            or (self._include_3xx_compat and _is_3xx(status))
        )

    def _tally_excluded(self, summary: dict, status: str) -> None:
        if self.matches(status):
            return
        summary[status] = summary.get(status, 0) + 1

    def excluded_summary(self, results: list) -> dict:
        summary: dict = {}
        for _, _, status in results:
            self._tally_excluded(summary, status)
        return summary


def build_filter(codes_raw: str, include_3xx_compat: bool = False) -> StatusFilter:
    if not codes_raw:
        return StatusFilter(frozenset(), include_3xx_compat)
    codes = frozenset(c.strip() for c in codes_raw.split(",") if c.strip())
    return StatusFilter(codes, include_3xx_compat)
