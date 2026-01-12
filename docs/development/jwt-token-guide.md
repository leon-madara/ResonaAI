# 🔑 How to Get Your JWT Token

You need a JWT (JSON Web Token) to access the personalized UI configuration. Here are **3 easy ways** to get one:

---

## 🚀 Method 1: Use the Helper Script (Easiest!)

I've created a simple script that does everything for you:

### PowerShell (Windows)
```powershell
cd "c:\Users\Dev Projects\ResonaAI\ResonaAI"
.\scripts\get_auth_token.ps1
```

This will:
- ✅ Register a new user (or login if already exists)
- ✅ Get your JWT token
- ✅ Copy it to your clipboard automatically
- ✅ Show you exactly what to do next

**If the user already exists, use:**
```powershell
.\scripts\get_auth_token.ps1 -Login
```

---

## 📝 Method 2: Register via API (Manual)

### Using PowerShell:
```powershell
$body = @{
    email = "testuser@example.com"
    password = "TestPass123!"
    consent_version = "1.0"
    is_anonymous = $false
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

# Your token is here:
Write-Host $response.access_token
```

### Using curl:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!",
    "consent_version": "1.0",
    "is_anonymous": false
  }'
```

The response will include:
```json
{
  "message": "User registered successfully",
  "user_id": "uuid-here",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Copy the `access_token` value!**

---

## 🔐 Method 3: Login (If You Already Registered)

### Using PowerShell:
```powershell
$body = @{
    email = "testuser@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

Write-Host $response.access_token
```

### Using curl:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!"
  }'
```

---

## 🎯 What to Do With Your Token

Once you have the token:

1. **Open the UI Test Page**: http://localhost:3000/ui-test
2. **Paste your token** in the "Authentication Token" field
3. **Click "Load UI Config"**
4. **See your personalized UI!** 🎨

---

## 🔍 Using the API Documentation

You can also use the interactive API docs:

1. Open: http://localhost:8000/docs
2. Find the `/api/auth/register` endpoint
3. Click "Try it out"
4. Fill in the form:
   - `email`: testuser@example.com
   - `password`: TestPass123!
   - `consent_version`: 1.0
   - `is_anonymous`: false
5. Click "Execute"
6. Copy the `access_token` from the response

---

## ⚠️ Important Notes

### Token Expiration
- Tokens expire after **24 hours** (default)
- If your token expires, just run the script again or login

### User Already Exists?
If you get an error saying the user already exists:
- Use the **login** method instead
- Or use a different email address

### Test User from Fake Data Script
If you ran `create_fake_user_data.py`, that creates a user but **doesn't give you a token**. You still need to:
1. Register a new user (or login if you know the password)
2. Get the token
3. Use that token to access the UI config

---

## 🐛 Troubleshooting

### "Connection refused" or "Cannot connect"
- Make sure the backend server is running on port 8000
- Check: `Test-NetConnection -Port 8000`

### "Invalid credentials"
- Make sure you're using the correct email/password
- Try registering a new user instead

### "User already exists"
- Use the login endpoint instead
- Or use a different email address

### Token doesn't work
- Token might be expired (24h limit)
- Make sure you copied the entire token (it's very long!)
- Try getting a fresh token

---

## 📋 Quick Reference

**Registration Endpoint:**
```
POST http://localhost:8000/api/auth/register
Body: { "email": "...", "password": "...", "consent_version": "1.0", "is_anonymous": false }
```

**Login Endpoint:**
```
POST http://localhost:8000/api/auth/login
Body: { "email": "...", "password": "..." }
```

**UI Config Endpoint (requires token):**
```
GET http://localhost:8000/api/ui-config
Headers: { "Authorization": "Bearer YOUR_TOKEN_HERE" }
```

---

## 💡 Pro Tip

The helper script (`get_auth_token.ps1`) automatically:
- ✅ Handles errors gracefully
- ✅ Copies token to clipboard
- ✅ Shows you exactly what to do next
- ✅ Works for both registration and login

**Just run it and you're done!** 🎉
