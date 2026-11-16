---
name: cheetah-init
description: Start or resume Cheetah Accounting setup for a South African taxpayer. Use when the person says "cheetah-init", "set up Cheetah", "help me get my tax up to date", or is new to Cheetah. Interviews them about their personal and business tax, finds what is outstanding, decides what to file first, and creates their workspace and Claude Projects.
---

# cheetah-init

1. Call the `cheetah_status` tool (Cheetah's local MCP server).
   - If no Cheetah tools are available, Cheetah is not installed or Claude Desktop needs a full restart. Explain
     that, and give the setup link: https://github.com/Skermunkel/Cheetah-Accounting/blob/main/docs/SETUP.md
     Do not continue without the tools.
2. Call `cheetah_guide("init")` and follow it exactly. It always comes from the installed version, so it stays
   current when Cheetah updates.
3. Apply `cheetah_guide("ground-rules")` throughout: the person submits on eFiling themselves, never guess,
   never backdate, record every decision.
