$ErrorActionPreference = 'Stop'
$baseUrl = 'http://127.0.0.1:5101'
$headers = @{ 'X-Internal-Token' = 'dev-token' }

$health = Invoke-RestMethod "$baseUrl/health"
if ($health.status -ne 'ok' -or $health.service -ne 'dotnet-svc') { throw 'Health check failed.' }

try {
    Invoke-RestMethod "$baseUrl/api/hello" | Out-Null
    throw 'Expected /api/hello without a token to fail.'
} catch {
    if ($_.Exception.Response.StatusCode.value__ -ne 401) { throw }
}
$hello = Invoke-RestMethod "$baseUrl/api/hello" -Headers $headers
if ($hello.message -ne 'Hello from DotnetSvc' -or -not $hello.time) { throw 'Hello response failed.' }

$reportBody = @{ items = @(@{ name = 'alpha'; value = 10 }, @{ name = 'beta'; value = 20 }, @{ name = 'gamma'; value = 30 }, @{ name = 'delta'; value = 40 }) } | ConvertTo-Json -Depth 5
$report = Invoke-RestMethod "$baseUrl/api/report" -Method Post -Headers $headers -ContentType 'application/json' -Body $reportBody
if ($report.count -ne 4 -or $report.sum -ne 100 -or $report.average -ne 25 -or $report.min -ne 10 -or $report.max -ne 40 -or $report.topItems.Count -ne 3) { throw 'Report summary failed.' }

try {
    Invoke-RestMethod "$baseUrl/api/report" -Method Post -Headers $headers -ContentType 'application/json' -Body '{"items":[]}' | Out-Null
    throw 'Expected empty report input to fail.'
} catch {
    if ($_.Exception.Response.StatusCode.value__ -ne 400) { throw }
}

try {
    Invoke-RestMethod "$baseUrl/api/hello" -Headers @{ Host = 'example.com'; 'X-Internal-Token' = 'dev-token' } | Out-Null
    throw 'Expected invalid Host to fail.'
} catch {
    if ($_.Exception.Response.StatusCode.value__ -ne 400) { throw }
}

Write-Output 'DotnetSvc smoke checks passed.'
