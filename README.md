# Dossier

Dossier is a passive OSINT reconnaissance toolkit for checking usernames, emails, and public footprint signals across common web surfaces.

It is designed for safe, read-only investigation and awareness workflows. The tool does not require login credentials, uses public URL patterns, and avoids intrusive scraping or credential theft.

## What it does

- Async username lookup across a curated set of public profile URLs
- Email footprint checks via public search and breach lookup URLs
- JSON export and local history logging
- Interactive terminal dashboard styled like a tactical reconnaissance console
- Safe HTTP probing with timeout, retry, and graceful handling of 403/404/429 responses

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

## Usage

Username scan:

```bash
dossier scan username alice
```

Email scan:

```bash
dossier scan email alice@example.com
```

JSON output:

```bash
dossier scan username alice --json
```

Interactive tactical console:

```bash
dossier ui
```

Web analyst dashboard:

```bash
dossier web
```

Open `http://127.0.0.1:8765` in your browser. The dashboard supports:

- Email and username investigations
- Email risk, domain, deliverability, and provider signals
- Digital footprint category counts
- Registered public account results
- Investigation metadata and local history
- Configured provider inspection

Read scan history:

```bash
dossier history
```

## Example workflow

```bash
dossier ui
```

Then choose:
- Investigate a target
- Review history
- Providers
- Diagnostics

## Notes

- Dossier performs passive checks only.
- It does not brute-force accounts, bypass authentication, or access private data.
- Respect platform rate limits, robots.txt, and local law.

## License

MIT
