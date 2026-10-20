"""
Reads test_data.xlsx and turns it into overrides for test_config.json.

Sheets (all optional; header row is row 1, extra rows/blank rows are ignored):
  Credentials  columns: type | email | password      (type = valid / invalid)
  Signup       columns: setting | value              (first_name, last_name,
                                                      email_domain, password,
                                                      existing_email)
  Clubs        columns: club_name | tag_id
"""

from pathlib import Path

from openpyxl import load_workbook


def _rows(ws):
    """Yield each data row as {lowercased header: stripped string}, skipping blank rows."""
    rows = ws.iter_rows(values_only=True)
    header = next(rows, None)
    if not header:
        return
    keys = [str(h).strip().lower() if h is not None else "" for h in header]
    for row in rows:
        record = {k: ("" if v is None else str(v).strip()) for k, v in zip(keys, row) if k}
        if any(record.values()):
            yield record


def load_overrides(path):
    """Returns a partial config dict, e.g. {"login": {...}, "signup": {...}, "play_golf": {"clubs": [...]}}."""
    wb = load_workbook(Path(path), data_only=True, read_only=True)
    sheets = {name.strip().lower(): wb[name] for name in wb.sheetnames}
    overrides = {}

    if "credentials" in sheets:
        login = {}
        for r in _rows(sheets["credentials"]):
            kind = r.get("type", "").lower()
            if kind in ("valid", "invalid") and r.get("email"):
                login[f"{kind}_credentials"] = {"email": r["email"], "password": r.get("password", "")}
        if login:
            overrides["login"] = login

    if "signup" in sheets:
        signup = {r["setting"]: r.get("value", "") for r in _rows(sheets["signup"]) if r.get("setting")}
        signup = {k: v for k, v in signup.items() if v != ""}
        if signup:
            overrides["signup"] = signup

    if "clubs" in sheets:
        clubs = [
            {"name": r["club_name"], "tag_id": r["tag_id"]}
            for r in _rows(sheets["clubs"])
            if r.get("club_name") and r.get("tag_id")
        ]
        if clubs:
            overrides["play_golf"] = {"clubs": clubs}

    wb.close()
    return overrides


def merge_config(config, overrides):
    """Overlays overrides onto config one level deep (so unrelated keys in a section survive)."""
    for section, values in overrides.items():
        if isinstance(values, dict) and isinstance(config.get(section), dict):
            config[section].update(values)
        else:
            config[section] = values
    return config


def apply_club_tags(waypoints, clubs):
    """
    Fills in "tag_id" on every waypoint that names a "club" instead, using the
    Clubs list ({"name", "tag_id"}). Waypoints that already have a tag_id, or
    no club at all (movement-only points), are left alone.
    """
    by_name = {c["name"].strip().lower(): c["tag_id"] for c in clubs}
    for wp in waypoints:
        club = wp.get("club")
        if club and "tag_id" not in wp:
            tag = by_name.get(club.strip().lower())
            if tag is None:
                raise ValueError(
                    f"Waypoint '{wp.get('label', '?')}' (hole {wp.get('hole', 1)}) uses club "
                    f"'{club}', which isn't in the Clubs sheet. Available: {sorted(c['name'] for c in clubs)}"
                )
            wp["tag_id"] = tag
    return waypoints
