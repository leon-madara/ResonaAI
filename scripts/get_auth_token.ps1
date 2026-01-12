# Get Authentication Token Script
# Simple script to register/login and get a JWT token for testing

param(
    [string]$Email = "testuser@example.com",
    [string]$Password = "TestPass123!",
    [string]$ApiUrl = "http://localhost:8000",
    [switch]$Login = $false
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Get Authentication Token" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if ($Login) {
    Write-Host "Attempting to login..." -ForegroundColor Yellow
    
    $body = @{
        email = $Email
        password = $Password
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$ApiUrl/api/auth/login" `
            -Method POST `
            -Body $body `
            -ContentType "application/json"
        
        Write-Host "[✓] Login successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your JWT Token:" -ForegroundColor Cyan
        Write-Host $response.access_token -ForegroundColor White
        Write-Host ""
        Write-Host "Copy this token and paste it into the UI Test page" -ForegroundColor Yellow
        Write-Host "URL: http://localhost:3000/ui-test" -ForegroundColor Yellow
        
        # Copy to clipboard if available
        try {
            $response.access_token | Set-Clipboard
            Write-Host "[✓] Token copied to clipboard!" -ForegroundColor Green
        } catch {
            # Clipboard not available, that's okay
        }
        
    } catch {
        Write-Host "[✗] Login failed!" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Trying registration instead..." -ForegroundColor Yellow
        $Login = $false
    }
}

if (-not $Login) {
    Write-Host "Registering new user..." -ForegroundColor Yellow
    
    $body = @{
        email = $Email
        password = $Password
        consent_version = "1.0"
        is_anonymous = $false
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$ApiUrl/api/auth/register" `
            -Method POST `
            -Body $body `
            -ContentType "application/json"
        
        Write-Host "[✓] Registration successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "User ID: $($response.user_id)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Your JWT Token:" -ForegroundColor Cyan
        Write-Host $response.access_token -ForegroundColor White
        Write-Host ""
        Write-Host "Token expires in: $($response.expires_in) seconds" -ForegroundColor Gray
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "1. Copy the token above" -ForegroundColor Yellow
        Write-Host "2. Open: http://localhost:3000/ui-test" -ForegroundColor Yellow
        Write-Host "3. Paste the token in the input field" -ForegroundColor Yellow
        Write-Host "4. Click 'Load UI Config'" -ForegroundColor Yellow
        Write-Host ""
        
        # Copy to clipboard if available
        try {
            $response.access_token | Set-Clipboard
            Write-Host "[✓] Token copied to clipboard!" -ForegroundColor Green
        } catch {
            # Clipboard not available, that's okay
        }
        
    } catch {
        Write-Host "[✗] Registration failed!" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        
        if ($_.Exception.Response.StatusCode -eq 400) {
            Write-Host "The user might already exist. Try:" -ForegroundColor Yellow
            Write-Host "  .\get_auth_token.ps1 -Login" -ForegroundColor White
        }
    }
}

Write-Host ""
