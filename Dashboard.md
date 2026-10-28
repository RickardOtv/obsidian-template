---
cssclasses: [dashboard]
---

```dataviewjs
// ---- CONFIG: edit this block ----
const CONFIG = {
  name: "",                 // shown in the greeting, e.g. "Alex"
  locale: "en",             // date locale, e.g. "en", "sv", "de"
  quickLinks: [             // [note name, label] chips in the header
    ["Braindump", "🧠 Braindump"],
    ["Quick notes", "📥 Quick notes"],
  ],
  dailyNoteButtons: [],     // e.g. [{ label: "+ Stand-up", folder: "Team/Stand-up" }] (see README)
};
// ---------------------------------

const root = dv.container;
const el = (parent, tag, cls, text) => {
  const e = parent.createEl(tag, { cls });
  if (text !== undefined) e.setText(text);
  return e;
};
const internal = (parent, path, label, cls) =>
  parent.createEl("a", { cls: "internal-link " + (cls ?? ""), text: label, attr: { "data-href": path, href: path } });
const card = (parent, title, cls) => {
  const c = el(parent, "section", "dash-card " + (cls ?? ""));
  el(c, "h3", "", title);
  return el(c, "div", "dash-body");
};

const now = dv.date("now").setLocale(CONFIG.locale);
const iso = now.toFormat("yyyy-MM-dd");

// Data
const clean = s => s
  .replace(/\s*\((?:[^()]*\[\[[^\]]*\]\][^()]*)\)/g, "")
  .replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, "$2")
  .replace(/\[\[([^\]]+)\]\]/g, "$1")
  .replace(/📅\s*\d{4}-\d{2}-\d{2}/g, "")
  .replace(/[🔺🔼🔽⏫⏬]/gu, "")
  .replace(/\s{2,}/g, " ")
  .trim();
const rich = (parent, text) => {
  text.split(/(`[^`]+`)/).forEach(part => {
    if (part.startsWith("`")) parent.createEl("code", { text: part.slice(1, -1) });
    else parent.appendText(part);
  });
};
const fmtDue = d => d ? (d.toFormat ? d.toFormat("yyyy-MM-dd") : String(d).slice(0, 10)) : null;

const tasks = dv.pages().file.tasks.where(t => !t.completed).array().map(t => {
  const due = fmtDue(t.due) ?? t.text.match(/📅\s*(\d{4}-\d{2}-\d{2})/)?.[1] ?? null;
  return { path: t.path, line: t.line, raw: t.text, due, text: clean(t.text), high: /🔺|⏫/u.test(t.text) };
}).sort((a, b) => (a.due ?? "9999").localeCompare(b.due ?? "9999"));
const overdue = tasks.filter(t => t.due && t.due < iso).length;
const dueDays = new Set(tasks.filter(t => t.due).map(t => t.due));

const quick = (dv.page("Quick notes")?.file.lists.array() ?? []).map(l => l.text);
const events = dv.pages('"Reminders"')
  .where(p => /^\d\d-\d\d-\d{4}$/.test(p.file.name))
  .flatMap(p => p.file.lists.where(l => !l.task).map(l => {
    const [d, m, y] = p.file.name.split("-");
    return { date: `${y}-${m}-${d}`, path: p.file.path, text: l.text };
  }))
  .array()
  .sort((a, b) => a.date.localeCompare(b.date));
const upcomingEvents = events.filter(e => e.date >= iso);
events.forEach(e => dueDays.add(e.date));
const jiraRaw = (await dv.io.load("Jira.md")) ?? "";
const jira = [...jiraRaw.matchAll(/\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|/g)]
  .map(m => ({ key: m[1], url: m[2], title: m[3], status: m[4] }));
const jiraUpdated = jiraRaw.match(/Updated ([^–*]+?)\s*[–-]/)?.[1];
const prRaw = (await dv.io.load("Pull requests.md")) ?? "";
const prs = [...prRaw.matchAll(/\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|/g)]
  .map(m => ({ title: m[1], url: m[2], repo: m[3], status: m[4] }));
