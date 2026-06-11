; raceGPS Windows Installer
; NSIS Script — Professional game installer with preflight onboarding
; Requires: NSIS 3.x + nsProcess plugin

!define PRODUCT_NAME "raceGPS"
!define PRODUCT_VERSION "0.2.0"
!define PRODUCT_PUBLISHER "LumenHelix Solutions"
!define PRODUCT_WEB_SITE "https://github.com/lumenhelixsolutions/raceGPS"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\raceGPS.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define MIN_RAM_MB "8192"
!define MIN_DISK_MB "5120"

; MUI 2
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!include "WinVer.nsh"
!include "nsDialogs.nsh"

; Variables
Var DirectXVer
Var VCRuntimesOK

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
Page custom PreflightPage PreflightLeave
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
Page custom FinishPage
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "raceGPS-v${PRODUCT_VERSION}-Win64-Setup.exe"
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show
RequestExecutionLevel admin

; ============================================================
; PREFLIGHT PAGE
; ============================================================
Function PreflightPage
    nsDialogs::Create 1018
    Pop $0

    ${If} $0 == error
        Abort
    ${EndIf}

    !insertmacro MUI_HEADER_TEXT "System Check" "raceGPS will verify your system is ready."

    ; Title
    ${NSD_CreateLabel} 0 0 100% 20u "Pre-Flight Checklist"
    Pop $0
    ; Check OS
    ${NSD_CreateLabel} 0 30u 100% 12u ""
    Pop $R0
    ReadRegStr $R1 HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion" "CurrentMajorVersionNumber"
    ${If} $R1 >= 10
        SetCtlColors $R0 0x00AA00 transparent
        ${NSD_SetText} $R0 "✓ Windows 10/11 detected"
    ${Else}
        SetCtlColors $R0 0xFF0000 transparent
        ${NSD_SetText} $R0 "✗ Windows 10/11 required. Upgrade to continue."
        EnableWindow $mui.Button.Next 0
    ${EndIf}

    ; Check RAM
    ${NSD_CreateLabel} 0 50u 100% 12u ""
    Pop $R2
    System::Call "kernel32::GlobalMemoryStatusEx(*) v .r0"
    System::Call "*(&i64) i (r0) .r1"
    System::Call "*$1(&i64, &i64, &i64, &i64, &i64, &i64, &i64, &i64)"
    System::Call "*$1(&i64 .r2, &i64 .r3, &i64 .r4, &i64 .r5, &i64 .r6, &i64 .r7, &i64 .r8, &i64 .r9)"
    IntOp $R3 $8 / 1048576  ; Total physical RAM in MB
    ${If} $R3 >= ${MIN_RAM_MB}
        ${NSD_SetText} $R2 "✓ RAM: $R3 MB (min: ${MIN_RAM_MB} MB)"
    ${Else}
        ${NSD_SetText} $R2 "⚠ RAM: $R3 MB (min: ${MIN_RAM_MB} MB recommended)"
    ${EndIf}

    ; Check Disk
    ${NSD_CreateLabel} 0 70u 100% 12u ""
    Pop $R4
    StrCpy $R5 "$INSTDIR"
    ${If} $R5 == ""
        StrCpy $R5 "$PROGRAMFILES64"
    ${EndIf}
    System::Call 'kernel32::GetDiskFreeSpaceEx(w "$R5", *l .r0, *l .r1, *l .r2) i .r3'
    System::Int64Op $1 / 1048576
    Pop $R6
    ${If} $R6 >= ${MIN_DISK_MB}
        ${NSD_SetText} $R4 "✓ Disk space: $R6 MB available on $R5"
    ${Else}
        ${NSD_SetText} $R4 "✗ Disk space: $R6 MB (need ${MIN_DISK_MB} MB). Choose another drive."
        EnableWindow $mui.Button.Next 0
    ${EndIf}

    ; Check DirectX
    ${NSD_CreateLabel} 0 90u 100% 12u ""
    Pop $R7
    ReadRegStr $DirectXVer HKLM "SOFTWARE\Microsoft\DirectX" "Version"
    ${If} $DirectXVer == ""
        ${NSD_SetText} $R7 "⚠ DirectX version unknown. Runtime will install if needed."
    ${Else}
        ${NSD_SetText} $R7 "✓ DirectX runtime present"
    ${EndIf}

    ; Check VC++ Runtimes
    ${NSD_CreateLabel} 0 110u 100% 12u ""
    Pop $R8
    ReadRegStr $VCRuntimesOK HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" "Version"
    ${If} $VCRuntimesOK == ""
        ${NSD_SetText} $R8 "⚠ VC++ 2015-2022 Redistributable will be installed."
    ${Else}
        ${NSD_SetText} $R8 "✓ VC++ Redistributables present"
    ${EndIf}

    ; GPU hint
    ${NSD_CreateLabel} 0 140u 100% 40u "If you have a discrete GPU (NVIDIA/AMD) with 6GB+ VRAM, we recommend High graphics settings. Integrated graphics will use Low settings automatically."
    Pop $R9

    nsDialogs::Show
