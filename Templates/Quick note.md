<%*
const text = await tp.system.prompt("Quick note");
if (text) {
  const file = tp.file.find_tfile("Quick notes");
  await tp.app.vault.append(file, "- " + tp.date.now("DD-MM-YYYY HH:mm") + " – " + text + "\n");
  new Notice("Added to Quick notes");
}
-%>
