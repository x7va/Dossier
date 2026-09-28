# Dossier

Small OSINT utility for checking usernames, email addresses, and the usual public web footprint.

It hits public URLs, records what comes back, and puts the results in a local report. No accounts, no magic, no private-data nonsense.

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

There is also a terminal menu if that is more your thing:

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

The dashboard also shows the results as a report instead of dumping a wall of URLs at you.

## A few obvious caveats

This is passive collection. It does not log in, brute-force anything, poke password-reset flows, or get around access controls.

A page returning `200` is not proof that a person owns an account. Treat results as leads, check the source, and use your judgement.

Be polite with providers, respect their terms and rate limits, and do not use this for stalking or harassment.

## License

MIT
