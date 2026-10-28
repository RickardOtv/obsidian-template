<%*
const title = await tp.system.prompt("Meeting title");
if (title) {
  const clean = title.replace(/[\\/:*?"<>|#^\[\]]/g, "").trim();
  const date = tp.date.now("DD-MM-YYYY");
  const content = `---
type: meeting
date: ${tp.date.now("YYYY-MM-DD")}
tags:
  - meeting
---
# 📅 ${clean} – ${date}

Back to [[Meetings]].

## Attendees

- 

## Notes

- 

## Action points

${"- [" + " ] "}
`;
  const folder = "Meetings";
  if (!tp.app.vault.getAbstractFileByPath(folder)) await tp.app.vault.createFolder(folder);
  await tp.file.create_new(content, `${date} ${clean}`, true, tp.app.vault.getAbstractFileByPath(folder));
}
-%>
