# Dead Link Checker

A CLI tool to detect broken links on any website. Given a starting URL, it crawls all internal pages recursively, collects external links, checks their HTTP status codes, and outputs a CSV report.

## Features

- Recursive crawling of all internal links
- External links checked but not followed
- Visited URL tracking to prevent infinite loops
- Parallel HTTP requests for performance
- CSV output: `link, referrer, http_status_code`
- Markdown summary of non-200 results per scan
- Email notification via the Resend API when non-200 results are found

## Installation

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/checker.py <start_url> [options]
```

| Option            | Default                                   | Description                                                 |
| ----------------- | ----------------------------------------- | ----------------------------------------------------------- |
| `start_url`       | _(required)_                              | The URL to begin crawling from (must use `http` or `https`) |
| `--output`, `-o`  | `scans/[WEBSITE]/[TIMESTAMP]/results.csv` | Path to the output CSV file                                 |
| `--workers`, `-w` | `10`                                      | Number of parallel threads                                  |
| `--timeout`, `-t` | `10`                                      | Per-request timeout in seconds                              |
| `--user-agent`    | `deadlinkchecker/1.0`                     | User-Agent header sent with every request                   |
| `--notify-email`  | _(omitted)_                               | Recipient address for a post-scan email notification        |

When `--output` is omitted, results are written to `scans/[WEBSITE]/[TIMESTAMP]/` and a `README.md` summary is produced alongside `results.csv`.

**Example:**

```bash
python src/checker.py https://example.com --output report.csv --workers 20
```

### Email notifications

Pass `--notify-email` with a recipient address to receive a summary email after each scan. Three environment variables must be set:

| Variable              | Description                       |
| --------------------- | --------------------------------- |
| `RESEND_API_KEY`      | API key from your Resend account  |
| `RESEND_FROM_ADDRESS` | Verified sender address in Resend |

```bash
export RESEND_API_KEY=re_xxx
export RESEND_FROM_ADDRESS=scanner@yourdomain.com
python src/checker.py https://example.com --notify-email you@example.com
```

See [Resend website](https://resend.com/) for setting up your account.

## Output Format

Results are written to a CSV file with the following columns:

| Column             | Description                             |
| ------------------ | --------------------------------------- |
| `link`             | The URL that was checked                |
| `referrer`         | The page that contained the link        |
| `http_status_code` | HTTP response code (e.g. 200, 404, 500) |

## Testing

### Unit tests

```bash
python -m pytest tests/ -v
```

### Integration test

A sample website is available to test the tool against:

```plaintext
https://deadlinkchecker-sample-website.netlify.app
```

The expected output is (sorted by referrer, then link):

```csv
link,referrer,http_status_code
https://deadlinkchecker-sample-website.netlify.app/about/,https://deadlinkchecker-sample-website.netlify.app/,404
https://deadlinkchecker-sample-website.netlify.app/blog,https://deadlinkchecker-sample-website.netlify.app/,200
https://deadlinkchecker-sample-website.netlify.app/contact,https://deadlinkchecker-sample-website.netlify.app/,200
https://iamjeremie.me/,https://deadlinkchecker-sample-website.netlify.app/contact,200
https://iamjeremie.me/doesnt-exist,https://deadlinkchecker-sample-website.netlify.app/contact,404
```

Notes:

- `/about/` is an intentional dead link (404) on the sample site.
- `https://iamjeremie.me/` and `https://iamjeremie.me/doesnt-exist` are external links, checked but not crawled.
- Links to `/` discovered from `/contact` and `/blog` are skipped as already visited.

## Development

This project uses a multi-agent pipeline powered by Claude Code. Describe a feature request or bug fix and the orchestrator coordinates specialist agents automatically.

| Agent         | Role                                        |
| ------------- | ------------------------------------------- |
| Specification | Writes detailed specs from the user request |
| Coder         | Implements the feature based on specs       |
| Tester        | Validates the implementation with tests     |
| Versioning    | Commits to a Git Flow branch and pushes     |

Human approval gates pause the pipeline after specs and after coding.

### Pipeline artifacts

```plaintext
.agents-output/
├── user-requests.md   # your input
├── specs.md           # specification output
├── code-ready.md      # coder output
├── test-results.md    # test output
└── status.md          # current pipeline stage
```

### Branch naming

| Change type | Branch prefix |
| ----------- | ------------- |
| New feature | `feature/`    |
| Bug fix     | `fix/`        |
| Docs only   | `docs/`       |

### Manual testing

```bash
python src/checker.py https://deadlinkchecker-sample-website.netlify.app
```

## License

See [LICENSE](LICENSE).