const prUpdated = prRaw.match(/Updated ([^–*]+?)\s*[–-]/)?.[1];
const recent = dv.pages()
  .where(p => !["Dashboard", "Quick notes", "Jira", "Pull requests", "Upcoming"].includes(p.file.name))
  .sort(p => p.file.mtime, "desc").limit(8).array();
const reminderNotes = new Map(dv.pages('"Reminders"').map(p => [p.file.name, p.file.path]));

// Layout
const dash = el(root, "div", "dash");
dash.style.setProperty("--side-bg", `url("${app.vault.adapter.getResourcePath("Attachments/topo-side.png")}")`);

const hero = el(dash, "div", "dash-hero");
const hour = now.hour;
el(hero, "div", "dash-hello", `${hour < 10 ? "Good morning" : hour < 17 ? "Hello" : "Good evening"}${CONFIG.name ? ", " + CONFIG.name : ""}`);
el(hero, "div", "dash-date", now.toFormat("cccc d LLLL yyyy"));
const refreshBtn = el(hero, "button", "qn-btn hero-refresh", "↻");
refreshBtn.title = "Refresh Jira and pull requests";
refreshBtn.onclick = () => {
  refreshBtn.textContent = "…";
  refreshBtn.disabled = true;
  const run = name => new Promise(res => window.require("child_process").execFile("/bin/zsh", [app.vault.adapter.getFullPath(`Scripts/${name}`)], err => res(!err)));
  Promise.all([run("refresh-jira.sh"), run("refresh-prs.sh")]).then(results => {
    refreshBtn.textContent = results.every(Boolean) ? "✓" : "✗";
    setTimeout(() => app.workspace.activeLeaf?.view?.previewMode?.rerender(true), 1500);
  });
};
const heroLinks = el(hero, "div", "hero-links");
for (const [path, label] of CONFIG.quickLinks) {
  internal(heroLinks, path, label, "chip-link");
}
const stats = el(hero, "div", "dash-stats");
for (const [n, label, warn] of [[tasks.length, "open tasks"], [overdue, "overdue", overdue > 0], [jira.length, "Jira issues"], [prs.length, "open PRs"], [upcomingEvents.length, "events"]]) {
  const s = el(stats, "div", "dash-stat" + (warn ? " warn" : ""));
  el(s, "span", "", String(n));
  s.appendText(label);
}

// Calendar
const cal = card(dash, `📆 ${now.toFormat("LLLL yyyy")}`, "cal");
const grid = el(cal, "div", "cal-grid");
["M", "T", "W", "T", "F", "S", "S"].forEach(d => el(grid, "div", "cal-head", d));
const first = now.startOf("month");
for (let i = 1 - (first.weekday - 1); i <= now.daysInMonth; i++) {
  if (i < 1) { el(grid, "div", "cal-day empty"); continue; }
  const date = first.plus({ days: i - 1 });
  const notePath = reminderNotes.get(date.toFormat("dd-MM-yyyy"));
  const cls = "cal-day" + (i === now.day ? " today" : "") + (dueDays.has(date.toFormat("yyyy-MM-dd")) ? " has" : "");
  if (notePath) internal(grid, notePath, String(i), cls);
  else el(grid, "div", cls, String(i));
}

if (upcomingEvents.length) {
  el(cal, "div", "cal-sub", "Events");
  for (const e of upcomingEvents.slice(0, 5)) {
    const row = el(cal, "div", "row");
    internal(row, e.path, e.text);
    el(row, "span", "chip", e.date.slice(5).split("-").reverse().join("/"));
  }
}

// Tasks
const tk = card(dash, "✅ To do", "tasks");
const addRow = el(tk, "div", "task-add");
const input = el(addRow, "input", "task-input");
input.placeholder = "New task… (Enter)";
const dateInput = el(addRow, "input", "task-date");
dateInput.type = "date";
const rerender = () => setTimeout(() => app.workspace.activeLeaf?.view?.previewMode?.rerender(true), 900);
input.addEventListener("keydown", async ev => {
  if (ev.key !== "Enter" || !input.value.trim()) return;
  const file = app.vault.getAbstractFileByPath("Reminders/To do.md");
  const line = `- [ ] ${input.value.trim()}${dateInput.value ? " 📅 " + dateInput.value : ""}`;
  await app.vault.process(file, d => d.replace(/\n*$/, "\n") + line + "\n");
  input.value = "";
  dateInput.value = "";
  rerender();
});

