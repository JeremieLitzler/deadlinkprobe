# User Request — Issue #39

## Title

Add filter to keep status code in report

## Source

GitHub Issue: https://github.com/JeremieLitzler/deadlinkprobe/issues/39

## Description

Add a new CLI parameter to filter which HTTP status codes appear in the report output.

Key requirements:

- New parameter with default values of `404,500`
- CSV output includes only rows whose status code matches the parameter values
- Email reports display count summaries of status codes excluded from the parameter
- Email report details table shows only status codes matching the parameter values
- Deprecate the existing `--include-3xx-status-code` flag to consolidate functionality into the new filter parameter
- Update tests with default and custom parameter values (e.g. `404,500,403`)

## Nature of Change

Feature addition + deprecation of existing flag → feature branch
