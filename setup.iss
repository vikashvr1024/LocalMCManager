[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
AppName=Local MC Manager
AppVersion=1.0.0
AppPublisher=Vikash
AppPublisherURL=https://github.com/vikashvr1024/LocalMCManager
AppSupportURL=https://github.com/vikashvr1024/LocalMCManager
AppUpdatesURL=https://github.com/vikashvr1024/LocalMCManager
DefaultDirName={autopf}\Local MC Manager
DisableDirPage=no
DisableProgramGroupPage=no
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=LocalMCManagerSetup
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\LocalMCManager.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; The main executable from PyInstaller
Source: "dist\LocalMCManager.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include the assets folder if your app needs it at runtime (if not bundled in onefile, but PyInstaller onefile includes them internally usually. 
; If you used --onefile, you mainly need the EXE. If you externalized them, include them here.)
; Since we used --add-data in PyInstaller --onefile mode, the assets are INSIDE the EXE. 
; We still might want the icon for the uninstaller/shortcuts if needed externally, but usually EXE is enough.

[Icons]
Name: "{autoprograms}\Local MC Manager"; Filename: "{app}\LocalMCManager.exe"
Name: "{autodesktop}\Local MC Manager"; Filename: "{app}\LocalMCManager.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\LocalMCManager.exe"; Description: "{cm:LaunchProgram,Local MC Manager}"; Flags: nowait postinstall skipifsilent
