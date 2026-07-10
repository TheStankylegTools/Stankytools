Unicode True

!include "MUI2.nsh"

!ifndef APP_VERSION
    !define APP_VERSION "dev"
!endif

!ifndef DIST_DIR
    !error "DIST_DIR was not provided by build_release.ps1."
!endif

!ifndef OUTPUT_DIR
    !error "OUTPUT_DIR was not provided by build_release.ps1."
!endif

!ifndef APP_EXE_REL
    !error "APP_EXE_REL was not provided by build_release.ps1."
!endif

!define APP_NAME "StankyTools"
!define COMPANY_NAME "TheStankylegTools"

Name "${APP_NAME}"
OutFile "${OUTPUT_DIR}\StankyTools-Setup-v${APP_VERSION}.exe"

InstallDir "$LOCALAPPDATA\Programs\${APP_NAME}"
InstallDirRegKey HKCU \
    "Software\${COMPANY_NAME}\${APP_NAME}" \
    "InstallLocation"

RequestExecutionLevel user

SetCompressor /SOLID lzma
SetCompressorDictSize 64

VIProductVersion "0.0.0.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${COMPANY_NAME}"
VIAddVersionKey "FileDescription" "${APP_NAME} Windows Installer"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"

!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install StankyTools" SEC_MAIN
    SetOutPath "$INSTDIR"

    ; DIST_DIR is an absolute path supplied by build_release.ps1.
    File /r "${DIST_DIR}\*.*"

    IfFileExists "$INSTDIR\${APP_EXE_REL}" AppFound 0

    MessageBox MB_ICONSTOP \
        "The application executable was not found after installation.$\r$\n$\r$\nExpected:$\r$\n$INSTDIR\${APP_EXE_REL}"

    Abort

    AppFound:

    WriteUninstaller "$INSTDIR\Uninstall.exe"

    WriteRegStr HKCU \
        "Software\${COMPANY_NAME}\${APP_NAME}" \
        "InstallLocation" \
        "$INSTDIR"

    WriteRegStr HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "DisplayName" \
        "${APP_NAME}"

    WriteRegStr HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "DisplayVersion" \
        "${APP_VERSION}"

    WriteRegStr HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "Publisher" \
        "${COMPANY_NAME}"

    WriteRegStr HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "InstallLocation" \
        "$INSTDIR"

    WriteRegStr HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "DisplayIcon" \
        "$INSTDIR\${APP_EXE_REL}"

    WriteRegStr HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "UninstallString" \
        '"$INSTDIR\Uninstall.exe"'

    CreateDirectory "$SMPROGRAMS\${APP_NAME}"

    CreateShortcut \
        "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
        "$INSTDIR\${APP_EXE_REL}"

    CreateShortcut \
        "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk" \
        "$INSTDIR\Uninstall.exe"

    CreateShortcut \
        "$DESKTOP\${APP_NAME}.lnk" \
        "$INSTDIR\${APP_EXE_REL}"
SectionEnd

Section "Uninstall"
    Delete "$DESKTOP\${APP_NAME}.lnk"

    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Uninstall ${APP_NAME}.lnk"

    RMDir "$SMPROGRAMS\${APP_NAME}"
    RMDir /r "$INSTDIR"

    DeleteRegKey HKCU \
        "Software\${COMPANY_NAME}\${APP_NAME}"

    DeleteRegKey HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
SectionEnd