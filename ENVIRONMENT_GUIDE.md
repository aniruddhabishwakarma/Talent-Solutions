# 🌍 Environment Configuration Guide

## **How It Works (Like Spring Boot Profiles!)**

This project uses **environment-based configuration** similar to Spring Boot's profile system. Instead of manually changing settings between development and production, the system automatically loads the correct configuration.

---

## **📁 Files Structure**

```
talent_solutions/
├── .env.local         ← Development settings (your laptop)
├── .env.production    ← Production settings (server)
├── .env.example       ← Template (commit this to git)
├── .gitignore         ← Blocks .env files from git
└── settings.py        ← Auto-detects environment
```

---

## **🔄 How Environment Detection Works**

### **Spring Boot Way:**
```yaml
# application.yml
spring:
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}  # defaults to 'dev'
```

### **Our Django Way:**
```python
# settings.py
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')  # defaults to 'local'

if ENVIRONMENT == 'production':
    load_dotenv('.env.production')  # Production config
else:
    load_dotenv('.env.local')       # Development config
```

---

## **🚀 Usage**

### **For Local Development (Default)**

Just run Django normally - it auto-loads `.env.local`:

```bash
python manage.py runserver
```

Output: `💻 Loading LOCAL config from .env.local`

**Settings Used:**
- `DEBUG=True`
- `ALLOWED_HOSTS=localhost,127.0.0.1`
- `SITE_URL=http://localhost:8000`

---

### **For Production (Server)**

Set the `ENVIRONMENT` variable before running:

#### **Windows (PowerShell):**
```powershell
$env:ENVIRONMENT="production"
python manage.py runserver
```

#### **Linux/Mac/Docker:**
```bash
export ENVIRONMENT=production
python manage.py runserver
```

#### **Docker (docker-compose.yml):**
```yaml
services:
  app:
    environment:
      - ENVIRONMENT=production
```

Output: `🚀 Loading PRODUCTION config from .env.production`

**Settings Used:**
- `DEBUG=False`
- `ALLOWED_HOSTS=talentsolutions.com.np,www.talentsolutions.com.np`
- `SITE_URL=https://talentsolutions.com.np`

---

## **📝 Configuration Files Explained**

### **`.env.local` (Development)**
```env
SECRET_KEY=local-dev-secret-key-not-for-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SITE_URL=http://localhost:8000
```

**When to use:** Running on your laptop for testing.

**Characteristics:**
- ✅ Debug toolbar enabled
- ✅ Detailed error pages
- ✅ Accepts localhost connections
- ✅ No HTTPS required
- ⚠️ Uses weak SECRET_KEY (safe for local only)

---

### **`.env.production` (Server)**
```env
SECRET_KEY=strong-random-key-for-production
DEBUG=False
ALLOWED_HOSTS=talentsolutions.com.np,www.talentsolutions.com.np
SITE_URL=https://talentsolutions.com.np
```

**When to use:** Running on DigitalOcean Droplet (live server).

**Characteristics:**
- 🔒 Debug mode OFF (security)
- 🔒 Strong SECRET_KEY
- 🔒 HTTPS enforced
- 🔒 Only accepts configured domains
- 📧 Real email sending enabled

---

## **🔐 Security Best Practices**

### ✅ **DO:**
- ✅ Keep `.env.local` and `.env.production` in `.gitignore`
- ✅ Use different `SECRET_KEY` for each environment
- ✅ Set `DEBUG=False` in production
- ✅ Use HTTPS (`https://`) in production `SITE_URL`
- ✅ Commit `.env.example` as a template

### ❌ **DON'T:**
- ❌ Commit `.env.local` or `.env.production` to git
- ❌ Use the same SECRET_KEY in both environments
- ❌ Run production with `DEBUG=True`
- ❌ Share your `.env` files publicly

---

## **🆚 Comparison: Spring Boot vs Django**

| Feature | Spring Boot | Our Django Setup |
|---------|-------------|------------------|
| **Profile Selection** | `spring.profiles.active=dev` | `ENVIRONMENT=local` |
| **Config Files** | `application-dev.yml`<br>`application-prod.yml` | `.env.local`<br>`.env.production` |
| **Default Profile** | `default` | `local` |
| **Override Method** | `-Dspring.profiles.active=prod` | `export ENVIRONMENT=production` |
| **Auto-Detection** | ❌ Manual flag required | ✅ Defaults to local |
| **File Format** | YAML | Key-Value (.env) |

---

## **🛠️ Common Workflows**

### **Workflow 1: Working Locally**
```bash
# No setup needed! Just run:
python manage.py runserver

# Django automatically loads .env.local
```

---

### **Workflow 2: Testing Production Settings Locally**
```bash
# Windows (PowerShell):
$env:ENVIRONMENT="production"
python manage.py runserver

# Linux/Mac:
export ENVIRONMENT=production
python manage.py runserver
```

⚠️ **Note:** Production mode expects HTTPS and production domains, so some features (like OAuth) might not work on localhost in production mode.

---

### **Workflow 3: Deploying to Server**

#### **Option A: Set environment variable in Docker**
```yaml
# docker-compose.yml
services:
  app:
    environment:
      - ENVIRONMENT=production
```

#### **Option B: Set in shell before running**
```bash
# SSH into server
export ENVIRONMENT=production

# Start application
docker-compose up -d
```

---

## **🎓 Teaching Points**

### **Why Environment Variables?**
- **Separation of Concerns:** Code and config are separate
- **Security:** Secrets not in source code
- **Flexibility:** Same code runs anywhere with different configs
- **12-Factor App:** Industry best practice

### **Why Not Hardcode?**
```python
# ❌ BAD - Hardcoded
DEBUG = True  # Have to manually change before deploy

# ✅ GOOD - Environment-based
DEBUG = os.getenv('DEBUG', 'False') == 'true'
```

### **Benefits:**
1. **No Code Changes:** Switch environments without touching code
2. **Safer Deploys:** Can't accidentally deploy with DEBUG=True
3. **Team Friendly:** Each developer has their own local config
4. **CI/CD Ready:** Automated pipelines can inject configs

---

## **🐛 Troubleshooting**

### **Issue: "Bad Request (400)"**
**Cause:** Your domain isn't in `ALLOWED_HOSTS`

**Fix:** Check which `.env` file is being loaded:
```bash
python manage.py runserver
# Look for: "💻 Loading LOCAL config..." or "🚀 Loading PRODUCTION config..."
```

If using `.env.production` on localhost, either:
1. Switch to `.env.local` (remove ENVIRONMENT variable)
2. Add `localhost` to production ALLOWED_HOSTS (not recommended)

---

### **Issue: Google OAuth Not Working**
**Cause:** `SITE_URL` mismatch with OAuth redirect URI

**Solution:**
- **Local:** Use `.env.local` with `SITE_URL=http://localhost:8000`
- **Production:** Use `.env.production` with `SITE_URL=https://talentsolutions.com.np`

---

### **Issue: Wrong Config File Loading**
**Check Current Environment:**
```bash
# Windows (PowerShell)
echo $env:ENVIRONMENT

# Linux/Mac
echo $ENVIRONMENT
```

**Reset to Local:**
```bash
# Windows
$env:ENVIRONMENT=""

# Linux/Mac
unset ENVIRONMENT
```

---

## **📚 Further Reading**

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Django Settings Best Practices](https://docs.djangoproject.com/en/5.1/topics/settings/)
- [Spring Boot Profiles (for comparison)](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.profiles)

---

**Created:** February 7, 2026
**Author:** Talent Solutions Team
