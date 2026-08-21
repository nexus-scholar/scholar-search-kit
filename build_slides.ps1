param (
    [Parameter(Mandatory=$false, Position=0)]
    [string]$File,

    [Parameter(Mandatory=$false)]
    [switch]$All,

    [Parameter(Mandatory=$false)]
    [switch]$Clean,

    [Parameter(Mandatory=$false)]
    [ValidateSet("pdflatex", "xelatex")]
    [string]$Engine = "pdflatex"
)

$RootDir = $PSScriptRoot
$PresDir = Join-Path $RootDir "docs\presentations"
$PdfDir  = Join-Path $PresDir "pdf"
$AuxDir  = Join-Path $PresDir "build"

# Ensure clean directory structure
if (-not (Test-Path $PdfDir)) { New-Item -ItemType Directory -Force -Path $PdfDir | Out-Null }
if (-not (Test-Path $AuxDir)) { New-Item -ItemType Directory -Force -Path $AuxDir | Out-Null }

if ($Clean) {
    Write-Host "[NEXUS] Cleaning auxiliary build artifacts..." -ForegroundColor Yellow
    Get-ChildItem -Path $AuxDir -Recurse -File | Remove-Item -Force
    Write-Host "[NEXUS] Clean complete." -ForegroundColor Green
    if (-not $File -and -not $All) { exit 0 }
}

function Build-Deck {
    param(
        [string]$Path,
        [int]$Current = 1,
        [int]$Total = 1
    )

    $FileName = Split-Path $Path -Leaf
    $BaseName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
    
    Write-Host "[$Current/$Total] Compiling $FileName ($Engine)..." -ForegroundColor Cyan -NoNewline

    $Sw = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Run compiler with output and aux directory parameters
    $Process = Start-Process -FilePath $Engine `
        -ArgumentList "-output-directory=`"$AuxDir`"", "-aux-directory=`"$AuxDir`"", "-interaction=nonstopmode", "`"$Path`"" `
        -WorkingDirectory $PresDir `
        -NoNewWindow -PassThru -Wait

    $Sw.Stop()
    $Elapsed = "{0:N1}s" -f $Sw.Elapsed.TotalSeconds

    $GeneratedPdf = Join-Path $AuxDir "$BaseName.pdf"
    $TargetPdf    = Join-Path $PdfDir "$BaseName.pdf"

    if (Test-Path $GeneratedPdf) {
        Copy-Item -Path $GeneratedPdf -Destination $TargetPdf -Force
        Write-Host " -> OK ($Elapsed) -> pdf\$BaseName.pdf" -ForegroundColor Green
    } else {
        Write-Host " -> FAILED ($Elapsed)" -ForegroundColor Red
        Write-Host "       Check log: $AuxDir\$BaseName.log" -ForegroundColor DarkGray
    }
}

Write-Host "==========================================================" -ForegroundColor DarkCyan
Write-Host "  NEXUS SCHOLAR SUITE - PRESENTATION COMPILER PIPELINE   " -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor DarkCyan
Write-Host "  Engine     : $Engine" -ForegroundColor Gray
Write-Host "  PDF Output : $PdfDir" -ForegroundColor Gray
Write-Host "  Build Aux  : $AuxDir" -ForegroundColor Gray
Write-Host "----------------------------------------------------------" -ForegroundColor DarkCyan

if ($All) {
    $TexFiles = Get-ChildItem -Path $PresDir -Filter "*.tex" | Sort-Object Name
    $Total = $TexFiles.Count
    $Index = 1

    Write-Host "Found $Total presentation decks to compile.`n" -ForegroundColor White

    foreach ($TexFile in $TexFiles) {
        Build-Deck -Path $TexFile.FullName -Current $Index -Total $Total
        $Index++
    }
} elseif ($File) {
    if (-not (Test-Path $File)) {
        # Check relative to PresDir
        $Candidate = Join-Path $PresDir $File
        if (Test-Path $Candidate) { $File = $Candidate }
        elseif (Test-Path "$Candidate.tex") { $File = "$Candidate.tex" }
    }

    if (-not (Test-Path $File)) {
        Write-Host "Error: Could not find presentation file: $File" -ForegroundColor Red
        exit 1
    }

    Build-Deck -Path (Resolve-Path $File).Path -Current 1 -Total 1
} else {
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  .\build_slides.ps1 -All                    # Compile all decks"
    Write-Host "  .\build_slides.ps1 -File 03-persistent-identifiers.tex"
    Write-Host "  .\build_slides.ps1 -Clean                  # Clean aux files"
    exit 0
}

Write-Host "----------------------------------------------------------" -ForegroundColor DarkCyan
Write-Host "[NEXUS] Build complete. Output saved to docs/presentations/pdf/" -ForegroundColor Magenta