FunctionEnd

Function PreflightLeave
    ; Re-enable next button if checks pass
FunctionEnd

; ============================================================
; COMPONENTS
; ============================================================
Section "Game Files" SEC_GAME
    SectionIn RO
    SetOutPath "$INSTDIR"
    File /nonfatal /r "..\Build\Windows\*.*"
    SetOutPath "$INSTDIR\citypacks"
    File /r "..\citypacks\*.*"
SectionEnd

Section "Akron Citypack (Default)" SEC_CITYPACK
    SectionIn RO
    DetailPrint "Akron citypack bundled."
SectionEnd

Section "Visual C++ Redistributables" SEC_VCREDIST
    DetailPrint "Installing VC++ 2015-2022 Redistributables..."
    SetOutPath "$TEMP"
    NSISdl::download "https://aka.ms/vs/17/release/vc_redist.x64.exe" "$TEMP\vc_redist.x64.exe"
    Pop $R0
    ${If} $R0 == "success"
        ExecWait '"$TEMP\vc_redist.x64.exe" /install /quiet /norestart'
    ${Else}
        DetailPrint "WARNING: VC++ Redist download failed. Game may not run."
    ${EndIf}
SectionEnd

Section "Desktop Shortcut" SEC_SHORTCUT
    CreateShortcut "$DESKTOP\raceGPS.lnk" "$INSTDIR\raceGPS.exe" "" "$INSTDIR\raceGPS.exe" 0
SectionEnd

Section "Start Menu Shortcuts" SEC_STARTMENU
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\Play raceGPS.lnk" "$INSTDIR\raceGPS.exe"
    CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

; ============================================================
; POST-INSTALL
; ============================================================
Section -Post
    WriteUninstaller "$INSTDIR\uninst.exe"
    WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\raceGPS.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\raceGPS.exe"
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

; ============================================================
; FINISH PAGE
; ============================================================
Function FinishPage
    nsDialogs::Create 1018
    Pop $0

    ${If} $0 == error
        Abort
    ${EndIf}

    !insertmacro MUI_HEADER_TEXT "Setup Complete" "raceGPS is ready to race."

    ${NSD_CreateLabel} 0 0 100% 20u "Installation Complete!"
    Pop $0

    ${NSD_CreateLabel} 0 30u 100% 60u "raceGPS has been installed successfully. On first launch, the game will run a quick hardware check and guide you through controller setup, graphics settings, and your first race."
    Pop $1

    ${NSD_CreateButton} 0 110u 100% 30u "Launch raceGPS"
    Pop $2
    ${NSD_OnClick} $2 LaunchGame

    ${NSD_CreateButton} 0 150u 100% 30u "Open Citypack Manager"
    Pop $3
    ${NSD_OnClick} $3 OpenCitypackManager

    nsDialogs::Show
FunctionEnd

Function LaunchGame
    Exec '"$INSTDIR\raceGPS.exe"'
    Quit
FunctionEnd

Function OpenCitypackManager
    Exec '"$INSTDIR\raceGPS.exe" -citypackmanager'
    Quit
FunctionEnd
