# Cleanup script - remove redundant files for deployment
# Run this before deploying to remove unnecessary files

Write-Host "Cleaning up redundant files..."

# Remove compiled Python files
if (Test-Path "__pycache__") {
    Remove-Item -Recurse -Force "__pycache__"
    Write-Host "Removed __pycache__ directory"
}

# Remove temp files
if (Test-Path "temp_image.jpg") {
    Remove-Item "temp_image.jpg"
    Write-Host "Removed temp_image.jpg"
}

# Remove SSL certs if present (should use secrets in production)
@("cert.pem", "key.pem") | ForEach-Object {
    if (Test-Path $_) {
        Remove-Item $_
        Write-Host "Removed $_"
    }
}

# Remove service account key (should use secrets in production)
if (Test-Path "serviceAccountKey.json") {
    Write-Host "WARNING: serviceAccountKey.json found - consider moving to secure secrets"
    Write-Host "Keeping file for now, but add to .gitignore"
}

# For deployment: TensorFlow files can be excluded if using LIGHT_MODE only
Write-Host "Files analysis for deployment optimization:"
Write-Host "- dactrung.py: Only needed for /train endpoint (TensorFlow)"
Write-Host "- result.py: Only needed when LIGHT_MODE=0 (TensorFlow)"  
Write-Host "- features.pkl: Only needed when LIGHT_MODE=0 (TensorFlow features)"
Write-Host "- firebase_download.py: Only needed for /train endpoint"

# Data directory analysis
$dataSize = (Get-ChildItem -Path "data" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Data directory size: $([math]::Round($dataSize, 2)) MB"
if ($dataSize -gt 100) {
    Write-Host "WARNING: Large data directory may cause deployment issues"
    Write-Host "Consider excluding data/ from Docker image and downloading at runtime"
}

Write-Host "Cleanup completed!"
