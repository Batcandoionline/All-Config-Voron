#Requires -Version 5.1

[CmdletBinding()]
param(
    [string]$OrcaUserRoot = (Join-Path $env:APPDATA "OrcaSlicer\user"),
    [string]$ProfileId,
    [switch]$SkipAnalysisAliases,
    [switch]$IncludeDiagnostics,
    [switch]$Commit,
    [switch]$Push
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($Push) {
    $Commit = $true
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$destinationRoot = $PSScriptRoot
$analysisRoot = Join-Path $repoRoot "extras\Orcasilcer setting"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$today = Get-Date -Format "yyyy-MM-dd"

function Get-RepositoryRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $base = [System.IO.Path]::GetFullPath($repoRoot).TrimEnd("\") + "\"
    $full = [System.IO.Path]::GetFullPath($Path)
    if (-not $full.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the repository: $full"
    }

    return $full.Substring($base.Length).Replace("\", "/")
}

function Test-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    try {
        $null = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        throw "Invalid JSON file '$Path': $($_.Exception.Message)"
    }
}

function Test-SameFileContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
        return $false
    }

    $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Source).Hash
    $destinationHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash
    return $sourceHash -eq $destinationHash
}

if (-not (Test-Path -LiteralPath (Join-Path $repoRoot ".git") -PathType Container)) {
    throw "Git repository was not found at '$repoRoot'."
}

if (-not (Test-Path -LiteralPath $OrcaUserRoot -PathType Container)) {
    throw "OrcaSlicer user profile directory was not found at '$OrcaUserRoot'."
}

