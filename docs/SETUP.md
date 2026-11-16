# Setting up Cheetah Accounting

About 15 minutes, once. You need a Windows or Mac computer, an internet connection, and a free Claude account.
Your tax documents stay on your computer; Cheetah never uploads them anywhere.

## 1. Install Claude Desktop
Download it from https://claude.com/download, install it and sign in.

## 2. Install Cheetah
**Windows**: press the Start button, type `PowerShell`, open it, paste this line and press Enter:

```
irm https://raw.githubusercontent.com/Skermunkel/Cheetah-Accounting/main/install/install.ps1 | iex
```

**Mac**: open the Terminal app (Spotlight: type `Terminal`), paste this line and press Enter:

```
curl -LsSf https://raw.githubusercontent.com/Skermunkel/Cheetah-Accounting/main/install/install.sh | sh
```

It takes a few minutes the first time (it downloads Python and the document-reading models, about 1 GB in all).
It creates a `Cheetah` folder in your home folder:
- `Cheetah\app`: the program (updated from GitHub)
- `Cheetah\workspace`: your own files (never uploaded, never overwritten by updates)

## 3. Restart Claude Desktop
Quit it completely (Windows: right-click the Claude icon near the clock > Quit; Mac: Claude menu > Quit), then open
it again. In a new chat, the tools menu (the sliders icon under the message box) now lists **cheetah**.

## 4. Settings in Claude Desktop
1. **Privacy**: Settings > Privacy > turn off "Help improve Claude", so your tax chats are not used for training.
2. **Skills**: Settings > Capabilities > turn on "Code execution and file creation". Then under Skills, upload each
   zip file from the folder the installer opened (`Cheetah\app\dist\skills`): cheetah-init, cheetah-personal-tax,
   cheetah-company-tax, cheetah-bookkeeping.
   If your plan does not show Skills, skip this: Cheetah works without them (see step 5).

## 5. Start
In a new chat type **cheetah-init** and press Enter. Claude asks about your situation, works out what to file
first, creates your folders, and helps you make a Claude Project for each taxpayer (you, and your business if you
have one).

Without the skills: click the **+** button in the chat > **Add from cheetah** > **cheetah-init**, then press Enter.

## Using it
- Save documents (PDFs, photos of slips, statements, certificates) into `Cheetah\workspace\inbox\<name>` and tell
  Claude "ingest my documents".
- Each chat about a taxpayer goes inside that taxpayer's Claude Project.
- The Free plan has usage limits. If you reach one, wait for the reset: everything is saved on your computer and
  Claude continues where you left off.

## Updating
Ask Claude: "update Cheetah". Then quit and reopen Claude Desktop. (Or run the install line from step 2 again.)

## Problems or ideas
Ask Claude to "send feedback to the Cheetah maintainer". It opens a pre-filled GitHub issue with personal details
removed; you read it and click Submit (a free GitHub account is needed). Or tell the person who set this up.

If the **cheetah** tools do not appear after a restart: Settings > Developer shows the server and its error.
Then run this in PowerShell or Terminal and send the output to the maintainer:

```
uv --directory "$HOME/Cheetah/app" run cheetah doctor
```

## Removing it
Delete the `Cheetah\app` folder and remove the `cheetah` entry under Settings > Developer > Edit Config.
Keep `Cheetah\workspace` for at least five years: it holds your tax records.
