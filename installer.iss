#define MyVer "1.0.0"
[Setup]
AppId={{9E4C1B27-7A3D-4F58-B6E2-HDEX00000001}
AppName=HYPERION DIGITAL EX
AppVersion={#MyVer}
AppVerName=HYPERION DIGITAL EX {#MyVer}
AppPublisher=EX Inc./HYPERION DIGITAL
AppPublisherURL=https://github.com/Teobokki/hyperion-digital-ex
AppCopyright=©2026 EX Inc./HYPERION DIGITAL ©2026
VersionInfoVersion={#MyVer}.0
VersionInfoCompany=EX Inc./HYPERION DIGITAL
VersionInfoCopyright=©2026 EX Inc./HYPERION DIGITAL ©2026
VersionInfoProductName=HYPERION DIGITAL EX
VersionInfoDescription=HYPERION DIGITAL EX Setup
DefaultDirName={localappdata}\Programs\HYPERION DIGITAL EX
DefaultGroupName=HYPERION DIGITAL EX
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=HYPERION.DIGITAL.EX.Setup.{#MyVer}
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\HYPERION DIGITAL EX.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "dist\HYPERION DIGITAL EX\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\HYPERION DIGITAL EX"; Filename: "{app}\HYPERION DIGITAL EX.exe"
Name: "{group}\Uninstall HYPERION DIGITAL EX"; Filename: "{uninstallexe}"
Name: "{userdesktop}\HYPERION DIGITAL EX"; Filename: "{app}\HYPERION DIGITAL EX.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\HYPERION DIGITAL EX.exe"; Description: "Launch HYPERION DIGITAL EX now"; Flags: nowait postinstall skipifsilent