$profileRoot = $null
if ($ProfileId) {
    $candidate = Join-Path $OrcaUserRoot $ProfileId
    if (-not (Test-Path -LiteralPath $candidate -PathType Container)) {
        throw "Requested OrcaSlicer profile ID was not found: $ProfileId"
    }
    $profileRoot = $candidate
}
else {
    $profileCandidates = @()
    foreach ($directory in Get-ChildItem -LiteralPath $OrcaUserRoot -Directory) {
        $jsonFiles = @(
            foreach ($category in @("machine", "process", "filament")) {
                $categoryPath = Join-Path $directory.FullName $category
                if (Test-Path -LiteralPath $categoryPath -PathType Container) {
                    Get-ChildItem -LiteralPath $categoryPath -Filter "*.json" -File
                }
            }
        )

        if ($jsonFiles.Count -gt 0) {
            $profileCandidates += [pscustomobject]@{
                Path = $directory.FullName
                Id = $directory.Name
                LatestWriteTime = ($jsonFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
            }
        }
    }

    if ($profileCandidates.Count -eq 0) {
        throw "No OrcaSlicer user profile containing machine/process/filament JSON files was found."
    }

    $selectedProfile = $profileCandidates | Sort-Object LatestWriteTime -Descending | Select-Object -First 1
    $profileRoot = $selectedProfile.Path
    $ProfileId = $selectedProfile.Id
}

$sourceFiles = @()
foreach ($category in @("machine", "process", "filament")) {
    $categoryPath = Join-Path $profileRoot $category
    if (Test-Path -LiteralPath $categoryPath -PathType Container) {
        foreach ($file in Get-ChildItem -LiteralPath $categoryPath -Filter "*.json" -File | Sort-Object Name) {
            Test-JsonFile -Path $file.FullName
            $sourceFiles += [pscustomobject]@{
                Category = $category
                Source = $file.FullName
                Name = $file.Name
                Destination = Join-Path $destinationRoot $file.Name
            }
        }
    }
}

$duplicateNames = @($sourceFiles | Group-Object Name | Where-Object Count -gt 1)
if ($duplicateNames.Count -gt 0) {
    $names = ($duplicateNames.Name -join ", ")
    throw "Flat Orca Config layout cannot safely store duplicate profile names: $names"
}

$syncItems = @($sourceFiles)
if (-not $SkipAnalysisAliases) {
    $aliasDefinitions = @(
        @{
            Category = "machine"
            SourceName = "Voron Stealthchanger.json"
            Destination = Join-Path $analysisRoot "Printersetting.json"
        },
        @{
            Category = "process"
            SourceName = "0.20mm PETG Multimaterial.json"
            Destination = Join-Path $analysisRoot "MulticolorPETG.json"
        }
    )

    foreach ($alias in $aliasDefinitions) {
        $sourceItem = $sourceFiles |
            Where-Object { $_.Category -eq $alias.Category -and $_.Name -eq $alias.SourceName } |
            Select-Object -First 1

        if ($sourceItem) {
            $syncItems += [pscustomobject]@{
                Category = "analysis-alias"
                Source = $sourceItem.Source
                Name = [System.IO.Path]::GetFileName($alias.Destination)
                Destination = $alias.Destination
            }
        }
    }
}

$changedItems = @(
    $syncItems | Where-Object {
        -not (Test-SameFileContent -Source $_.Source -Destination $_.Destination)
    }
)

$backupRoot = $null
$backupRecords = @()
if ($changedItems.Count -gt 0) {
    $existingDestinations = @(
        $changedItems | Where-Object {
            Test-Path -LiteralPath $_.Destination -PathType Leaf
        }
    )

    if ($existingDestinations.Count -gt 0) {
        $backupRoot = Join-Path $repoRoot "extras\backups\pre-orcaslicer-profile-sync-$timestamp"
        foreach ($item in $existingDestinations) {
            $relativeDestination = Get-RepositoryRelativePath -Path $item.Destination
            $backupPath = Join-Path $backupRoot $relativeDestination
            $backupDirectory = Split-Path -Parent $backupPath
            $null = New-Item -ItemType Directory -Force -Path $backupDirectory
            Copy-Item -LiteralPath $item.Destination -Destination $backupPath
            $backupRecords += $relativeDestination
        }

        $backupReadme = @"
# Backup record

- **Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- **Task:** Back up repository OrcaSlicer JSON profiles before direct AppData synchronization.
- **Source profile ID:** $ProfileId
- **Files backed up:**
$(($backupRecords | Sort-Object -Unique | ForEach-Object { "  - ``$_``" }) -join [Environment]::NewLine)
- **Related journal:** ``extras/Nhat-ky-chinh-sua/$today-session-updates.md``
"@
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText(
            (Join-Path $backupRoot "README.md"),
            $backupReadme + [Environment]::NewLine,
            $utf8NoBom
        )
    }

    foreach ($item in $changedItems) {
        $destinationDirectory = Split-Path -Parent $item.Destination
        $null = New-Item -ItemType Directory -Force -Path $destinationDirectory
        Copy-Item -LiteralPath $item.Source -Destination $item.Destination -Force
        Test-JsonFile -Path $item.Destination
    }
}

$diagnosticPaths = @()
$changedDiagnosticRelativePaths = @()
if ($IncludeDiagnostics) {
    $diagnosticPaths = @(
        Get-ChildItem -LiteralPath (Join-Path $repoRoot "extras\gcode") -Filter "*.gcode" -File -ErrorAction SilentlyContinue
        Get-ChildItem -LiteralPath (Join-Path $repoRoot "extras\logs") -Filter "*.log" -File -ErrorAction SilentlyContinue
    )

    foreach ($diagnosticPath in $diagnosticPaths) {
        $relativePath = Get-RepositoryRelativePath -Path $diagnosticPath.FullName
        $status = & git -C $repoRoot status --porcelain --untracked-files=all --ignored=matching -- $relativePath
        if ($LASTEXITCODE -ne 0) {
            throw "git status failed while checking '$relativePath'."
        }
        if ($status) {
            $changedDiagnosticRelativePaths += $relativePath
        }
    }
    $changedDiagnosticRelativePaths = @($changedDiagnosticRelativePaths | Sort-Object -Unique)
}

$journalPath = Join-Path $repoRoot "extras\Nhat-ky-chinh-sua\$today-session-updates.md"
$journalWasUpdated = $false
if ($changedItems.Count -gt 0 -or $changedDiagnosticRelativePaths.Count -gt 0) {
    $journalDirectory = Split-Path -Parent $journalPath
    $null = New-Item -ItemType Directory -Force -Path $journalDirectory

    $existingJournal = ""
    if (Test-Path -LiteralPath $journalPath -PathType Leaf) {
        $existingJournal = Get-Content -Raw -LiteralPath $journalPath
    }

    $sectionNumbers = @(
        [regex]::Matches($existingJournal, "(?m)^##\s+(\d+)\.") |
            ForEach-Object { [int]$_.Groups[1].Value }
    )
    $nextSection = if ($sectionNumbers.Count -gt 0) {
        ($sectionNumbers | Measure-Object -Maximum).Maximum + 1
    }
    else {
        1
    }

    $changedRelativePaths = @(
        $changedItems |
            ForEach-Object { Get-RepositoryRelativePath -Path $_.Destination } |
            Sort-Object -Unique
    )
    $changedRelativePaths += $changedDiagnosticRelativePaths
    $changedRelativePaths = @($changedRelativePaths | Sort-Object -Unique)
    $backupDescription = if ($backupRoot) {
        Get-RepositoryRelativePath -Path $backupRoot
    }
    else {
        "No existing destination files required backup."
    }

    $journalEntry = @"

## $nextSection. Automatic OrcaSlicer profile synchronization

### Goal
Copy the active OrcaSlicer user presets directly from AppData into the repository and synchronize requested G-code/log diagnostics without manual export.

### Source
- ``$profileRoot``
- Selected profile ID: ``$ProfileId``

### Updated files
$(($changedRelativePaths | ForEach-Object { "- ``$_``" }) -join [Environment]::NewLine)

### Backup
- ``$backupDescription``

### Validation
- All source and destination JSON files passed ``ConvertFrom-Json`` validation.
- Exact source bytes were copied without reformatting.

### Result
- $($changedItems.Count) repository JSON file(s) synchronized.
- $($changedDiagnosticRelativePaths.Count) G-code/log diagnostic file(s) added or updated.
- Use ``Orca Config\Sync-OrcaProfiles.cmd`` for one-click sync, commit and push.
"@
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::AppendAllText(
        $journalPath,
        $journalEntry + [Environment]::NewLine,
        $utf8NoBom
    )
    $journalWasUpdated = $true
}

$commitPaths = @(
    $syncItems |
        ForEach-Object { Get-RepositoryRelativePath -Path $_.Destination } |
        Sort-Object -Unique
)
if ($journalWasUpdated) {
    $commitPaths += Get-RepositoryRelativePath -Path $journalPath
}

if ($IncludeDiagnostics) {
    $commitPaths += $diagnosticPaths |
        ForEach-Object { Get-RepositoryRelativePath -Path $_.FullName }
}

$commitPaths = @($commitPaths | Sort-Object -Unique)

if ($Commit -and $commitPaths.Count -gt 0) {
    $profilePaths = @(
        $syncItems |
            ForEach-Object { Get-RepositoryRelativePath -Path $_.Destination } |
            Sort-Object -Unique
    )
    if ($profilePaths.Count -gt 0) {
        & git -C $repoRoot add -- $profilePaths
        if ($LASTEXITCODE -ne 0) {
            throw "git add failed for OrcaSlicer profiles."
        }
    }

    if ($journalWasUpdated) {
        $journalRelativePath = Get-RepositoryRelativePath -Path $journalPath
        & git -C $repoRoot add -- $journalRelativePath
        if ($LASTEXITCODE -ne 0) {
            throw "git add failed for the daily journal."
        }
    }

    if ($IncludeDiagnostics) {
        $diagnosticRelativePaths = @(
            $diagnosticPaths |
                ForEach-Object { Get-RepositoryRelativePath -Path $_.FullName } |
                Sort-Object -Unique
        )
        if ($diagnosticRelativePaths.Count -gt 0) {
            & git -C $repoRoot add -f -- $diagnosticRelativePaths
            if ($LASTEXITCODE -ne 0) {
                throw "git add failed for G-code/log diagnostics."
            }
        }
    }

    $pendingChanges = & git -C $repoRoot status --porcelain -- $commitPaths
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed."
    }

    if ($pendingChanges) {
        $commitMessage = "chore: sync OrcaSlicer profiles $(Get-Date -Format "yyyy-MM-dd HH:mm")"
        & git -C $repoRoot commit --only -m $commitMessage -- $commitPaths
        if ($LASTEXITCODE -ne 0) {
            throw "git commit failed."
        }
    }
    else {
        Write-Host "No repository changes require a new commit."
    }
}

if ($Push) {
    & git -C $repoRoot push
    if ($LASTEXITCODE -ne 0) {
        throw "git push failed."
    }
}

Write-Host "OrcaSlicer profile ID: $ProfileId"
Write-Host "Source JSON files: $($sourceFiles.Count)"
Write-Host "Updated repository JSON files: $($changedItems.Count)"
if ($backupRoot) {
    Write-Host "Backup: $backupRoot"
}
