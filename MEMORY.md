# Customer Support App — Memory

## Support Dashboard (desk page)
- Desk page lives at the **module folder**: `customer_support/customer_support/page/support_dashboard/` (NOT app-root `page/`; app-root pages are not synced into `Page` records).
- Files: `support_dashboard.js` (self-contained controller, builds DOM inline — no template), `support_dashboard.py` (whitelisted `get_ticket_summary()`), `support_dashboard.json` (Page def, module "Customer Support").
- Route: `/app/support_dashboard`. Page record must exist; sync via `import_file_by_path` or `bench migrate`.
- The whitelisted method path is `customer_support.customer_support.page.support_dashboard.support_dashboard.get_ticket_summary` (module folder → double `customer_support`).
- Data source: HD Ticket doctype (`helpdesk` app). Counts statuses Open/Resolved/Closed and open tickets by priority Urgent/High/Medium/Low (actual values verified on site `tboindia`).
- Delta semantics: Open delta uses `creation` (new tickets); Resolved/Closed deltas use `modified` (status changed). Closed card shows "this month" count.
- Do NOT use the `page_js` hook for this page — it conflicts with the page-folder controller and pulled in a broken implementation that referenced a nonexistent template. `public/js/support_dashboard.js` was removed, `page_js` block removed from hooks.py.

## Helpdesk file uploads (LinkValidationError / 417)
- Helpdesk desk `TicketTextEditor.vue` uploads attachments to folder `Home/Helpdesk`, which must exist as a `File` record with `is_folder=1` under `Home`.
- If missing, upload fails with HTTP 417 + `frappe.exceptions.LinkValidationError: Could not find Folder: Home/Helpdesk` (417 is just Frappe's status code for `ValidationError`).
- Fix per site: `bench --site <site> execute helpdesk.setup.file.create_helpdesk_folder` (idempotent; the setup fn already exists in the helpdesk app).

## Cross-site ticket sync (pull into hub site)
- Sites have isolated DBs; HD Tickets do NOT auto-appear across sites. The hub site (e.g. `tboindia`) must pull remote tickets in.
- Config DocType: `Ticket Sync Source` (module `Customer Support`) — fields `site_name`, `site_url`, `api_key`, `api_secret` (Password), `enabled`, `last_sync_on`, `last_sync_message`. System Manager only.
- Core: `customer_support/customer_support/customer_support/sync_tickets.py` → whitelisted `sync_remote_tickets(source_name=None)`.
- Pulls via `GET /api/resource/HD Ticket` (token auth) and upserts into local `tabHD Ticket` with **direct SQL** (INSERT/UPDATE), bypassing helpdesk/customer_support doc_events (avoids notifications + custom naming-series autoname on sync).
- Provenance custom fields on HD Ticket (added by patch `add_ticket_sync_fields`): `custom_ticket_source`, `custom_remote_ticket`, `custom_synced_on`. Dedupe key = (`custom_ticket_source`, `custom_remote_ticket`); local `name` = `SYNC-<slug>-<remote>`. Skip rows whose `custom_ticket_source` is set to prevent ping-pong loops.
- Scheduler: `hooks.py` cron `*/15 * * * *` → `sync_remote_tickets`. Manual trigger: `bench --site tboindia execute customer_support.customer_support.sync_tickets.sync_remote_tickets`.
- `creation`/`modified` are preserved from remote so the dashboard's deltas stay correct.
- NOTE: `bench migrate` on tboindia prints a pre-existing `sync_customizations` JSONDecodeError from `apps/tbo_india/tbo_india/tbo_india/custom/lead.json` (invalid control char) — unrelated to this app; does not block the patch/doctype sync.
