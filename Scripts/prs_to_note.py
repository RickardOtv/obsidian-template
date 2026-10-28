import datetime
import json
import os
import sys
import urllib.request

out = sys.argv[1]
data = json.load(sys.stdin)
api = os.environ.get("GITHUB_API_URL", "https://api.github.com")

if "items" not in data:
    sys.exit(f"GitHub error: {data.get('message', 'unknown response')} (is GITHUB_TOKEN set in ~/.zshrc?)")


def get(path):
    req = urllib.request.Request(
        f"{api}{path}",
        headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"], "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except Exception:
        return None


def review_state(repo, number, author):
    reviews = get(f"/repos/{repo}/pulls/{number}/reviews?per_page=100") or []
    latest = {}
    for r in reviews:
        user = (r.get("user") or {}).get("login")
        if user and user != author and r["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            latest[user] = r["state"]
    states = set(latest.values())
    if "CHANGES_REQUESTED" in states:
        return "Changes requested"
    if "APPROVED" in states:
        return "Approved"
    return "Awaiting review"


def ci_state(repo, sha):
    runs = (get(f"/repos/{repo}/commits/{sha}/check-runs?per_page=100") or {}).get("check_runs", [])
    status = get(f"/repos/{repo}/commits/{sha}/status") or {}
    results = [r["conclusion"] for r in runs if r["status"] == "completed"]
    pending = any(r["status"] != "completed" for r in runs) or status.get("state") == "pending" and status.get("statuses")
    if any(c in ("failure", "timed_out", "cancelled", "action_required") for c in results) or status.get("state") in ("failure", "error"):
        return "CI failed"
    if pending:
        return "CI running"
    return None


def status_for(pr):
    repo = pr["repository_url"].split("/repos/")[-1]
    details = get(f"/repos/{repo}/pulls/{pr['number']}")
    if details is None:
        return "Open"

    if details.get("draft"):
        parts = ["Draft"]
    else:
        review = review_state(repo, pr["number"], pr["user"]["login"])
        parts = [] if review == "Awaiting review" and details.get("mergeable_state") == "dirty" else [review]

    ci = ci_state(repo, details["head"]["sha"])
    if ci:
        parts.append(ci)
    if details.get("mergeable_state") == "dirty":
        parts.append("Conflict")
    return " · ".join(parts)


lines = [
    "# 🔀 Pull requests",
    "",
    f"*Updated {datetime.datetime.now():%d-%m-%Y %H:%M} – {data['total_count']} open PRs*",
    "",
    "| Title | Repo | Status |",
    "|---|---|---|",
]
for pr in data["items"]:
    repo = pr["repository_url"].split("/repos/")[-1]
    title = pr["title"].replace("|", "/").replace("[", "(").replace("]", ")")
    lines.append(f"| [{title}]({pr['html_url']}) | {repo.split('/')[-1]}#{pr['number']} | {status_for(pr)} |")

with open(out, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"Wrote {out}")
