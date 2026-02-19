# deadlinkchecker

Checks if a website has dead or not working links (HTTP 4xx, HTTP 5xx)

## Goal

With an input being a URL, scan the website for all internal and external links.

For external links, do not continue scanning,
For internal links, continue scanning until all links have been discoverrd.

Then, check all links to gather HTTP status code.

The output is a CSV for the run with the link itself, the referrer link, the HTTP status code.

Try to run the logic with parallel requests.
