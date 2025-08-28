# Demo script for training APIs
# Test all available training endpoints

$BaseUrl = "https://train-pet-image.onrender.com"

Write-Host "=== Pet Image API Training Demo ===" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Yellow

# Test 1: Get current status
Write-Host "`n🔍 Test 1: Get Status" -ForegroundColor Green
try {
    $status = Invoke-RestMethod -Uri "$BaseUrl/status" -Method GET
    Write-Host "✅ Status Response:" -ForegroundColor Green
    $status | ConvertTo-Json -Depth 3 | Write-Host
} catch {
    Write-Host "❌ Status Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Train with current mode (LIGHT_MODE)
Write-Host "`n🚀 Test 2: Train (Current Mode)" -ForegroundColor Green
try {
    Write-Host "Training... (this may take 30-60 seconds)" -ForegroundColor Yellow
    $train = Invoke-RestMethod -Uri "$BaseUrl/train" -Method POST -TimeoutSec 120
    Write-Host "✅ Training Response:" -ForegroundColor Green
    $train | ConvertTo-Json -Depth 3 | Write-Host
} catch {
    Write-Host "❌ Training Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# Test 3: Force train light features
Write-Host "`n⚡ Test 3: Force Light Training" -ForegroundColor Green
try {
    Write-Host "Light training... (faster, 10-30 seconds)" -ForegroundColor Yellow
    $lightTrain = Invoke-RestMethod -Uri "$BaseUrl/train/light" -Method POST -TimeoutSec 60
    Write-Host "✅ Light Training Response:" -ForegroundColor Green
    $lightTrain | ConvertTo-Json -Depth 3 | Write-Host
} catch {
    Write-Host "❌ Light Training Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Get status after training
Write-Host "`n📊 Test 4: Status After Training" -ForegroundColor Green
try {
    $finalStatus = Invoke-RestMethod -Uri "$BaseUrl/status" -Method GET
    Write-Host "✅ Final Status:" -ForegroundColor Green
    $finalStatus | ConvertTo-Json -Depth 3 | Write-Host
} catch {
    Write-Host "❌ Final Status Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Training API Demo Complete!" -ForegroundColor Cyan
Write-Host "`nAvailable Endpoints:" -ForegroundColor Yellow
Write-Host "  GET  /status           - Get app status and features info"
Write-Host "  POST /train            - Train with current mode (LIGHT/TensorFlow)"  
Write-Host "  POST /train/light      - Force train light features (color histogram)"
Write-Host "  POST /search           - Search similar images (with file upload)"
Write-Host "  GET  /                 - Beautiful homepage"
