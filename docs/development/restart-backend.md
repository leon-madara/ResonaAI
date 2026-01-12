# 🔄 Restart Backend Server

The `/api/ui-config` endpoint was added but the server needs to be restarted to register it.

## Quick Restart Steps

### Option 1: If server is running in a terminal
1. Go to the terminal where the backend is running
2. Press `Ctrl+C` to stop it
3. Run:
   ```powershell
   cd "c:\Users\Dev Projects\ResonaAI\ResonaAI"
   $env:DATABASE_URL="postgresql://postgres:9009@localhost:5432/mental_health"
   $env:JWT_SECRET_KEY="test-secret-key-dev-only"
   python apps/backend/gateway/main.py
   ```

### Option 2: Check if server is running
```powershell
# Check if port 8000 is in use
Test-NetConnection -ComputerName localhost -Port 8000

# If it's running, you'll need to stop it first
# Then restart with the command above
```

### Option 3: Kill and restart
```powershell
# Find the process
Get-Process python | Where-Object {$_.Path -like "*ResonaAI*"}

# Kill it (replace PID with actual process ID)
Stop-Process -Id <PID> -Force

# Then restart
cd "c:\Users\Dev Projects\ResonaAI\ResonaAI"
$env:DATABASE_URL="postgresql://postgres:9009@localhost:5432/mental_health"
$env:JWT_SECRET_KEY="test-secret-key-dev-only"
python apps/backend/gateway/main.py
```

## Verify Endpoint is Working

After restarting, test the endpoint:
```powershell
$token = "YOUR_JWT_TOKEN_HERE"
Invoke-RestMethod -Uri "http://localhost:8000/api/ui-config" `
    -Method GET `
    -Headers @{ "Authorization" = "Bearer $token" }
```

Or check the API docs:
- Open: http://localhost:8000/docs
- Look for `/api/ui-config` in the list of endpoints

## Why This Happened

The endpoint was added to the code after the server started. FastAPI needs a restart to register new routes.
