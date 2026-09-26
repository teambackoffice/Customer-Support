# Copyright (c) 2024, nehala and contributors
# For license information, please see license.txt

import json

import frappe
import requests
from frappe import _
from frappe.utils import get_datetime_str, now_datetime


# Fieldnames pulled from the remote HD Ticket and written to the local copy.
# Column names in `tabHD Ticket` match these fieldnames (custom_* are custom fields).
SYNC_FIELDS = [
    "subject",
    "status",
    "priority",
    "status_category",
    "ticket_type",
    "raised_by",
    "customer",
    "contact",
    "custom_customer",
    "custom_module",
    "first_responded_on",
    "resolution_date",
    "description",
]

PAGE_LENGTH = 200
DEFAULT_TICKET_TYPE = "Technical Support"
DEFAULT_STATUS = "Open"


def _make_local_name(source, remote_name):
    """Local name mirrors the remote ticket name (dedupe is per source)."""
    return (remote_name or "ticket")[:130]


def _ensure_unique_name(candidate):
    name = candidate[:130]
    i = 1
    while frappe.db.exists("HD Ticket", name):
        suffix = "-{0}".format(i)
        name = "{0}{1}".format(candidate[: 130 - len(suffix)], suffix)
        i += 1
    return name


@frappe.whitelist()
def sync_remote_tickets(source_name=None):
    """Pull HD Tickets from enabled Ticket Sync Source records into this site.

    Args:
        source_name (str, optional): sync a single source by name; otherwise
            every enabled source is processed.
    """
    if not frappe.has_permission("Ticket Sync Source", "write"):
        frappe.throw(_("Not permitted to run ticket sync."), frappe.PermissionError)

    if source_name:
        sources = [frappe.get_doc("Ticket Sync Source", source_name)]
    else:
        source_names = frappe.get_all(
            "Ticket Sync Source", filters={"enabled": 1}, order_by="site_name", pluck="name"
        )
        sources = [frappe.get_doc("Ticket Sync Source", name) for name in source_names]

    results = []
    for source in sources:
        try:
            created, updated, last_modified = _pull_source(source)
            source.db_set("last_sync_on", last_modified or now_datetime())
            _set_sync_status(source, "OK: {0} created, {1} updated".format(created, updated))
            frappe.db.commit()
            results.append(
                {"site": source.site_name, "created": created, "updated": updated, "status": "ok"}
            )
        except Exception as e:
            frappe.log_error(
                frappe.get_traceback(), "Ticket Sync Failed: {0}".format(source.site_name)
            )
            _set_sync_status(source, "Error: {0}".format(e))
            frappe.db.commit()
            results.append({"site": source.site_name, "status": "error", "error": str(e)})

    return results


def _set_sync_status(source, message):
    try:
        source.db_set("last_sync_message", (message or "")[:500])
    except Exception:
        pass


def _pull_source(source):
    """Fetch HD Tickets from a remote site and upsert them locally."""
    url = source.site_url.rstrip("/") + "/api/resource/HD Ticket"
    headers = {
        "Authorization": "token {0}:{1}".format(source.api_key, source.get_password("api_secret")),
        "Accept": "application/json",
    }

    params = {
        "fields": json.dumps(
            ["name", "creation", "modified", "custom_ticket_source"] + SYNC_FIELDS
        ),
        "limit_page_length": PAGE_LENGTH,
        "order_by": "modified asc",
    }
    if source.last_sync_on:
        params["filters"] = json.dumps(
            [["modified", ">", get_datetime_str(source.last_sync_on)]]
        )

    created = 0
    updated = 0
    max_modified = None
    limit_start = 0
    while True:
        page = dict(params)
        page["limit_start"] = limit_start
        resp = requests.get(url, headers=headers, params=page, timeout=60)
        resp.raise_for_status()
        data = (resp.json() or {}).get("data") or []
        if not data:
            break

        for row in data:
            modified = row.get("modified")
            if modified and (max_modified is None or modified > max_modified):
                max_modified = modified
            # Skip tickets that are themselves synced copies, to avoid ping-pong loops.
            if (row.get("custom_ticket_source") or "").strip():
                continue
            if _upsert_ticket(source, row):
                created += 1
            else:
                updated += 1

        limit_start += len(data)
        if len(data) < PAGE_LENGTH:
            break

    return created, updated, max_modified


def _upsert_ticket(source, row):
    """Insert or update the local copy of a remote ticket. Returns True if created."""
    remote_name = row.get("name")
    if not remote_name:
        return False

    existing = frappe.db.get_value(
        "HD Ticket",
        {"custom_ticket_source": source.site_name, "custom_remote_ticket": remote_name},
        "name",
    )

    now = now_datetime()
    if existing:
        values = {key: row.get(key) for key in SYNC_FIELDS}
        values["modified"] = row.get("modified") or now
        _apply_defaults(values)
        _update_ticket(existing, values)
        return False

    values = {
        "name": _ensure_unique_name(_make_local_name(source, remote_name)),
        "creation": row.get("creation") or now,
        "modified": row.get("modified") or now,
        "modified_by": "Administrator",
        "owner": "Administrator",
        "docstatus": 0,
        "idx": 1,
        "custom_ticket_source": source.site_name,
        "custom_remote_ticket": remote_name,
        "custom_synced_on": now,
    }
    for key in SYNC_FIELDS:
        values[key] = row.get(key)
    _apply_defaults(values)
    _insert_ticket(values)
    return True


def _apply_defaults(values):
    """Static defaults applied to every synced ticket."""
    values["ticket_type"] = DEFAULT_TICKET_TYPE
    if not values.get("status"):
        values["status"] = DEFAULT_STATUS
    return values


def _insert_ticket(values):
    columns = [
        "name",
        "creation",
        "modified",
        "modified_by",
        "owner",
        "docstatus",
        "idx",
    ] + SYNC_FIELDS + ["custom_ticket_source", "custom_remote_ticket", "custom_synced_on"]
    cols = ", ".join("`{0}`".format(c) for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    vals = [values.get(c) for c in columns]
    frappe.db.sql(
        "INSERT INTO `tabHD Ticket` ({0}) VALUES ({1})".format(cols, placeholders), vals
    )


def _update_ticket(name, values):
    assignments = ", ".join("`{0}`=%s".format(k) for k in values)
    vals = [values[k] for k in values] + [name]
    frappe.db.sql(
        "UPDATE `tabHD Ticket` SET {0} WHERE `name`=%s".format(assignments), vals
    )
