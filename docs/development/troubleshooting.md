# 🔧 Fix CORS Error - Server Restart Required

## The Problem

The `/api/ui-config` endpoint is returning a CORS error because:
1. **The endpoint isn't registered yet** - Server needs restart
2. **CORS preflight is failing** - OPTIONS request not handled

## ✅ Solution: Restart Backend Server

### Step 1: Stop Current Server
1. Find the terminal where backend is running
2. Press `Ctrl+C` to stop it

### Step 2: Restart Server
```powershell
cd "c:\Users\Dev Projects\ResonaAI\ResonaAI\apps\backend\gateway"
$env:DATABASE_URL="postgresql://postgres:9009@localhost:5432/mental_health"
$env:JWT_SECRET_KEY="test-secret-key-dev-only"
python main.py
```

### Step 3: Verify Endpoint is Registered
1. Open: http://localhost:8000/docs
2. Look for `/api/ui-config` in the endpoints list
3. If you see it, the endpoint is registered! ✅

### Step 4: Test Again
1. Go to: http://localhost:3000/ui-test
2. Paste your JWT token
3. Click "Load UI Config"

## What I Fixed

1. ✅ **Added explicit OPTIONS handler** for CORS preflight
2. ✅ **Updated CORS configuration** to explicitly allow localhost:3000
3. ✅ **Endpoint is correctly defined** at `/api/ui-config`

## Why This Happens

- FastAPI registers routes when the server starts
- New routes added to code won't appear until server restarts
- CORS middleware needs the endpoint to exist to add headers

## Quick Test After Restart

Test the endpoint directly:
```powershell
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlcjJAZXhhbXBsZS5jb20iLCJ1c2VyX2lkIjoidXNlci0zIiwiZXhwIjoxNzY1NzYxNjQwfQ.DQCgc6ez9KiVZYPOU9zqvoTVH_ErSRTMjDhCUX7kN-A"
Invoke-RestMethod -Uri "http://localhost:8000/api/ui-config" `
    -Method GET `
    -Headers @{ "Authorization" = "Bearer $token" }
```

If this works, the frontend should work too!
