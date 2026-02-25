"""Email notification via the Resend API."""

import html
import os
import sys

import resend

_RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
_RESEND_FROM_ADDRESS = os.environ.get("RESEND_FROM_ADDRESS")


def _build_email_rows(non_200_results: list[tuple[str, str, str]]) -> str:
    rows = []
    for link, referrer, status in non_200_results:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(link),
                html.escape(referrer),
                html.escape(status),
            )
        )
    return "\n".join(rows)


def _build_email_html(
    website: str,
    timestamp: str,
    total_links: int,
    non_200_results: list[tuple[str, str, str]],
) -> str:
    non_200_count = len(non_200_results)
    lines = [
        "<p>Website: <strong>{}</strong></p>".format(html.escape(website)),
        "<p>Scan timestamp: {}</p>".format(html.escape(timestamp)),
        "<p>Total links checked: {}</p>".format(total_links),
        "<p>Non-200 results: {}</p>".format(non_200_count),
    ]
    if non_200_results:
        lines.append(
            "<table>"
            "<thead><tr><th>Link</th><th>Referrer</th><th>Status</th></tr></thead>"
            "<tbody>{}</tbody>"
            "</table>".format(_build_email_rows(non_200_results))
        )
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
    results: list[tuple[str, str, str]],
    website: str,
    timestamp: str,
    total_links: int,
    notify_email: str,
) -> None:
    """Send an email notification with scan results via the Resend API.

    Parameters
    ----------
    results:
        Full list of (link, referrer, http_status_code) tuples.
    website:
        The netloc of the scanned URL (used in subject and body).
    timestamp:
        The scan timestamp string (e.g. "2026-02-24T14-05-32").
    total_links:
        Total number of links checked.
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
    non_200_results = [row for row in results if row[2] != "200"]
    non_200_count = len(non_200_results)
    subject = "Dead link scan: {} — {} non-200 result(s)".format(website, non_200_count)
    body = _build_email_html(website, timestamp, total_links, non_200_results)
    _send_via_resend(notify_email, _RESEND_FROM_ADDRESS, subject, body)
