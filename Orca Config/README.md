# OrcaSlicer profiles

[English](README.md) | [Tiếng Việt](README.vi.md)

This directory contains the repository copies of the OrcaSlicer user profiles
for the five-tool Voron: three machine profiles, four process profiles and 15
filament profiles. JSON files are the source artifacts; this README does not
infer settings that are not present in them.

## Synchronization behavior

Double-clicking `Sync-OrcaProfiles.cmd` runs:

```powershell
Sync-OrcaProfiles.ps1 -IncludeDiagnostics -Commit -Push
```

This is the fully automated path: it selects the most recently edited Orca user
profile, validates JSON, synchronizes changed profiles, includes configured
diagnostics, writes the daily journal, creates a scoped Git commit and pushes
it.

Running the PowerShell script directly is safer for review because commit,
push and diagnostics are opt-in:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File ".\Orca Config\Sync-OrcaProfiles.ps1"
```

Useful switches:

| Switch | Code behavior |
| --- | --- |
| `-ProfileId <id>` | Select this Orca user directory instead of the most recently edited one |
| `-SkipAnalysisAliases` | Do not update the two analysis aliases under `extras/Orcasilcer setting/` |
| `-IncludeDiagnostics` | Include diagnostics selected by the script in its scoped commit set |
| `-Commit` | Stage only synchronization-owned paths and create a commit |
| `-Push` | Implies `-Commit`, then pushes the current branch |

The script reads `%APPDATA%\OrcaSlicer\user`, locates `machine`, `process` and
`filament` JSON files, parses every selected file, and rejects duplicate flat
destination names. It copies only changed files. Before replacing a changed
destination that already exists, it saves that old file under
`extras/backups/pre-orcaslicer-profile-sync-<timestamp>/`. A first-time copy has
no old destination to back up.

The optional analysis aliases are:

- `extras/Orcasilcer setting/Printersetting.json`
- `extras/Orcasilcer setting/MulticolorPETG.json`

The directory spelling is retained because it is an existing repository path.

## Profile inventory

Machine profiles:

- `Stealthchanger.json`
- `Voron Stealthchanger.json`
- `VoronStealthchanger.json`

Process profiles:

- `0.20 Tinmory.json`
- `0.20mm ABS TPmoins.json`
- `0.20mm ABS.json`
- `0.20mm PETG Multimaterial.json`

Filament profiles:

- ABS: `ABS Tpoimns Black.json`, `ABS Tpoimns Pink.json`,
  `ABS-Pro Tinmory Black.json`
- PETG: `PETG Bambu Basic Black.json`, `PETG Bambu Basic.json`,
  `PETG Kabber Blue.json`, `PETG Noname Antums.json`,
  `PETG Tinmory Black.json`, `PETG Tinmory.json`,
  `PETG TPoimns Black.json`, `PETG TPoimns Gray.json`,
  `PETG TPoimns Orange.json`, `PETG TPoimns Red.json`,
  `PETG TPoimns White.json`, `PETG TPoimns Yellow.json`

## Restore to OrcaSlicer

Orca user profiles normally live at:

```text
%APPDATA%\OrcaSlicer\user\<profile-id>\
```

Close OrcaSlicer before restoring files. Copy machine JSON to `machine`,
process JSON to `process`, and filament JSON to `filament` under the intended
profile ID. Do not choose the first directory blindly when several Orca
accounts exist; identify the same profile ID recorded by the sync script.

Example for one known profile directory:

```powershell
$profile = Join-Path $env:APPDATA 'OrcaSlicer\user\<profile-id>'
Copy-Item '.\Orca Config\Voron Stealthchanger.json' `
  (Join-Path $profile 'machine')
Copy-Item '.\Orca Config\0.20mm PETG Multimaterial.json' `
  (Join-Path $profile 'process')
Copy-Item '.\Orca Config\PETG Bambu Basic.json' `
  (Join-Path $profile 'filament')
```

Open OrcaSlicer and verify the selected printer, process, filament mapping and
tool count before slicing a production job.
