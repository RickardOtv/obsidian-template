#!/bin/zsh
# Refreshes Jira.md with the current user's open issues.
# Reads JIRA_URL, JIRA_TOKEN (and optionally JIRA_EMAIL, JIRA_API_PATH) from ~/.zshrc. See README.md.
source ~/.zshrc 2>/dev/null

if [[ -z "$JIRA_URL" || -z "$JIRA_TOKEN" ]]; then
  echo "JIRA_URL and JIRA_TOKEN must be set (see README.md)" >&2
  exit 1
fi

if [[ -n "$JIRA_EMAIL" ]]; then
  auth=(-u "$JIRA_EMAIL:$JIRA_TOKEN")
else
  auth=(-H "Authorization: Bearer $JIRA_TOKEN")
fi

curl -s --fail "${auth[@]}" --get \
  --data-urlencode "jql=assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC" \
  --data-urlencode "fields=summary,status" \
  --data-urlencode "maxResults=15" \
  "$JIRA_URL${JIRA_API_PATH:-/rest/api/2/search}" | python3 "${0:A:h}/jira_to_note.py" "$JIRA_URL" "${0:A:h}/../Jira.md"
