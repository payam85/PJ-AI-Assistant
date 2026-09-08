# Consolidation status — 8 September 2026

- Canonical code and state: this project directory and private/career.sqlite.
- Existing heartbeat `automation` updated successfully to **دستیار شغلی متمرکز**.
  It invokes this project's run.sh daily once per slot (09:00 and 17:00 London).
  It must not separately search, write posts, generate images or send invitations.
- Previous standalone `follow-up-monitor` successfully changed to PAUSED.
- Original scheduling configurations and job-search memory are backed up in private/automation-backup.
- Original CV assets and networking history preserved in private/cv-history; four Markdown
  sources imported idempotently. Two published posts, one draft, ten contacts and one sent
  message were reconciled into canonical records. Accepted/pending are historical observations.
- CV text imported from the previously referenced CV PDF; phone/email/postcode excluded
  from generation context. Original PDF is preserved privately. Work authorisation unknown.
- No source folders deleted or modified. Source repository's untracked test preserved.
- Existing credential file is referenced, not copied. Code and private state are central;
  the current Mac launcher still depends on the original credential file and Python runtime.

## Verification limits

Local API attempt failed with a connection error. The current sandbox also rejected
binding the dashboard to loopback. Escalated execution requests were rejected automatically
because sandbox approvals are disabled. No successful paid-model result is claimed.
The consolidated schedule is configured, but successful live daily execution is not yet
verified and may encounter the same environment restrictions. Old duplicate search remains paused.

Offline snapshot: run.sh snapshot. Interactive dashboard: run.sh serve when permitted.
This is an implemented local foundation, not an official LinkedIn publishing integration.
