; PersonaLock Setup — NSIS installer (Janice edition)
; Requires: NSIS 3.x — https://nsis.sourceforge.io/
; Build: .\scripts\build_setup.ps1
; Output: release/PersonaLock_Setup.exe

!ifndef REPO_ROOT
  !define REPO_ROOT ".."
!endif

!define APP_NAME "PersonaLock"
!define APP_VERSION "0.1.0"
!define APP_PUBLISHER "AI Integration and Consulting LLC"
!define APP_EXE "PersonaLock.exe"

Name "${APP_NAME}"
OutFile "${REPO_ROOT}\release\PersonaLock_Setup.exe"
InstallDir "$LOCALAPPDATA\${APP_NAME}"
RequestExecutionLevel user

Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  ; Copy PyInstaller output (dist/PersonaLock/*)
  File /r "${REPO_ROOT}\dist\PersonaLock\*"

  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\Sam.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$DESKTOP\Sam.lnk" "$INSTDIR\${APP_EXE}"

  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\Sam.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Sam.lnk"
  RMDir /r "$INSTDIR"
  RMDir "$SMPROGRAMS\${APP_NAME}"
SectionEnd
