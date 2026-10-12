# Obsidian Template Vault

A ready-to-use Obsidian vault with a dashboard homepage, tasks, quick capture, an icy-blue dark theme and optional Jira integration. No secrets, no personal data.

## What you get

- **Dashboard** (homepage): calendar, tasks (add/complete inline), Jira issues, quick notes, recently modified notes
- **Quick note** hotkey `⌥ ⌘ Q` → appended to `Quick notes.md`
- **Reminders/**: dated notes (`DD-MM-YYYY.md`) show as events on the dashboard calendar
- Minimal theme + blue CSS snippet (optional background image, see section 4)
- Optional: Jira refresh, stand-up/refinement notes, Git backup

## 1. Install

1. Install [Obsidian](https://obsidian.md) (and `git`).
2. Get the template:
   ```bash
   git clone git@github.com:RickardOtv/obsidian-template.git "My Vault"
   ```
   Or use **Use this template** on GitHub to create your own repo first, then clone that.
3. In Obsidian: **Open folder as vault** → select `My Vault`.
4. When asked, choose **Trust author and enable plugins**.

## 2. Install the theme

Settings → Appearance → Themes → **Manage** → install **Minimal** → select it.
Then Appearance → CSS snippets → enable `dashboard` and `theme-blue`.

## 3. Install the plugins

Plugin settings are already included in the repo, but plugin code is not. Settings → Community plugins → Turn on community plugins → Browse, then install **and enable**:

| Plugin | ID | Needed for |
|---|---|---|
| Dataview | `dataview` | Dashboard (**required**; enable *JavaScript queries* in its settings) |
| Tasks | `obsidian-tasks-plugin` | Task queries, due dates |
| Templater | `templater-obsidian` | Quick note, stand-up/refinement templates |
| Homepage | `homepage` | Opens `Dashboard` on startup |
| Minimal Theme Settings | `obsidian-minimal-settings` | Theme options |
| Calendar | `calendar` | Sidebar calendar |
| Full Calendar | `obsidian-full-calendar` | Calendar views |
| Iconize | `obsidian-icon-folder` | Icons on folders/notes |
| Banners | `obsidian-banners` | Note banners |
| Meta Bind | `obsidian-meta-bind-plugin` | Inputs in notes |
| Editing Toolbar | `editing-toolbar` | Formatting toolbar |
| Shell commands | `obsidian-shellcommands` | Run scripts from Obsidian (optional) |
| Git | `obsidian-git` | Automatic backup (optional, see below) |

Also enable Dataview's **JavaScript queries**: Settings → Dataview → *Enable JavaScript Queries*.

Restart Obsidian. The Dashboard should open automatically.

## 4. Personalize

Edit the `CONFIG` block at the top of `Dashboard.md`:

- `name` – name in the greeting
- `locale` – date language (`en`, `sv`, ...)
- `quickLinks` – header shortcuts
- `dailyNoteButtons` – buttons for stand-ups etc. (see section 6)

**Optional background image:** the dashboard's side panel uses `Attachments/topo-side.png` (portrait, about 1440x2560). It is not included for licensing reasons. Save any wallpaper you have the rights to use under that name, for example a topographic one from a free source such as Unsplash. Without it the panel simply has no image.

Replace this README and rename `Home.md` as you like. Dates in `Reminders/` use `DD-MM-YYYY`; this is hard-coded in `Dashboard.md` and `.obsidian/daily-notes.json`.

## 5. Optional: Jira

Skip this if you don't use Jira; the dashboard card then just shows a hint.

Requirements: macOS/Linux with `zsh`, `curl` and `python3`.

1. Create an API token:
   - **Jira Server / Data Center**: Profile → Personal Access Tokens → Create token.
   - **Jira Cloud**: https://id.atlassian.com/manage-profile/security/api-tokens
2. Add to `~/.zshrc` (never commit these):
   ```bash
   # Jira Server / Data Center
   export JIRA_URL="https://jira.example.com"
   export JIRA_TOKEN="your-personal-access-token"

   # Jira Cloud (also set the next two)
   # export JIRA_URL="https://your-site.atlassian.net"
   # export JIRA_EMAIL="you@example.com"
   # export JIRA_TOKEN="your-api-token"
   # export JIRA_API_PATH="/rest/api/3/search/jql"
   ```
3. Make the script executable and test it:
   ```bash
   chmod +x Scripts/refresh-jira.sh
   Scripts/refresh-jira.sh
   ```
   `Jira.md` should now list your open issues.
4. Use the **↻** button on the dashboard's Jira card to refresh. Obsidian must have been started with access to your shell environment; since the script sources `~/.zshrc` this works when launched normally.

To change which issues are shown, edit the `jql=` line in `Scripts/refresh-jira.sh`.

## 6. Optional: stand-ups and refinements

Not every team has these. To enable them:

1. Create the folders `Team/Stand-up` and `Team/Refinement`.
2. Move the files from `Templates/Optional/` as needed: `Stand-ups.md` and `Refinements.md` to `Team/` (overview notes), and `Stand-up.md` / `Refinement.md` to `Templates/`.
3. Settings → Templater → **Folder templates** → add:
   - `Team/Stand-up` → `Templates/Stand-up.md`
   - `Team/Refinement` → `Templates/Refinement.md`
4. In `Dashboard.md` CONFIG set:
   ```js
   dailyNoteButtons: [
     { label: "+ Stand-up", folder: "Team/Stand-up" },
     { label: "+ Refinement", folder: "Team/Refinement" },
   ],
   ```

Each button creates today's note in that folder and the template fills it in. Rename folders freely, just keep CONFIG and Templater in sync.

## 7. Optional: Git backup (Obsidian Git plugin)

1. Create your own **private** repo and point the vault at it:
   ```bash
   git remote set-url origin git@github.com:YOU/my-vault.git
   ```
2. Configure the Git plugin's auto commit interval in its settings.

Never put tokens or passwords in notes, as git history keeps them forever. The `.gitignore` already excludes workspace state, plugin code and `.smart-env/`.

## 8. Reusing the setup at another workplace

1. Clone the template again into a new folder and follow sections 1-4.
2. Only enable the optional parts (Jira, stand-ups) that apply there.
3. Use a separate vault per workplace; never copy notes between employers' vaults.

## 9. Troubleshooting

- **Dashboard is empty or shows code**: Dataview not enabled, or *JavaScript queries* is off.
- **Dashboard doesn't open on start**: enable the Homepage plugin; check it points to `Dashboard`.
- **Quick note hotkey does nothing**: Templater enabled? Settings → Hotkeys → search "Quick note".
- **Jira ↻ shows ✗**: run `Scripts/refresh-jira.sh` in a terminal to see the error.
- **Plugin settings look reset**: a plugin overwrote `data.json` the first time you ran it; this is normal.

## Updating plugin list

If you add a plugin you want to keep, add it to `.obsidian/community-plugins.json` and to the table in section 3.
