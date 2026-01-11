# Backlog: Real Authentication System

**Status**: 🔴 Mock Implementation Only  
**Priority**: ⭐⭐⭐⭐⭐ CRITICAL  
**Estimated Effort**: 1 week  
**Blocking**: Production deployment

---

## Overview

Replace mock authentication with real user database integration. Currently the system uses hardcoded credentials which is a security vulnerability and blocks production deployment.

---

## Current State

### ✅ What Works (Mock)
- JWT token generation and validation
- Authentication middleware
- Protected routes
- Basic user registration/login endpoints

### ❌ What's Missing (Real Implementation)
- Password hashing (bcrypt)
- User database lookup
- Email verification
- Duplicate email checking
- Password validation
- Account management

---

## Current Mock Implementation

**Location**: `apps/backend/gateway/middleware/auth.py`

**Problems**:
```python
# MOCK - Always returns success
async def authenticate_user(email: str, password: str):
    return {
        "user_id": "mock-user-123",
        "email": email,
        "is_anonymous": False
    }
```

**Security Issues**:
- Any email/password combination works
- No password validation
- No user persistence
- No account security

---

## Required Implementation

### 1. Database Schema Updates
```sql
-- Add password_hash column to users table
ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
```

### 2. Password Hashing
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

### 3. Real User Authentication
```python
async def authenticate_user(email: str, password: str):
    # Look up user in database
    user = await db.get_user_by_email(email)
    if not user:
        return None
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    await db.update_last_login(user.user_id)
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "is_anonymous": user.is_anonymous
    }
```

### 4. User Registration
```python
async def register_user(email: str, password: str, consent_version: str):
    # Check if user exists
    existing = await db.get_user_by_email(email)
    if existing:
        raise HTTPException(400, "Email already registered")
    
    # Validate password strength
    if not is_strong_password(password):
        raise HTTPException(400, "Password too weak")
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    user_id = await db.create_user(
        email=email,
        password_hash=password_hash,
        consent_version=consent_version
    )
    
    return {"user_id": user_id, "email": email}
```

---

## Implementation Tasks

### Phase 1: Database Updates (Day 1)
- [ ] Add password_hash column to users table
- [ ] Add email_verified, created_at, last_login columns
- [ ] Create database migration script
- [ ] Update user model classes

### Phase 2: Password Security (Day 2)
- [ ] Install bcrypt dependency
- [ ] Implement password hashing functions
- [ ] Implement password strength validation
- [ ] Add password security tests

### Phase 3: Authentication Logic (Day 3-4)
- [ ] Replace mock authenticate_user function
- [ ] Implement real user lookup
- [ ] Implement password verification
- [ ] Update login endpoint

### Phase 4: Registration Logic (Day 4-5)
- [ ] Implement real user registration
- [ ] Add email duplicate checking
- [ ] Add password validation
- [ ] Update registration endpoint

### Phase 5: Testing & Security (Day 5)
- [ ] Write authentication tests
- [ ] Test password hashing
- [ ] Test duplicate email handling
- [ ] Security audit

---

## Security Requirements

### Password Policy
- Minimum 8 characters
- Must contain uppercase, lowercase, number
- Must contain special character
- Cannot be common passwords

### Security Features
- Password hashing with bcrypt (cost factor 12)
- JWT tokens with expiration (24 hours)
- Rate limiting on login attempts
- Secure password reset flow

### Data Protection
- No plaintext passwords stored
- Secure session management
- HTTPS only in production
- GDPR compliance for user data

---

## Testing Strategy

### Unit Tests
- [ ] Password hashing/verification
- [ ] User lookup functions
- [ ] Registration validation
- [ ] Authentication flow

### Integration Tests
- [ ] Login endpoint with real credentials
- [ ] Registration endpoint with validation
- [ ] Protected route access
- [ ] JWT token validation

### Security Tests
- [ ] SQL injection attempts
- [ ] Password brute force protection
- [ ] Invalid token handling
- [ ] Session security

---

## Dependencies

**Available**:
- ✅ PostgreSQL database
- ✅ JWT token system
- ✅ Authentication middleware
- ✅ User model structure

**Needed**:
- bcrypt library for password hashing
- Email validation library
- Rate limiting middleware

---

## Success Criteria

- ✅ Real user registration works
- ✅ Real user login works
- ✅ Passwords are securely hashed
- ✅ Duplicate emails are rejected
- ✅ All tests pass
- ✅ Security audit passes
- ✅ Production ready

---

## Risk Assessment

**Current Risk**: 🔴 **HIGH**
- Mock authentication is a security vulnerability
- Cannot deploy to production
- No user account security

**After Implementation**: 🟢 **LOW**
- Secure password handling
- Real user authentication
- Production ready

---

## Timeline

**Total Effort**: 1 week  
**Complexity**: Low-Medium  
**Blocking**: Production deployment

**Must complete before**: Any production deployment

---

## Next Steps

1. **Add Database Columns** (2 hours)
2. **Install bcrypt** (30 minutes)  
3. **Implement Password Hashing** (4 hours)
4. **Replace Mock Functions** (1 day)
5. **Write Tests** (1 day)
6. **Security Review** (4 hours)

This is a **production blocker** and must be completed before deployment.