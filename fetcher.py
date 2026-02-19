"""HTTP request utilities."""

import socket
import urllib.error
import urllib.request


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Prevent redirect following by raising HTTPError on any 3xx response."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)


def check_url(url: str, timeout: int, user_agent: str) -> str:
    """Return the HTTP status code as a string, or 'ERROR:<ExceptionClassName>'.

    Issues HEAD first; retries with GET on HTTP 405.
    Does not follow redirects — 3xx codes are recorded as-is.
    """
    opener = urllib.request.build_opener(NoRedirectHandler())

    def _do_request(method: str) -> str:
        request = urllib.request.Request(url, method=method)
        request.add_header("User-Agent", user_agent)
        response = opener.open(request, timeout=timeout)
        return str(response.status)

    try:
        return _do_request("HEAD")
    except urllib.error.HTTPError as e:
        if e.code == 405:
            try:
                return _do_request("GET")
            except urllib.error.HTTPError as e2:
                return str(e2.code)
            except urllib.error.URLError:
                return "ERROR:URLError"
            except (TimeoutError, socket.timeout):
                return "ERROR:TimeoutError"
            except Exception as e2:
                return f"ERROR:{type(e2).__name__}"
        return str(e.code)
    except urllib.error.URLError:
        return "ERROR:URLError"
    except (TimeoutError, socket.timeout):
        return "ERROR:TimeoutError"
    except Exception as e:
        return f"ERROR:{type(e).__name__}"


def fetch_html(url: str, timeout: int, user_agent: str) -> str | None:
    """Fetch the response body of an internal page for link extraction.

    Follows redirects (default urllib behaviour).
    Returns None if the content type is not text/html or on any error.
    """
    try:
        request = urllib.request.Request(url, method="GET")
        request.add_header("User-Agent", user_agent)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None
            charset = "utf-8"
            if "charset=" in content_type:
                for part in content_type.split(";"):
                    part = part.strip()
                    if part.startswith("charset="):
                        charset = part.split("=", 1)[1].strip()
                        break
            raw = response.read()
            return raw.decode(charset, errors="replace")
    except Exception:
        return None
