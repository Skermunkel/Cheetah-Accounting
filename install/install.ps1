# Cheetah Accounting installer for Windows. In PowerShell (no admin needed):
#   irm https://raw.githubusercontent.com/Skermunkel/Cheetah-Accounting/main/install/install.ps1 | iex
# Installs into %USERPROFILE%\Cheetah: app\ (this repo) and workspace\ (your private files, never uploaded).
# Run it again at any time to repair or update.
$ErrorActionPreference = 'Stop'
$Base = Join-Path $env:USERPROFILE 'Cheetah'
$App = Join-Path $Base 'app'
$env:CHEETAH_WORKSPACE = Join-Path $Base 'workspace'
$Repo = 'https://github.com/Skermunkel/Cheetah-Accounting'

Write-Host '1/5 Python tools (uv)'
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    powershell -ExecutionPolicy ByPass -c 'irm https://astral.sh/uv/install.ps1 | iex'
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

Write-Host '2/5 Cheetah app'
New-Item -ItemType Directory -Force -Path $Base | Out-Null
if (Test-Path "$App\.git") {
    git -C $App pull --ff-only
} elseif (Get-Command git -ErrorAction SilentlyContinue) {
    git clone $Repo $App
} else {
    $zip = Join-Path $env:TEMP 'cheetah.zip'
    Invoke-WebRequest "$Repo/archive/refs/heads/main.zip" -OutFile $zip
    $tmp = Join-Path $env:TEMP 'cheetah-unzip'
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    Expand-Archive $zip $tmp
    New-Item -ItemType Directory -Force -Path $App | Out-Null
    Copy-Item "$tmp\Cheetah-Accounting-main\*" $App -Recurse -Force
}

Write-Host '3/5 Requirements (a few minutes the first time)'
uv --directory $App sync

Write-Host '4/5 Connect to Claude Desktop and build the skills'
uv --directory $App run cheetah setup-claude
uv --directory $App run cheetah build-skills

Write-Host '5/5 Document-reading models (about 500 MB, once)'
uv --directory $App run cheetah warm
uv --directory $App run cheetah doctor

Write-Host ''
Write-Host 'Done. Next:'
Write-Host '  1. Fully quit Claude Desktop (right-click the tray icon > Quit) and open it again.'
Write-Host '  2. Settings > Capabilities: turn on code execution, then upload each zip from the folder that opens now.'
Write-Host '  3. In a new chat, type: cheetah-init'
explorer (Join-Path $App 'dist\skills')
