$ErrorActionPreference = "Stop"
Write-Host "TabletopMentor acceptance"
python -m pytest -q tests/test_tabletop_acceptance.py
if ($LASTEXITCODE -ne 0) { throw "backend acceptance failed" }
Write-Host "backend acceptance passed"
if (Test-Path (Join-Path $PSScriptRoot "frontend/node_modules/.bin/tsc.cmd")) {
  npm --prefix frontend run build
  if ($LASTEXITCODE -ne 0) { throw "frontend build failed" }
  Write-Host "frontend build passed"
} else {
  Write-Warning "frontend dependencies are missing; build skipped"
}
Write-Host "acceptance complete"
