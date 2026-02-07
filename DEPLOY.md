# 🚀 Deployment Guide - Google OAuth Fix

## What Was Wrong?
Django was using `request.build_absolute_uri()` which generated `http://127.0.0.1:8002` URLs instead of `https://talentsolutions.com.np` when behind nginx reverse proxy.

## What Was Fixed?
1. ✅ Added `SECURE_PROXY_SSL_HEADER` to Django settings (trusts nginx's X-Forwarded-Proto header)
2. ✅ Changed Google OAuth to use `SITE_URL` from .env instead of `build_absolute_uri()`
3. ✅ Updated `.env` with proper production settings
4. ✅ Updated `nginx.conf` with your domain and enabled HTTPS
5. ✅ Generated a secure `SECRET_KEY`

---

## 📋 Deployment Steps

### Step 1: Push Changes to Server
```bash
# On your local machine
git add .
git commit -m "Fix Google OAuth redirect URI issue"
git push origin master
```

### Step 2: SSH into DigitalOcean Droplet
```bash
ssh root@talentsolutions.com.np
# or whatever user you use
```

### Step 3: Pull Latest Code
```bash
cd /path/to/talent_solutions  # adjust path
git pull origin master
```

### Step 4: Update .env on Server
**IMPORTANT:** Make sure your server's `.env` file has these exact values:

```bash
nano .env
```

Paste this:
```env
# ── Core ──────────────────────────────────
SECRET_KEY=i%q0!e9@5qi$s4z-h$hg@r-4i0cbmy65+pxr3tkpz@m$tq!ju1
DEBUG=False
ALLOWED_HOSTS=talentsolutions.com.np,www.talentsolutions.com.np
SITE_URL=https://talentsolutions.com.np

# ── Google OAuth ──────────────────────────
GOOGLE_OAUTH_CLIENT_ID=1080034778136-qqrcvoc34nub56vcmsp4803alneeno1v.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=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

# ── Brevo SMTP (relay) ────────────────────
BREVO_SMTP_LOGIN=90e20e001@smtp-brevo.com
BREVO_SMTP_PASSWORD=9AG0TVfMJRjk64ZO
```

Save with `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 5: Rebuild Docker Container
```bash
# Stop current container
docker-compose down

# Rebuild with new code
docker-compose build --no-cache

# Start container
docker-compose up -d
```

### Step 6: Verify Deployment
```bash
# Check logs
docker-compose logs -f app

# Check if container is running
docker-compose ps
```

### Step 7: Test Google OAuth
1. Visit https://talentsolutions.com.np/login/
2. Click "Continue with Google"
3. Should redirect properly now! ✅

---

## 🔍 Troubleshooting

### If HTTPS isn't working:
Your nginx.conf expects SSL certificates at:
```
/etc/letsencrypt/live/talentsolutions.com.np/fullchain.pem
/etc/letsencrypt/live/talentsolutions.com.np/privkey.pem
```

**Check if certificates exist:**
```bash
ls -la /etc/letsencrypt/live/talentsolutions.com.np/
```

**If missing, you need to obtain SSL certs first:**
1. Temporarily comment out the HTTPS block in nginx.conf
2. Run certbot to get certificates
3. Uncomment the HTTPS block
4. Reload nginx

### If Google OAuth still fails:
**Check the exact error:**
```bash
docker-compose logs -f app | grep -i oauth
```

**Verify SITE_URL in Django:**
```bash
docker-compose exec app python manage.py shell
>>> from django.conf import settings
>>> print(settings.SITE_URL)
# Should print: https://talentsolutions.com.np
```

**Verify the redirect URI Django sends to Google:**
- Visit https://talentsolutions.com.np/auth/google/
- Look at the URL you get redirected to (in browser address bar)
- Find the `redirect_uri=` parameter
- It should be: `https://talentsolutions.com.np/auth/google/callback/`
- NOT: `http://127.0.0.1:8002/auth/google/callback/`

### If you get "redirect_uri_mismatch":
**Double-check Google Console:**
1. Go to https://console.cloud.google.com
2. Select your project
3. APIs & Services → Credentials
4. Click your OAuth 2.0 Client ID
5. Authorized redirect URIs should have:
   - `https://talentsolutions.com.np/auth/google/callback/`
   - `https://www.talentsolutions.com.np/auth/google/callback/`

**EXACT match required** - no trailing slashes mismatches, http vs https, etc.

---

## 📌 Important Notes

1. **Never commit .env to git** - It's in .gitignore, keep it that way
2. **SECRET_KEY must stay secret** - Don't share it publicly
3. **DEBUG=False in production** - Already set correctly
4. **HTTPS is required** - Google OAuth won't work on HTTP (except localhost)

---

## ✅ Success Checklist
- [ ] Code pushed to server
- [ ] .env updated with SITE_URL=https://talentsolutions.com.np
- [ ] Docker container rebuilt
- [ ] HTTPS working (green padlock in browser)
- [ ] Google OAuth redirect works
- [ ] Can log in with Google successfully

---

**Questions? Check the logs:**
```bash
docker-compose logs -f app
```
