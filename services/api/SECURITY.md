# Security Guidelines - Aplicación Señas API

## Email Normalization

### Case-Insensitive Email Handling
All emails are **normalized to lowercase** for security and consistency:

```python
# Registration: "User@Example.COM" → stored as "user@example.com"
# Login: "USER@EXAMPLE.COM" → matched with "user@example.com"
```

**Benefits:**
- ✅ Prevents duplicate accounts with different cases (User@test.com vs user@test.com)
- ✅ Consistent login experience (case doesn't matter)
- ✅ Standard practice (RFC 5321 - email local-part can be case-sensitive but domains are not)
- ✅ Better UX - users don't need to remember exact capitalization

**Implementation:**
```python
def normalize_email(email: str) -> str:
    """Normalize email to lowercase for case-insensitive comparison"""
    return email.lower().strip()

def check_email_exists(table, email: str) -> bool:
    """Check if email exists (case-insensitive)"""
    normalized_email = normalize_email(email)
    # ... scan and compare with normalized emails
```

**Applied to:**
- ✅ Registration endpoint - stores email in lowercase
- ✅ Login endpoint - compares emails case-insensitively
- ✅ Email uniqueness check - prevents Case.Variations@example.com

---

## Password Security

### Implementation
The API implements a **defense-in-depth** approach for password security:

#### 1. Length Constraints (DoS Protection)
```python
MIN_PASSWORD_LENGTH = 8    # Minimum for security
MAX_PASSWORD_LENGTH = 128  # Prevents DoS attacks
```

**Why 128 characters max?**
- Prevents **Denial of Service (DoS)** attacks using extremely long passwords
- Without a limit, attackers could send 1GB+ passwords to exhaust:
  - CPU resources (hashing time)
  - Memory (storing the input)
  - Network bandwidth
- 128 chars is sufficient for strong passphrases (e.g., "correct horse battery staple + numbers + symbols")

#### 2. Pre-hashing with SHA256
```python
SHA256(password) → bcrypt(sha256_hash)
```

**Benefits:**
- Supports passwords longer than bcrypt's 72-byte limit
- SHA256 is fast and deterministic (always produces 64 hex chars)
- The SHA256 hash is then securely hashed with bcrypt

#### 3. Bcrypt for Final Hashing
- **Adaptive cost factor**: Automatically increases computational difficulty over time
- **Salt included**: Each password gets a unique salt (prevents rainbow table attacks)
- **Slow by design**: ~100ms per hash (prevents brute force)

### Password Requirements

✅ **Recommended passwords:**
- Length: 12-128 characters
- Mix of uppercase, lowercase, numbers, symbols
- Avoid dictionary words
- Example: `MyS3cur3P@ssw0rd2024!`

❌ **Rejected passwords:**
- < 8 characters (too weak)
- \> 128 characters (DoS protection)

### Attack Mitigations

| Attack Type | Mitigation |
|-------------|------------|
| **DoS (Long Password)** | Max 128 chars validation |
| **Brute Force** | Bcrypt slow hashing (~100ms/attempt) |
| **Rainbow Tables** | Bcrypt automatic salting |
| **Dictionary Attack** | Min 8 chars + complexity recommended |
| **Timing Attacks** | Bcrypt constant-time comparison |

## JWT Token Security

### Configuration
```python
SECRET_KEY = os.getenv("SECRET_KEY", "...")  # Use strong key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Best Practices
1. **Change SECRET_KEY** in production (use 256-bit random key)
2. **Use HTTPS** in production (prevent token interception)
3. **Short expiration time** (30 minutes) balances security vs UX
4. **Store tokens securely** on client (httpOnly cookies or secure storage)

## 2. API Endpoint Security Levels

### Public Endpoints (No Authentication)
- `GET /` - Health check
- `GET /healthz` - Health check
- `GET /readyz` - Readiness check
- `GET /v1/languages` - List available languages
- `GET /v1/topics` - List all topics
- `GET /v1/topics/{id}` - Get topic details
- `GET /v1/levels/topic/{id}` - List levels for a topic
- `GET /v1/levels/{id}` - Get level details
- `GET /v1/exercises/level/{id}` - List exercises for a level
- `GET /v1/exercises/{id}` - Get exercise details

### Authenticated Endpoints (Requires Valid JWT)
- `POST /v1/auth/register` - Create new user account (**always creates as "user" role**)
- `POST /v1/auth/login` - Login and get JWT token
- `GET /v1/auth/me` - Get current user info
- `POST /v1/progress/submit` - Submit exercise attempt
- `GET /v1/progress/level/{id}` - Get user's progress for level
- `GET /v1/progress/exercise/{id}` - Get user's progress for exercise
- `GET /v1/progress/summary` - Get overall user progress
- `GET /v1/leaderboards/global` - Get global leaderboard
- `GET /v1/leaderboards/topic/{id}` - Get topic leaderboard
- `GET /v1/leaderboards/level/{id}` - Get level leaderboard
- `GET /v1/leaderboards/user/{id}/rank` - Get user rank

### Admin-Only Endpoints (Requires Admin Role)

**Content Management:**
- `POST /v1/topics` - Create new topic
- `PUT /v1/topics/{id}` - Update topic
- `DELETE /v1/topics/{id}` - Delete topic
- `POST /v1/levels` - Create new level
- `PUT /v1/levels/{id}` - Update level
- `DELETE /v1/levels/{id}` - Delete level
- `POST /v1/exercises` - Create new exercise
- `PUT /v1/exercises/{id}` - Update exercise
- `DELETE /v1/exercises/{id}` - Delete exercise

**User Management:**
- `PATCH /v1/auth/users/{user_id}/role` - Promote/demote user role (admin only)
  - ⚠️ **CRITICAL SECURITY**: Admins cannot demote themselves
  - Only way to create admin users after initial setup

## 3. Role-Based Access Control (RBAC)

### User Roles

**user** (Default Role)
- Automatically assigned to all new registrations
- Can access all public and authenticated endpoints
- Can submit exercise attempts and track progress
- Can view leaderboards
- **CANNOT be promoted to admin by themselves**

**admin** (Privileged Role)
- Has all user permissions
- Can create, update, and delete content (topics, levels, exercises)
- Can promote users to admin or demote admins to user
- **CANNOT demote themselves** (prevents accidental lockout)
- **CANNOT be self-assigned during registration** (security measure)

### Admin Creation Process

1. **Initial Setup**: First admin created via secure method:
   ```bash
   # Option A: Via seed script
   python scripts/seed_database.py
   
   # Option B: Register as user, then manually promote in database
   ```

2. **Subsequent Admins**: Only existing admins can promote users:
   ```bash
   # First, user registers normally (always creates as "user")
   POST /v1/auth/register
   {
     "email": "newuser@example.com",
     "password": "SecurePass123!",
     "name": "New User"
   }
   
   # Then admin promotes them
   PATCH /v1/auth/users/{user_id}/role?role=admin
   Authorization: Bearer {admin_jwt_token}
   ```

3. **Security**: The `role` field is ignored in registration to prevent privilege escalation attacks

### Example Attack Prevention

❌ **This will NOT work (security protection):**
```bash
POST /v1/auth/register
{
  "email": "hacker@evil.com",
  "password": "HackPass123!",
  "name": "Hacker",
  "role": "admin"  # ← IGNORED! Always creates as "user"
}
```

✅ **Correct way to create admin:**
```bash
# 1. User self-registers (creates as "user")
POST /v1/auth/register { ... }

# 2. Existing admin promotes them
PATCH /v1/auth/users/{user_id}/role?role=admin
Authorization: Bearer {admin_token}
```

## Rate Limiting (TODO - Production)

**Recommended for production:**
```python
# Install: pip install slowapi
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("5/minute")  # 5 login attempts per minute
@router.post("/auth/login")
async def login(...):
    ...
```

## CORS Configuration

**Current (Development):**
```python
allow_origins=["*"]  # Allow all origins
```

**Production:**
```python
allow_origins=[
    "https://app.aplicacion-senas.com",
    "https://admin.aplicacion-senas.com"
]
```

## Environment Variables

**Required for production:**
```bash
SECRET_KEY="your-256-bit-random-key-here"
AWS_REGION="us-east-1"
DYNAMO_ENDPOINT_URL=""  # Empty for real AWS
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
```

**Generate secure SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

## Security Checklist for Production

- [ ] Change SECRET_KEY to random 256-bit value
- [ ] Set CORS to specific origins only
- [ ] Enable HTTPS/TLS (API Gateway handles this)
- [ ] Implement rate limiting (login, register endpoints)
- [ ] Set up CloudWatch alarms for suspicious activity
- [ ] Enable AWS WAF rules (SQL injection, XSS protection)
- [ ] Regular security updates (dependencies)
- [ ] Implement password reset flow with email verification
- [ ] Add 2FA for admin accounts
- [ ] Log all authentication attempts
- [ ] Implement session management (token blacklisting on logout)

## Reporting Security Issues

If you discover a security vulnerability, please email:
**security@aplicacion-senas.com**

Do NOT create public GitHub issues for security problems.

---

Last updated: November 2025
