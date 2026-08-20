param (
    [Parameter(Mandatory=$false)]
    [string]$File,

    [Parameter(Mandatory=$false)]
    [switch]$All
)

$OutputDir = "docs\presentations"
$AuxDir = "docs\presentations\build"

# Ensure directories exist
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null }
if (-not (Test-Path $AuxDir)) { New-Item -ItemType Directory -Force -Path $AuxDir | Out-Null }

function Compile-Tex {
    param([string]$FilePath)
    
    $FileName = Split-Path $FilePath -Leaf
    Write-Host "Compiling $FileName..." -ForegroundColor Cyan
    
    # Run xelatex with aux-directory to prevent root pollution
    xelatex -output-directory=$OutputDir -aux-directory=$AuxDir -interaction=nonstopmode $FilePath | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  -> Success!" -ForegroundColor Green
    } else {
        Write-Host "  -> Warning: Compilation returned non-zero exit code. Check logs in $AuxDir." -ForegroundColor Yellow
    }
}

if ($All) {
    Write-Host "Compiling all .tex files in $OutputDir..."
    $Files = Get-ChildItem -Path $OutputDir -Filter "*.tex"
    foreach ($f in $Files) {
        Compile-Tex -FilePath $f.FullName
    }
} elseif ($File) {
    Compile-Tex -FilePath $File
} else {
    Write-Host "Usage: .\build_slides.ps1 -File docs\presentations\00-why-build-this.tex"
    Write-Host "   or: .\build_slides.ps1 -All"
    exit 1
}

Write-Host "Done. Temporary files are isolated in $AuxDir." -ForegroundColor Magenta
