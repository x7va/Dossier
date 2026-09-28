# Dossier

Small OSINT utility for checking usernames, email addresses, and the usual public web footprint.

It hits public URLs, records what comes back, and puts the results in a local report.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Use it

Check a username:

```bash
dossier scan username alice
```

Check an email:

```bash
dossier scan email alice@example.com
```

Get JSON instead of terminal output:

```bash
dossier scan username alice --json
```

Run the local dashboard:

```bash
dossier web
```

Then open [http://127.0.0.1:8765](http://127.0.0.1:8765).

There is also a terminal menu:

```bash
dossier ui
```

History lives here:

```bash
dossier history
```

## What it checks

- Public profile URLs for common services
- Email and domain basics
- DNS and website reachability
- Public account matches
- A local record of each investigation


A page returning `200` is not proof that a person owns an account. Treat results as leads, check the source.

Respect terms and rate limits.

## License

MIT
