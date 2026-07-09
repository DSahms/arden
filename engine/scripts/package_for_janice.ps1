# Package PersonaLock for Janice — no NSIS required
# Run after: python -m PyInstaller packaging/personalock.spec --noconfirm
# Output: release/PersonaLock-Portable.zip + release/Install-Sam.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$dist = Join-Path $Root "dist\PersonaLock"
if (-not (Test-Path (Join-Path $dist "PersonaLock.exe"))) {
    Write-Host "Build first: .\scripts\build_consumer.ps1" -ForegroundColor Red
    exit 1
}

$release = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $release | Out-Null

# Desktop shortcut installer script (Janice double-clicks this)
$installScript = @'
# PersonaLock Install - for Janice
$dest = Join-Path $env:LOCALAPPDATA "PersonaLock\App"
$src = $PSScriptRoot
$skip = @(
    "Install-Sam.ps1", "Uninstall-Sam.ps1",
    "README-FOR-JANICE.txt", "EMAIL-TO-JANICE.txt", "DAVE-QUICK-TEST.txt"
)
Write-Host "Installing Sam to $dest ..."
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Get-ChildItem $src | Where-Object { $skip -notcontains $_.Name } | Copy-Item -Destination $dest -Recurse -Force
$wsh = New-Object -ComObject WScript.Shell
$desktop = $wsh.SpecialFolders("Desktop")
if (-not $desktop) {
    $desktop = [Environment]::GetFolderPath("Desktop")
}
$lnk = Join-Path $desktop "Sam.lnk"
$shortcut = $wsh.CreateShortcut($lnk)
$shortcut.TargetPath = Join-Path $dest "PersonaLock.exe"
$shortcut.WorkingDirectory = $dest
$shortcut.Description = "PersonaLock - Sam"
$shortcut.Save()
Write-Host ""
Write-Host "Done! Shortcut: $lnk" -ForegroundColor Green
Write-Host "Or run: $(Join-Path $dest 'PersonaLock.exe')"
Write-Host "First run: free Groq API key at https://console.groq.com"
Read-Host "Press Enter to close"
'@
$installScript | Out-File -FilePath (Join-Path $release "Install-Sam.ps1") -Encoding ascii

$uninstallScript = @'
# PersonaLock Uninstall - removes Sam shortcut and app files
$dest = Join-Path $env:LOCALAPPDATA "PersonaLock\App"
$wsh = New-Object -ComObject WScript.Shell
$desktop = $wsh.SpecialFolders("Desktop")
if (-not $desktop) { $desktop = [Environment]::GetFolderPath("Desktop") }
$lnk = Join-Path $desktop "Sam.lnk"
if (Test-Path $lnk) { Remove-Item $lnk -Force }
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Write-Host "Sam removed. Your memories in %LOCALAPPDATA%\PersonaLock\ are kept unless you delete that folder."
Read-Host "Press Enter to close"
'@
$uninstallScript | Out-File -FilePath (Join-Path $release "Uninstall-Sam.ps1") -Encoding ascii
Copy-Item (Join-Path $Root "release\README-FOR-JANICE.txt") (Join-Path $dist "README-FOR-JANICE.txt") -Force
# Include installer scripts INSIDE the zip (Janice gets one file to unzip)
Copy-Item (Join-Path $release "Install-Sam.ps1") (Join-Path $dist "Install-Sam.ps1") -Force
Copy-Item (Join-Path $release "Uninstall-Sam.ps1") (Join-Path $dist "Uninstall-Sam.ps1") -Force

$zipPath = Join-Path $release "PersonaLock-Portable.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path $dist "*") -DestinationPath $zipPath -Force

Write-Host ""
Write-Host "Release ready:" -ForegroundColor Green
Write-Host "  $zipPath"
Write-Host "  $(Join-Path $release 'Install-Sam.ps1')"
Write-Host ""
Write-Host "For Janice: unzip, run Install-Sam.ps1, click desktop Sam icon." -ForegroundColor Yellow
