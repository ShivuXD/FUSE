$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$target = Join-Path $root 'demo/vulnerable-device'
$output = Join-Path $root '.fuse-demo-results'
$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = (Join-Path $root 'src') + [IO.Path]::PathSeparator + $previousPythonPath
    $flags = @('--profile', 'esp-idf', '--no-network', '--no-sbom', '--no-vulnerabilities', '--no-firmware', '--no-git-history')
    & py -m vigil_fuse scan $target --plan @flags
    if ($LASTEXITCODE -ne 0) { throw "Plan failed with exit code $LASTEXITCODE" }
    & py -m vigil_fuse scan $target --output-dir $output @flags
    if ($LASTEXITCODE -ne 0) { throw "Scan failed with exit code $LASTEXITCODE" }
    'findings.txt', 'findings.json', 'findings.sarif' | ForEach-Object { Join-Path $output $_ }
} finally {
    $env:PYTHONPATH = $previousPythonPath
}
