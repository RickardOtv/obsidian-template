import datetime
import json
import sys

url, out = sys.argv[1], sys.argv[2]
data = json.load(sys.stdin)

if "issues" not in data:
    sys.exit(f"Unexpected Jira response: {json.dumps(data)[:300]}")

issues = data["issues"]
lines = [
    "# 🎫 Jira",
    "",
    f"*Updated {datetime.datetime.now():%d-%m-%Y %H:%M} – {len(issues)} open issues*",
    "",
    "| Issue | Title | Status |",
    "|---|---|---|",
]
for issue in issues:
    fields = issue["fields"]
    key = issue["key"]
    summary = fields["summary"].replace("|", "/")
    lines.append(f"| [{key}]({url}/browse/{key}) | {summary} | {fields['status']['name']} |")

with open(out, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"Wrote {out}")