if (!tasks.length) el(tk, "div", "dash-empty", "Nothing to do 🎉");
for (const t of tasks.slice(0, 15)) {
  const late = t.due && t.due < iso;
  const row = el(tk, "div", "row task" + (late ? " late" : "") + (t.high ? " high" : ""));
  const box = el(row, "input", "task-check");
  box.type = "checkbox";
  box.onchange = async () => {
    const file = app.vault.getAbstractFileByPath(t.path);
    await app.vault.process(file, data => {
      const lines = data.split("\n");
      if (!lines[t.line]?.includes("[ ]")) return data;
      lines[t.line] = lines[t.line].replace("[ ]", "[x]") + ` ✅ ${iso}`;
      return lines.join("\n");
    });
    row.addClass("done");
  };
  const label = el(row, "a", "task-text");
  label.setAttr("title", t.text);
  label.onclick = async ev => {
    ev.preventDefault();
    const file = app.vault.getAbstractFileByPath(t.path);
    await app.workspace.getLeaf(false).openFile(file, { eState: { line: t.line } });
  };
  rich(label, t.text);
  if (t.due) {
    const when = dv.date(t.due);
    const days = Math.round(when.diff(dv.date("today"), "days").days);
    const txt = days === 0 ? "today" : days === 1 ? "tomorrow" : days < 0 ? `${-days}d ago` : when.toFormat("d LLL");
    el(row, "span", "chip", txt);
  }
}

// Jira
const jr = card(dash, `🎫 Jira${jiraUpdated ? " · " + jiraUpdated.trim() : ""}`, "jira");
if (!jira.length) el(jr, "div", "dash-empty", "No issues. Jira is optional - see README.md");
for (const j of jira.slice(0, 10)) {
  const row = el(jr, "div", "row");
  row.createEl("a", { text: `${j.key} ${j.title}`, attr: { href: j.url } });
  el(row, "span", "chip", j.status);
}

// Pull requests
const pr = card(dash, `🔀 My PRs${prUpdated ? " · " + prUpdated.trim() : ""}`, "prs");
if (!prs.length) el(pr, "div", "dash-empty", "No open PRs. GitHub is optional - see README.md");
for (const p of prs.slice(0, 10)) {
  const row = el(pr, "div", "row");
  row.createEl("a", { text: p.title, attr: { href: p.url } });
  el(row, "span", "chip", p.status);
}

// Quick notes
const qn = card(dash, "📥 Quick notes", "quick");
if (!quick.length) el(qn, "div", "dash-empty", "No quick notes yet");
for (const q of quick.slice(-8).reverse()) el(qn, "div", "row", q);
internal(qn, "Quick notes", "Open all →", "more");
el(qn, "div", "qn-hint", "⌥ + ⌘ + Q for a quick note");

const newDaily = async (folder) => {
  const path = `${folder}/${dv.date("today").toFormat("dd-MM-yyyy")}.md`;
  let file = app.vault.getAbstractFileByPath(path);
  if (!file) {
    file = await app.vault.create(path, "");
    await new Promise(r => setTimeout(r, 400));
  }
  await app.workspace.getLeaf(false).openFile(file);
};
const btnRow = el(qn.parentElement, "div", "qn-actions");
qn.parentElement.insertBefore(btnRow, qn);
el(btnRow, "button", "qn-btn", "+ Quick note").onclick = () => app.commands.executeCommandById("templater-obsidian:Templates/Quick note.md");
for (const b of CONFIG.dailyNoteButtons) {
  el(btnRow, "button", "qn-btn", b.label).onclick = () => newDaily(b.folder);
}

// Recent
const rc = card(dash, "🕘 Recently modified", "recent");
for (const p of recent) {
  const row = el(rc, "div", "row");
  internal(row, p.file.path, p.file.name);
}

const side = el(dash, "div", "dash-side");
el(side, "div", "big", String(now.day));
el(side, "div", "small", now.toFormat("cccc · LLLL"));
```
