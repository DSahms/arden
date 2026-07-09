# Install Arden Consigliere shortcut on Dave's desktop (uses same App folder as consumer)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $Root "dist\Arden"
$dest = Join-Path $env:LOCALAPPDATA "Arden\App"

if (-not (Test-Path (Join-Path $dist "Arden.exe"))) {
    Write-Host "Build first: cd $Root; .\scripts\ship_brittany.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "Installing app to $dest ..."
New-Item -ItemType Directory -Force -Path $dest | Out-Null
$skip = @("Install-Arden.ps1", "Uninstall-Arden.ps1", "README-FOR-BRITTANY.txt", "EMAIL-TO-BRITTANY.txt", "THIRD_PARTY_NOTICES.txt", "DAVE-QUICK-TEST.txt")
Get-ChildItem $dist | Where-Object { $skip -notcontains $_.Name } | Copy-Item -Destination $dest -Recurse -Force

$launcher = Join-Path $dest "Arden-Consigliere.cmd"
Copy-Item (Join-Path $Root "release\Arden-Consigliere.cmd") $launcher -Force

$consigYml = Join-Path $Root "assistant_config.consigliere.yml"
if (Test-Path $consigYml) {
    Copy-Item $consigYml (Join-Path $dest "_internal\assistant_config.consigliere.yml") -Force
    Copy-Item $consigYml (Join-Path $env:LOCALAPPDATA "Arden\assistant_config.consigliere.yml") -Force
}

$wsh = New-Object -ComObject WScript.Shell
$desktop = $wsh.SpecialFolders("Desktop")
if (-not $desktop) { $desktop = [Environment]::GetFolderPath("Desktop") }

$lnk = Join-Path $desktop "Arden Consigliere.lnk"
$shortcut = $wsh.CreateShortcut($lnk)
$shortcut.TargetPath = $launcher
$shortcut.WorkingDirectory = $dest
$shortcut.Description = "Arden Consigliere - Powered by Remanence"
$shortcut.Save()

Write-Host ""
Write-Host "Done! Double-click: Arden Consigliere (on your Desktop)" -ForegroundColor Green
Write-Host "App folder: $dest"
