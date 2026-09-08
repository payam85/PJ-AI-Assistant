# PJ Career Assistant

One local SQLite database for LinkedIn drafts, imported contacts, CV evidence,
job-search drafts, application notes and API usage. UK, UAE/Dubai, Oman, Qatar and Kuwait.

## Try the offline demo first

The demo uses fictional data, makes **zero API calls**, and needs only Python 3.11+.

```bash
git clone https://github.com/payam85/PJ-AI-Assistant.git
cd PJ-AI-Assistant
python3 demo.py
```

Open `private/demo.html` in your browser. On Windows use `py` instead of `python3`.
The demo illustrates the workflow with fixed examples; it is not a live AI test.

## Install the full application

### macOS or Linux

From the downloaded project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` in a local text editor and set `OPENAI_API_KEY` to **your own** key.
Do not share it or commit it. An API account with model access and available credit is
required for real generation. The repository contains no usable key or personal profile.

On macOS/Linux, with the virtual environment active:

```bash
python doctor.py
python -m unittest discover -s tests -v
python app.py serve
```

On Windows, use `.\.venv\Scripts\python.exe` instead of `python` in these commands.
Open http://127.0.0.1:8421 in your browser and keep the terminal running.
Paste your own CV and work-authorisation details into **Your evidence**, then save.
Choose `linkedin` and enter a topic to test one real generation. A successful draft is
saved in **Your work**; submitting the identical request again reuses it.

For CV tailoring or fit analysis, paste the vacancy text into the request field.
The API call limit defaults to six attempts a day. Real generation may incur charges.

## Commands and scheduling

`python app.py status`, `python app.py daily`, `python app.py import-history`,
`python app.py generate linkedin 'A specific topic'`, `python app.py reset-api`.
Reset the API circuit only after resolving credit or authentication problems.

`daily` prepares job leads and one LinkedIn draft before 17:00 London time, and one
LinkedIn draft after 17:00. It runs once and exits; it is **not a background scheduler**.
Configure your own scheduler if needed. The author's Work automations are not distributed
with this repository. Failed daily slots are retained to prevent repeated billed attempts.

`./run.sh serve` is an optional Mac/Linux launcher. It uses `.venv` when available;
private/runtime.json can override local runtime and credential-file locations.
No machine-specific configuration is required for a fresh installation.

## Troubleshooting

- Missing module: activate the virtual environment and install `requirements.txt`.
- Missing key: save your key in `.env` at the project root; restart the app.
- `insufficient_quota`: check API billing/credit, then run `python app.py reset-api`.
- Connection failure: check the machine's network and execution permissions.
- Port already in use: run `python app.py serve --port 8422` and open that port.
- A run remains “running” after a crash: inspect provider activity before clearing it;
  automatic replay is deliberately disabled. There is no self-service recovery UI yet.

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

## Readiness and licence

This is an early local prototype, not a hosted service. Automated tests cover local
behaviour; successful live API generation, fresh dependency downloads on every platform,
and end-to-end job-search quality are not yet verified. See the boundaries above.

Released under the [MIT License](LICENSE). Each user supplies their own credentials,
profile and scheduling. Third-party services retain their own terms and charges.
