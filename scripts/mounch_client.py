"""
Mounch API helper for the LCE syndicate site.

Usage:
    from mounch_client import call
    status, body = call("GET", "/form-templates")
    status, body = call("PATCH", "/workflows/10", {"isActive": True})

Token is read from the MOUNCH_TOKEN environment variable so it never
appears in source control. Set it before running:
    export MOUNCH_TOKEN="..."
"""
import os
import json
import urllib.request
import urllib.error

USER_AGENT = "LCE-Syndicat-Integrator/1.0 (+https://syndicat-lce.fr; sg@syndicat-lce.fr)"
BASE = "https://api.mounch.wdes.eu/api"


def call(method, path, payload=None, token=None):
    """
    Issue an HTTP request to the Mounch API.

    Returns (status_code, parsed_json_body). On HTTPError the body is
    still parsed when possible — no exception is raised so callers can
    inspect 4xx/5xx payloads.
    """
    token = token or os.environ.get("MOUNCH_TOKEN")
    if not token:
        raise RuntimeError("MOUNCH_TOKEN env var is not set")

    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode() or "{}"
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode() or "{}"
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"_raw": body}
