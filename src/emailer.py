"""Email notification via the Resend API."""

import html
import os
import sys

import resend

_RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
_RESEND_FROM_ADDRESS = os.environ.get("RESEND_FROM_ADDRESS")


def _is_3xx(status: str) -> bool:
    return len(status) == 3 and status.startswith("3") and status.isdigit()


def _build_email_rows(results: list) -> str:
    rows = []
    for link, referrer, status in results:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(link),
                html.escape(referrer),
                html.escape(status),
            )
        )
    return "\n".join(rows)


def _build_table_html(results: list) -> str:
    return (
        "<table>"
        "<thead><tr><th>Link</th><th>Referrer</th><th>Status</th></tr></thead>"
        "<tbody>{}</tbody>"
        "</table>".format(_build_email_rows(results))
    )


def _format_excluded_item(code: str, count: int) -> str:
    return "<li>{}: {}</li>".format(html.escape(code), count)


def _build_excluded_summary_html(excluded_summary: dict) -> str:
    if not excluded_summary:
        return ""
    items = "".join(
        _format_excluded_item(code, count)
        for code, count in sorted(excluded_summary.items())
    )
    return "<p>Excluded status codes (not in filter):</p><ul>{}</ul>".format(items)


def _build_email_summary_lines(
    website: str,
    timestamp: str,
    total_links: int,
    filtered_count: int,
) -> list:
    return [
        "<p>Website: <strong>{}</strong></p>".format(html.escape(website)),
        "<p>Scan timestamp: {}</p>".format(html.escape(timestamp)),
        "<p>Total links checked: {}</p>".format(total_links),
        "<p>Results matching filter: {}</p>".format(filtered_count),
    ]


def _build_email_html(
    website: str,
    timestamp: str,
    total_links: int,
    filtered_results: list,
    excluded_summary: dict,
) -> str:
    lines = _build_email_summary_lines(website, timestamp, total_links, len(filtered_results))
    excluded_html = _build_excluded_summary_html(excluded_summary)
    if excluded_html:
        lines.append(excluded_html)
    if filtered_results:
        lines.append(_build_table_html(filtered_results))
    return "\n".join(lines)


def _send_via_resend(
    notify_email: str,
    from_address: str,
    subject: str,
    body: str,
) -> None:
    params: resend.Emails.SendParams = {
        "from": from_address,
        "to": [notify_email],
        "subject": subject,
        "html": body,
    }
    try:
        resend.Emails.send(params)
        print("Notification sent.")
    except Exception as error:
        print(
            "Warning: notification failed: {}.".format(error),
            file=sys.stderr,
        )


def send_email_notification(
    filtered_results: list,
    excluded_summary: dict,
    website: str,
    timestamp: str,
    total_links: int,
    notify_email: str,
) -> None:
    """Send an email notification with scan results via the Resend API.

    Parameters
    ----------
    filtered_results:
        Pre-filtered list of (link, referrer, http_status_code) tuples to show in the table.
    excluded_summary:
        Mapping of status_code -> count for results excluded by the filter.
    website:
        The netloc of the scanned URL (used in subject and body).
    timestamp:
        The scan timestamp string (e.g. "2026-02-24T14-05-32").
    total_links:
        Total number of links checked (unfiltered count).
    notify_email:
        Recipient email address.
    """
    if _RESEND_API_KEY is None:
        print("Warning: RESEND_API_KEY is not set; notification skipped.", file=sys.stderr)
        return
    if _RESEND_FROM_ADDRESS is None:
        print("Warning: RESEND_FROM_ADDRESS is not set; notification skipped.", file=sys.stderr)
        return
    resend.api_key = _RESEND_API_KEY
    filtered_count = len(filtered_results)
    subject = "Dead link scan: {} — {} result(s) matching filter".format(website, filtered_count)
    body = _build_email_html(website, timestamp, total_links, filtered_results, excluded_summary)
    _send_via_resend(notify_email, _RESEND_FROM_ADDRESS, subject, body)
