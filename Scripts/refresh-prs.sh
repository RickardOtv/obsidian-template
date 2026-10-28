#!/bin/zsh
# Refreshes Pull requests.md with the open PRs you are involved in (authored, reviewed, assigned, mentioned or commented).
# Reads GITHUB_TOKEN (and optionally GITHUB_API_URL for GitHub Enterprise) from ~/.zshrc. See README.md.
source ~/.zshrc 2>/dev/null

if [[ -z "$GITHUB_TOKEN" ]]; then
  echo "GITHUB_TOKEN must be set (see README.md)" >&2
  exit 1
fi

curl -s --fail -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" --get \
  --data-urlencode "q=is:pr is:open involves:@me archived:false" \
  --data-urlencode "sort=updated" \
  --data-urlencode "per_page=30" \
  "${GITHUB_API_URL:-https://api.github.com}/search/issues" | python3 "${0:A:h}/prs_to_note.py" "${0:A:h}/../Pull requests.md"
