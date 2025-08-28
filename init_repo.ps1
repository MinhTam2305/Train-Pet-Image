<#
Initialize a git repo locally, create initial commit, and show suggested remote push command.
This script will NOT push to any remote.
#>

param(
    [string]$RemoteUrl = ''
)

if (-not (Test-Path .git)) {
    git init
    git add -A
    git commit -m "Initial commit: prepare app for deployment"
    Write-Host "Repository initialized and committed locally."
} else {
    Write-Host "Repository already initialized."
}

if ($RemoteUrl -ne '') {
    git remote add origin $RemoteUrl
    Write-Host "Remote 'origin' set to $RemoteUrl"
    Write-Host "To push: git push -u origin main"
} else {
    Write-Host "No remote specified. Provide a remote URL to set origin."
}
