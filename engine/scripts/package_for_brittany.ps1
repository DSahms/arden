# Package Arden Desktop for Brittany — unzip + Install-Arden.ps1
# Run after: .\scripts\build_arden_consumer.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$dist = Join-Path $Root "dist\Arden"
if (-not (Test-Path (Join-Path $dist "Arden.exe"))) {
    Write-Host "Build first: .\scripts\build_arden_consumer.ps1" -ForegroundColor Red
    exit 1
}

$release = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $release | Out-Null

$installScript = @'
# Arden Desktop Install — for Brittany
$dest = Join-Path $env:LOCALAPPDATA "Arden\App"
$src = $PSScriptRoot
$skip = @(
    "Install-Arden.ps1", "Uninstall-Arden.ps1",
    "README-FOR-BRITTANY.txt", "EMAIL-TO-BRITTANY.txt",
    "THIRD_PARTY_NOTICES.txt", "DAVE-QUICK-TEST.txt"
)
Write-Host "Installing Arden Desktop to $dest ..."
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Get-ChildItem $src | Where-Object { $skip -notcontains $_.Name } | Copy-Item -Destination $dest -Recurse -Force
$wsh = New-Object -ComObject WScript.Shell
$desktop = $wsh.SpecialFolders("Desktop")
if (-not $desktop) {
    $desktop = [Environment]::GetFolderPath("Desktop")
}
$lnk = Join-Path $desktop "Arden.lnk"
$shortcut = $wsh.CreateShortcut($lnk)
$shortcut.TargetPath = Join-Path $dest "Arden.exe"
$shortcut.WorkingDirectory = $dest
$shortcut.Description = "Arden Desktop — Powered by Rémanence"
$shortcut.Save()
Write-Host ""
Write-Host "Done! Desktop shortcut: $lnk" -ForegroundColor Green
Write-Host "Or run: $(Join-Path $dest 'Arden.exe')"
Write-Host ""
Write-Host "First run: Venice API key (venice.ai) or free Groq backup (console.groq.com)"
Read-Host "Press Enter to close"
'@
$installScript | Out-File -FilePath (Join-Path $release "Install-Arden.ps1") -Encoding ascii

$uninstallScript = @'
# Arden Desktop Uninstall
$dest = Join-Path $env:LOCALAPPDATA "Arden\App"
$wsh = New-Object -ComObject WScript.Shell
$desktop = $wsh.SpecialFolders("Desktop")
if (-not $desktop) { $desktop = [Environment]::GetFolderPath("Desktop") }
$lnk = Join-Path $desktop "Arden.lnk"
if (Test-Path $lnk) { Remove-Item $lnk -Force }
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Write-Host "Arden app removed. Memories in %LOCALAPPDATA%\Arden\ are kept unless you delete that folder."
Read-Host "Press Enter to close"
'@
$uninstallScript | Out-File -FilePath (Join-Path $release "Uninstall-Arden.ps1") -Encoding ascii

$readme = @'
ARDEN DESKTOP — README FOR BRITTANY
===================================

Powered by Rémanence

WHAT YOU GET
- Arden — personal companion (forest-green window)
- Chat · Sources (your PDFs) · Help me know you · Tools
- Saved sessions · What I know about you · local memory on your PC
- Venice Cloud (recommended) or Groq backup · optional Local Kobold

INSTALL (5 minutes)
1. Unzip Arden-Portable.zip to a folder (e.g. Downloads\Arden)
2. Double-click Install-Arden.ps1
3. Click the "Arden" shortcut on your desktop
4. First run: name your assistant (default Arden), your name, paste API key

VENICE KEY (recommended)
- Sign up at https://venice.ai
- Paste key when prompted (or use free Groq at console.groq.com)

UNINSTALL
- Run Uninstall-Arden.ps1 from the zip folder
- To wipe memories too: delete %LOCALAPPDATA%\Arden\

Taglines:
- All remembered. Deeply encrypted. Never leaves home.
- Where nothing is forgotten, and nothing leaves the forest.

Questions? Text Dave.
'@
$readme | Out-File -FilePath (Join-Path $release "README-FOR-BRITTANY.txt") -Encoding utf8

$notices = @'
THIRD-PARTY NOTICES — Arden Desktop
===================================

Arden Desktop is by AI Integration and Consulting LLC.
Product identity: Arden Desktop — Powered by Rémanence.

The following third-party software is used in development or optional
modules. It is NOT branded on the product face.

ChromaDB and other libraries ship inside the PyInstaller
bundle under their respective open-source licenses.
'@
$notices | Out-File -FilePath (Join-Path $release "THIRD_PARTY_NOTICES.txt") -Encoding utf8

Copy-Item (Join-Path $release "README-FOR-BRITTANY.txt") (Join-Path $dist "README-FOR-BRITTANY.txt") -Force
Copy-Item (Join-Path $release "THIRD_PARTY_NOTICES.txt") (Join-Path $dist "THIRD_PARTY_NOTICES.txt") -Force
Copy-Item (Join-Path $release "Install-Arden.ps1") (Join-Path $dist "Install-Arden.ps1") -Force
Copy-Item (Join-Path $release "Uninstall-Arden.ps1") (Join-Path $dist "Uninstall-Arden.ps1") -Force

$zipPath = Join-Path $release "Arden-Portable.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path $dist "*") -DestinationPath $zipPath -Force

Write-Host ""
Write-Host "Release ready:" -ForegroundColor Green
Write-Host "  $zipPath"
Write-Host ""
Write-Host "For Brittany: email zip + README. She unzips, runs Install-Arden.ps1." -ForegroundColor Yellow
