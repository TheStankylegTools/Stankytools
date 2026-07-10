!define APP_NAME "StankyTools"
!ifndef VERSION
!define VERSION "dev"
!endif
!define OUT_DIR "release_artifacts"

Name "${APP_NAME}"
OutFile "${OUT_DIR}\StankyTools-Setup-${VERSION}.exe"
InstallDir "$LOCALAPPDATA\${APP_NAME}"
RequestExecutionLevel user
ShowInstDetails nevershow
ShowUninstDetails nevershow

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\StankyTools\*"
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\StankyTools.exe"
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\StankyTools.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  RMDir /r "$INSTDIR"
SectionEnd
