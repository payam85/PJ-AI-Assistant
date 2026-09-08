# PJ Career Assistant

One local SQLite database for LinkedIn drafts, imported contacts, CV evidence,
job-search drafts, application notes and API usage. UK, UAE/Dubai, Oman, Qatar and Kuwait.

## Run on this Mac

`./run.sh serve` opens the service at http://127.0.0.1:8421 (loopback only).
Open that address in your browser. The launcher reuses the existing ignored credential
file and installed SDK runtime; it never copies or prints the key.

Other commands: `./run.sh status`, `./run.sh daily`, `./run.sh import-history`,
`./run.sh generate linkedin 'A specific topic'`, `./run.sh reset-api`.
Reset the API circuit only after resolving the reported credit or authentication issue.

## Portable setup

Python 3.11+; create a virtual environment and install `requirements.txt`.
Set `OPENAI_API_KEY` securely or set `PJ_ENV_FILE` to an ignored existing env file.
Run `python app.py serve`. `Main.py` is a compatibility entry point; do not create
a separate lowercase `main.py` on a case-insensitive Mac filesystem.

## Lower usage

- Deterministic routing calls only the selected SDK specialist, not a team of models.
- Repeated task/profile/model/input combinations return the stored answer without an API call.
- The daily command has stable date/slot identities; imported posts also occupy their slots.
- Default daily cap: six attempted generations; output capped at 2,500 tokens per run.
- No automatic retries; quota/auth failures pause subsequent calls until deliberately reset.
- Send only current CV evidence and a small recent-record summary, not full chat history.
- No automatic image generation. Original images remain in private/cv-history.
- Recorded token cost is optional and based on user-configured rates; hosted web search
  fees are excluded. The cap is a call limit, not a guaranteed account-wide dollar budget.
- A run interrupted while running blocks further calls; review provider activity before
  manually marking it failed in the database. This avoids silently repeating billed work.

## What is implemented

SDK agents for LinkedIn, web-search leads, fit analysis, CV/cover letter, outreach drafts,
and an optional daily manager summary. `daily` uses direct routing for economy.
The dashboard saves CV evidence, creates/reuses drafts, records approval/status and tracks
application notes by vacancy URL. All actions are local except explicit API generation.
Imported post metadata overrides stale mentions in the networking log.

## Boundaries

No LinkedIn scraping, auto-publication, invitation sending, email sending, job application
submission or inbox synchronisation. Approval only records local review; completed/applied
statuses mean the user has manually performed that action. Job-search output is a set of
leads requiring source and eligibility review, not guaranteed live/eligible vacancies.
CV tailoring produces editable text; Word/PDF export is a later addition.
Work authorisation is unknown until supplied. CV claims are user-provided evidence.

## Private data and migration

`private/` contains the imported sources, CV, database and automation snapshots and is
ignored by Git. Back it up securely. The original Desktop and CV folders are preserved;
this checkout is the intended operational home. Never commit private data or credentials.
Source test_agent.py is preserved in private/legacy. The original Git history is retained.
Automation cutover status is documented in docs/cutover.md.

## Verification

`python -m unittest discover -s tests -v` tests cache reuse, profile invalidation, API cap,
concurrent-run exclusion, quota circuit, timeout behaviour, approvals and idempotent import.
Tests use isolated temporary databases and do not spend API credits.

SDK references: https://developers.openai.com/api/docs/guides/agents
and https://openai.github.io/openai-agents-python/running_agents/.
