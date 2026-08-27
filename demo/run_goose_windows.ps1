[CmdletBinding()]
param(
    [string]$GoosePath = "$env:LOCALAPPDATA\Goose\bin\goose.exe",
    [string]$UvPath = "$env:LOCALAPPDATA\Goose\bin\uv.exe",
    [string]$DataDir = (Join-Path $PSScriptRoot ".demo-data")
)

$ErrorActionPreference = "Stop"
$repository = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$promptPath = Join-Path $PSScriptRoot "berd-prompt.md"

foreach ($requiredPath in @($GoosePath, $UvPath, $promptPath)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required path not found: $requiredPath"
    }
}

$runStamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runDataDir = Join-Path $DataDir $runStamp
New-Item -ItemType Directory -Force -Path $runDataDir | Out-Null

$extension = 'OPEN_JOBSITE_DATA_DIR="{0}" "{1}" run --directory "{2}" open-jobsite' -f $runDataDir, $UvPath, $repository
$prompt = (Get-Content -LiteralPath $promptPath -Raw).Replace(
    "berd-wall-demo-001",
    "berd-wall-demo-$runStamp"
)

& $GoosePath run `
    --no-profile `
    --no-session `
    --max-turns 20 `
    --output-format json `
    --with-extension $extension `
    --text $prompt

exit $LASTEXITCODE
