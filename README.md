# Cheetah Accounting

A local helper for South African personal and small-business tax, used through the **Claude Desktop** app, and
designed to work on the **Free** plan.

Cheetah reads your documents on your own computer (bank statements, IRP5s, certificates, invoices, photos of
slips), sorts and adds them up, and gives Claude short summaries to work with. Claude then asks you the questions
that matter, keeps a record of every decision, and prepares returns, schedules and letters **for you to check and
submit yourself** on SARS eFiling or CIPC. Nothing is submitted or paid by Claude.

## Quick start: setting up a new user, from step 0 to the end

Takes 20 to 30 minutes, once. Each step says what to do on **Windows**, **Mac** and **Linux**; do only the lines
for your system. Copy each command exactly, paste it into the terminal, and press Enter. Wait for one command to
finish before you paste the next.

**Shortcut:** you can skip steps 3 to 7 by running the one-line installer in [step 3a](#3a-one-line-installer).
**Want Claude to guide you instead?** Do step 1, then paste [docs/HANDOFF-PROMPT.md](docs/HANDOFF-PROMPT.md)
into a new Claude chat, and Claude will walk you through the rest.

### Step 0: what you need
- A Windows 10/11, macOS or Linux (Ubuntu or Debian) computer, with about 3 GB of free disk space.
- An internet connection (only needed for setup and updates; documents are read offline).
- A Claude account. The Free plan is enough on Windows and Mac.
- No administrator rights are needed, except to install Git and Claude Desktop on Linux.
- Everything goes into one folder in your home folder, called `Cheetah`:
  - `Cheetah/app`: the program, downloaded from this repository
  - `Cheetah/workspace`: your own documents and records (never uploaded, never touched by updates)

### Step 1: install Claude Desktop and sign in
- **Windows and Mac:** download it from https://claude.com/download, install it, open it and sign in.
- **Linux:** Anthropic's Linux app is an official beta for Ubuntu and Debian. Follow the Linux instructions on
  https://claude.com/download (an apt repository, or a `.deb` file). Other distributions only have unofficial
  community builds, which you use at your own risk. (check: one report says the Linux beta needs a paid plan)

Then in Claude Desktop turn off training on your chats: **Settings > Privacy > "Help improve Claude" off**.

### Step 2: open a terminal
- **Windows:** press the Start button, type `PowerShell`, and click **Windows PowerShell**. (No admin needed.)
- **Mac:** press Cmd+Space, type `Terminal`, press Enter.
- **Linux:** press Ctrl+Alt+T (or open "Terminal" from your applications).

Keep this window open until step 7.

### Step 3: install Git and uv (the Python tool manager)
**Windows (PowerShell):**
```powershell
winget install --id Git.Git -e --source winget
winget install --id astral-sh.uv -e --source winget
```
Close PowerShell and open it again (step 2), so it finds the new programs. Check with `git --version` and
`uv --version`; each prints a version number.

**Mac (Terminal):**
```sh
xcode-select --install
```
Click **Install** in the window that pops up and wait for it to finish (this provides Git). Then:
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
```

**Linux (Terminal):** on Ubuntu or Debian
```sh
sudo apt update && sudo apt install -y git curl
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
```
(Fedora: `sudo dnf install -y git curl`; Arch: `sudo pacman -S --needed git curl`; then the two `uv` lines.)

Check with `git --version` and `uv --version`.

#### 3a. One-line installer
Instead of steps 3 to 7, you can run the installer. It does everything in those steps for you, and you can run it
again at any time to repair or update. Then continue at step 8.
- **Windows (PowerShell):**
  `irm https://raw.githubusercontent.com/Skermunkel/Cheetah-Accounting/main/install/install.ps1 | iex`
- **Mac and Linux (Terminal):**
  `curl -LsSf https://raw.githubusercontent.com/Skermunkel/Cheetah-Accounting/main/install/install.sh | sh`

### Step 4: download Cheetah (clone the repository)
These commands are the same on all three systems (PowerShell understands them too):
```sh
cd ~
mkdir Cheetah
cd Cheetah
git clone https://github.com/Skermunkel/Cheetah-Accounting.git app
cd app
```
You are now in `Cheetah/app` (Windows: `C:\Users\<you>\Cheetah\app`; Mac: `/Users/<you>/Cheetah/app`;
Linux: `/home/<you>/Cheetah/app`). If `mkdir` says the folder already exists, carry on.

### Step 5: install Cheetah's requirements
Still in `Cheetah/app`:
```sh
uv sync
```
The first time takes a few minutes: uv downloads its own Python and the document-reading libraries (about 1 to
2 GB). You do not need to install Python yourself.

### Step 6: connect Cheetah to Claude Desktop and build the skills
Still in `Cheetah/app`:
```sh
uv run cheetah setup-claude
uv run cheetah build-skills
```
`setup-claude` adds a `cheetah` entry to Claude Desktop's settings file and keeps a backup of the old file
(`claude_desktop_config.json.bak`). Your workspace is created at `~/Cheetah/workspace`.
`build-skills` makes four zip files in `Cheetah/app/dist/skills` for step 9.

### Step 7: download the document-reading models, then check everything
```sh
uv run cheetah warm
uv run cheetah doctor
```
`warm` downloads the models that read scans and photos (about 500 MB, once). If the OCR download fails, it tries
three times; if it still fails, the models download the first time you add a scan or photo instead.
`doctor` should print `ok` for `mcp`, `pdfplumber` and `docling`, and `registered` for Claude. If anything says
MISSING or NOT registered, run steps 5 and 6 again.

### Step 8: restart Claude Desktop completely
Closing the window is not enough; the app has to quit:
- **Windows:** right-click the Claude icon next to the clock (bottom right; click the `^` arrow if it is hidden)
  and choose **Quit**. Open Claude again from the Start menu.
- **Mac:** with Claude in front, press Cmd+Q (or Claude menu > Quit Claude). Open it again from Applications.
- **Linux:** use **Quit** from the Claude tray icon or the app menu, then open it again.

Check: start a new chat and click the tools button (the sliders icon under the message box). **cheetah** should be
listed and switched on. If it is missing, open **Settings > Developer**: it shows the cheetah server and its
error message.

### Step 9: turn on Skills and upload Cheetah's skills
1. **Settings > Capabilities**: turn on **Code execution and file creation**.
2. Under **Skills**, click **Upload skill** and upload each zip from `Cheetah/app/dist/skills`, one at a time:
   `cheetah-init.zip`, `cheetah-personal-tax.zip`, `cheetah-company-tax.zip`, `cheetah-bookkeeping.zip`.
   To open that folder: **Windows** `explorer $HOME\Cheetah\app\dist\skills`; **Mac** `open ~/Cheetah/app/dist/skills`;
   **Linux** `xdg-open ~/Cheetah/app/dist/skills`.

If your plan does not show Skills, skip this step. Cheetah still works: in a chat, click **+ > Add from cheetah**
and choose the guide (for example **cheetah-init**).

### Step 10: run cheetah-init
Start a new chat and type **cheetah-init**, then press Enter (or pick it from **+ > Add from cheetah**). Claude:
1. checks that the cheetah tools work;
2. asks about you: age group, income, medical aid, retirement annuity, any business, and any SARS or CIPC letters;
3. asks you to save your eFiling returns history and statements of account into the inbox, and reads them;
4. works out what has to be filed first, and why;
5. creates your workspace folders (one per taxpayer: you, and each business) and a task list;
6. walks you through creating one **Claude Project** per taxpayer: Projects > New project, name it
   "Cheetah - <name>", paste in `INSTRUCTIONS.md`, and add `ABOUT.md` and `GROUND-RULES.md` as project files
   (all three are in `Cheetah/workspace/projects/<name>/`);
7. gives you a short list of documents to collect first.

### Step 11: everyday use
- Save documents (PDFs, CSV statements, photos of slips, certificates) into `Cheetah/workspace/inbox/<name>`
  (Windows: `$HOME\Cheetah\workspace\inbox\<name>`), then tell Claude **"ingest my documents"** inside that
  taxpayer's Project.
- Bank statements: CSV downloads from online banking are the most reliable; PDFs work for most banks. FNB credit
  card PDFs do not parse yet, so use their CSV.
- Claude prepares; you check, sign and submit on SARS eFiling or CIPC yourself.
- On the Free plan, if you hit a usage limit, wait for the reset. Everything is saved on your computer.
- Back up the `Cheetah/workspace` folder regularly, and keep it for at least five years (tax records).

### Step 12: updates
Ask Claude **"update Cheetah"**, then quit and reopen Claude Desktop (step 8). Or by hand:
```sh
cd ~/Cheetah/app
git pull
uv run cheetah build-skills
```
Re-upload the skills only if the changelog says they changed (the guides they load update by themselves).

### Step 13: problems and feedback
- Ask Claude to **"send feedback to the Cheetah maintainer"**. It opens a pre-filled GitHub issue with names,
  numbers and amounts masked; read it and click Submit (needs a free GitHub account).
- `uv` or `git` "not recognised" or "command not found": close the terminal, open a new one, and try again.
- The cheetah tools do not appear: check **Settings > Developer**, then run `cd ~/Cheetah/app` and
  `uv run cheetah doctor`, and send the output to the maintainer.
- **Mac:** if `xcode-select --install` says the tools are already installed, carry on.

### Removing Cheetah
Delete the `Cheetah/app` folder and remove the `cheetah` entry in **Settings > Developer > Edit Config**.
Keep `Cheetah/workspace`: it holds your tax records.

## What it covers
- Personal income tax (ITR12): certificates, auto-assessment checks, refund estimates (tax years 2023-2026)
- Sole proprietors and companies: bank statements to categorised books, year summary, director's loan, ITR14 and
  financial statements preparation, VAT201 and PAYE basics, CIPC annual return and beneficial ownership
- Catching up: what to file first, penalty remission requests and motivation letters
- Optional bookkeeping in **Zoho Books** (Free plan) through Claude's Zoho Books connector

## How it fits together

| Part | Where it runs | What it does |
|---|---|---|
| `src/cheetah/` (MCP server) | your computer | reads documents (pdfplumber, Docling), parses statements, applies rules, writes working papers, PDFs, CSVs |
| `knowledge/` guides | served by the MCP server | the process and SA tax reference, read by Claude only when needed |
| `skills/` | uploaded to Claude | thin entry points (cheetah-init and others) that load the guides from the installed version |
| Claude Project per taxpayer | Claude Desktop | instructions and a short profile; live state comes from `cheetah_status` |
| Zoho Books connector | Claude (optional) | invoices, reports and year-end journals for businesses that use Zoho |
| `Cheetah/workspace/` | your computer | your documents, transactions, decisions and outputs; never in this repo |

**Why the work happens locally:** the Free plan has usage limits. Reading a 20-page statement in a chat uses far
more than a 10-line summary of it. Cheetah does the reading and arithmetic on your computer, checks every
statement against its opening and closing balances, and sends Claude only what it needs to decide or ask.

**Document reading:** digital PDFs use their exact text layer (no AI model, no mistakes). Scans, photos, Word
and Excel files use [Docling](https://github.com/docling-project/docling) (MIT licence), which runs fully offline
after a one-time model download and handles tables and OCR.

**Updates:** the skills only point at the guides; the guides and tools come from the installed copy of this
repo. Asking Claude to "update Cheetah" pulls the latest version, so improvements reach everyone without
re-uploading skills.

## Privacy
- Documents and records stay in `Cheetah/workspace` on your computer. Only the summaries you discuss in a chat
  go to Claude. Turn off "Help improve Claude" in Settings > Privacy.
- Feedback (`cheetah_feedback`) opens a GitHub issue for you to read before submitting; ID, tax and account
  numbers, emails, phone numbers and amounts are masked.

## Not tax advice
Cheetah helps you prepare. Tax rules change every year; check figures marked "(check)" on sars.gov.za, and use a
registered tax practitioner for audits, disputes, estates, trusts or foreign income.

## Development
```
uv sync
uv run pytest
uv run cheetah doctor
```
Add a bank format: put an anonymised statement text in `tests/fixtures/`, make `statements.py` parse it, and add
a test that it reconciles. Add a tax year: extend the tables in `tax.py` with the SARS source in the docstring.

Licence: MIT.
