# Test script for Render deployment
# Tests the /search endpoint with a sample image

param(
    [string]$ImagePath = "",
    [string]$BaseUrl = "https://train-pet-image.onrender.com"
)

Write-Host "Testing Pet Image Search API at: $BaseUrl"

# Test 1: Health check (GET root - should return 404/405 but server is alive)
Write-Host "`n=== Test 1: Server Health ===" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $BaseUrl -Method GET -ErrorAction SilentlyContinue
    Write-Host "Server is responding (status: $($response.StatusCode))"
} catch {
    if ($_.Exception.Response.StatusCode -eq 404 -or $_.Exception.Response.StatusCode -eq 405) {
        Write-Host "✅ Server is alive (404/405 expected for GET /)" -ForegroundColor Green
    } else {
        Write-Host "❌ Server might be down: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 2: POST /search without file (should return 400)
Write-Host "`n=== Test 2: No file upload ===" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/search" -Method POST -ErrorAction Stop
    Write-Host "❌ Unexpected success - should have failed" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✅ Correctly rejected empty request (400)" -ForegroundColor Green
    } else {
        Write-Host "❌ Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 3: POST /search with image file
if ($ImagePath -and (Test-Path $ImagePath)) {
    Write-Host "`n=== Test 3: Image search ===" -ForegroundColor Yellow
    try {
        $form = @{
            file = Get-Item $ImagePath
        }
        $response = Invoke-RestMethod -Uri "$BaseUrl/search" -Method POST -Form $form
        Write-Host "✅ Image search successful!" -ForegroundColor Green
        Write-Host "Found $($response.similar_images.Count) similar images:"
        $response.similar_images | ForEach-Object { 
            Write-Host "  - $($_.image_path) (similarity: $([math]::Round($_.similarity, 3)))"
        }
    } catch {
        Write-Host "❌ Image search failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "Response: $responseBody" -ForegroundColor Red
        }
    }
} else {
    Write-Host "`n=== Test 3: Skipped (no image provided) ===" -ForegroundColor Yellow
    Write-Host "To test with an image: .\test_api.ps1 -ImagePath 'path\to\your\image.jpg'"
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "Manual Postman test:"
Write-Host "POST $BaseUrl/search"
Write-Host "Body: form-data, key='file', type=File, value=<your_image>"
