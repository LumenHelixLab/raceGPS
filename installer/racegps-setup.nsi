; raceGPS Windows Installer
; NSIS Script — packages a UE5 BuildCookRun archive with a standard MUI flow.
; Requires: NSIS 3.x (stock plugins only)
;
; Layout contract: the payload dir (apps\unreal-akron-beta\Build\Windows) is
; installed verbatim under $INSTDIR. The runnable exe is the UE bootstrap at
; $INSTDIR\${GAME_EXE_REL} (default: Windows\raceGPSAkronBeta.exe).
; build-windows-installer.ps1 detects the real exe and passes /DGAME_EXE_REL.

!ifndef PRODUCT_VERSION
    !define PRODUCT_VERSION "0.2.0"
!endif
!ifndef GAME_EXE_REL
    !define GAME_EXE_REL "Windows\raceGPSAkronBeta.exe"
!endif
!ifndef PAYLOAD_REL
    ; Path to the UE5 archive root, relative to this script. build-windows-installer.ps1
    ; overrides this when packaging a timestamped build.py archive.
    !define PAYLOAD_REL "..\apps\unreal-akron-beta\Build\Windows"
!endif

!define PRODUCT_NAME "raceGPS"
!define PRODUCT_PUBLISHER "LumenHelix Solutions"
!define PRODUCT_WEB_SITE "https://github.com/LumenHelixLab/raceGPS"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\raceGPS.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 2
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!include "WinVer.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Finish page: offer to launch the game (must be defined BEFORE page macros).
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_FINISHPAGE_RUN "$INSTDIR\${GAME_EXE_REL}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch raceGPS"

; Pages - standard MUI only, no custom pages (crash-safe).
; Payload validation lives in scripts\build-windows-installer.ps1.
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Installer metadata
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "raceGPS-v${PRODUCT_VERSION}-Win64-Setup.exe"
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show
RequestExecutionLevel admin

; Version info embedded in the setup exe (Explorer properties, SmartScreen)
VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME} Installer"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "LegalCopyright" "Copyright ${PRODUCT_PUBLISHER}"

; ============================================================
; GUARDS
; ============================================================
Function .onInit
    ${IfNot} ${RunningX64}
        MessageBox MB_ICONSTOP "raceGPS requires a 64-bit version of Windows."
        Abort
    ${EndIf}
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_ICONSTOP "raceGPS requires Windows 10 or later."
        Abort
    ${EndIf}
FunctionEnd

; ============================================================
; COMPONENTS
; ============================================================
Section "Game Files" SEC_GAME
    SectionIn RO
    SetOutPath "$INSTDIR"
    ; UE5 packaged payload (Windows\raceGPSAkronBeta.exe + content). No /nonfatal:
    ; a missing payload must fail the compile, not ship an empty install.
    File /r "${PAYLOAD_REL}\*.*"

    ; Runtime data the importer resolves via ../../citypacks and ../../generated
    ; from $INSTDIR\Windows\raceGPSAkronBeta\ (packaged ProjectDir).
    SetOutPath "$INSTDIR\citypacks"
    File /r "..\citypacks\*.*"
    SetOutPath "$INSTDIR\generated"
    File /nonfatal "..\generated\*_LevelSpec.json"
SectionEnd

Section "Visual C++ Redistributables" SEC_VCREDIST
    DetailPrint "Installing VC++ 2015-2022 Redistributables..."
    SetOutPath "$TEMP"
    NSISdl::download "https://aka.ms/vs/17/release/vc_redist.x64.exe" "$TEMP\vc_redist.x64.exe"
    Pop $R0
    ${If} $R0 == "success"
        ExecWait '"$TEMP\vc_redist.x64.exe" /install /quiet /norestart' $R1
        ${If} $R1 != 0
            DetailPrint "WARNING: VC++ Redist installer exited with code $R1. Game may not run."
        ${EndIf}
    ${Else}
        DetailPrint "WARNING: VC++ Redist download failed ($R0). Install vc_redist.x64 manually if the game fails to start."
    ${EndIf}
SectionEnd

Section "Desktop Shortcut" SEC_SHORTCUT
    CreateShortcut "$DESKTOP\raceGPS.lnk" "$INSTDIR\${GAME_EXE_REL}" "" "$INSTDIR\${GAME_EXE_REL}" 0
SectionEnd

Section "Start Menu Shortcuts" SEC_STARTMENU
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\Play raceGPS.lnk" "$INSTDIR\${GAME_EXE_REL}"
    CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

; ============================================================
; POST-INSTALL
; ============================================================
Section -Post
    WriteUninstaller "$INSTDIR\uninst.exe"
    WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\${GAME_EXE_REL}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${GAME_EXE_REL}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
    WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "NoModify" 1
    WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "NoRepair" 1
SectionEnd

; ============================================================
; UNINSTALLER
; ============================================================
Section Uninstall
    Delete "$INSTDIR\uninst.exe"
    Delete "$DESKTOP\raceGPS.lnk"
    RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
    RMDir /r "$INSTDIR"
    DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
    DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
    SetAutoClose true
SectionEnd
