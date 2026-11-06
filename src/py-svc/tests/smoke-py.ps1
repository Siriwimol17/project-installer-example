param(
    [string]$BaseUrl = "http://127.0.0.1:5102",
    [string]$Token = "dev-token"
)

$ErrorActionPreference = "Stop"

$health = Invoke-RestMethod -Method Get -Uri "$BaseUrl/health"
if ($health.status -ne "ok" -or $health.service -ne "py-svc") {
    throw "Unexpected health response."
}
Write-Host "PASS GET /health"

$body = @{ text = "Hello world. Hello again!" } | ConvertTo-Json
$headers = @{ "X-Internal-Token" = $Token }
$analysis = Invoke-RestMethod -Method Post -Uri "$BaseUrl/analyze" -Headers $headers -ContentType "application/json" -Body $body
if ($analysis.wordCount -ne 4 -or $analysis.sentenceCount -ne 2) {
    Write-Host "Actual /analyze response: $($analysis | ConvertTo-Json -Compress -Depth 10)"
    throw "Unexpected authenticated /analyze response. Expected wordCount=4 and sentenceCount=2."
}
Write-Host "PASS POST /analyze with token"

try {
    Invoke-RestMethod -Method Post -Uri "$BaseUrl/analyze" -ContentType "application/json" -Body $body | Out-Null
    throw "Expected unauthenticated /analyze to fail with 401."
} catch {
    if ($_.Exception.Response.StatusCode.value__ -ne 401) { throw }
}
Write-Host "PASS POST /analyze without token returns 401"
