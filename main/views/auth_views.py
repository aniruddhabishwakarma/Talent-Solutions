from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from main.models import User, UserDocument, Skill, UserSkill
from main.decorators import admin_required, user_required, guest_only
import requests
import secrets
import random
from urllib.parse import urlencode
from django.utils import timezone
from datetime import timedelta, datetime


def get_tokens_for_user(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def set_jwt_cookies(response, tokens):
    """Set JWT tokens in HTTP-only cookies."""
    response.set_cookie(
        settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token'),
        tokens['access'],
        max_age=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds(),
        httponly=settings.SIMPLE_JWT.get('AUTH_COOKIE_HTTP_ONLY', True),
        secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
        samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
        path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/'),
    )
    response.set_cookie(
        settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token'),
        tokens['refresh'],
        max_age=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').total_seconds(),
        httponly=settings.SIMPLE_JWT.get('AUTH_COOKIE_HTTP_ONLY', True),
        secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
        samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'Lax'),
        path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/'),
    )
    return response


def clear_jwt_cookies(response):
    """Clear JWT tokens from cookies."""
    response.delete_cookie(settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token'))
    response.delete_cookie(settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token'))
    return response


# =============================================================================
# ADMIN AUTHENTICATION
# =============================================================================

@guest_only(redirect_to='admin_profile')
def admin_register(request):
    """Register a new admin user."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Validation
        errors = []

        if not username:
            errors.append('Username is required.')
        if not email:
            errors.append('Email is required.')
        if not password:
            errors.append('Password is required.')

        if password and password != password_confirm:
            errors.append('Passwords do not match.')

        if password and len(password) < 8:
            errors.append('Password must be at least 8 characters long.')

        # Check uniqueness
        if username and User.objects.filter(username=username).exists():
            errors.append('Username already exists.')

        if email and User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            errors.append('Phone number already registered.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'my-admin/register.html', {
                'form_data': {
                    'username': username,
                    'email': email,
                    'phone_number': phone_number,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            })

        try:
            # Create admin user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number if phone_number else None,
                role='admin',
                is_staff=True,
            )

            messages.success(request, f'Admin account created successfully! Please login.')
            return redirect('admin_login')

        except Exception as e:
            messages.error(request, f'Error creating account. Please try again.')
            return render(request, 'my-admin/register.html')

    return render(request, 'my-admin/register.html')


@guest_only(redirect_to='admin_profile')
def admin_login(request):
    """
    Login view for admin users.
    Accepts username, email, or phone number with password.
    """
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')

        if not identifier or not password:
            messages.error(request, 'Please provide login credentials.')
            return render(request, 'my-admin/login.html')

        # Find user by username, email, or phone number
        user = User.objects.filter(
            Q(username=identifier) |
            Q(email=identifier) |
            Q(phone_number=identifier)
        ).first()

        if user and user.check_password(password):
            # Check if user is admin
            if user.role == 'admin':
                # Generate JWT tokens
                tokens = get_tokens_for_user(user)

                messages.success(request, f'Welcome back, {user.first_name or user.username}!')

                # Redirect to next page or admin dashboard
                next_page = request.GET.get('next', 'admin_dashboard')
                response = redirect(next_page)

                # Set JWT cookies
                return set_jwt_cookies(response, tokens)
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'my-admin/login.html')


# =============================================================================
# ADMIN FORGOT PASSWORD (3-step: email → OTP → new password)
# =============================================================================

def admin_forgot_password(request):
    """Step 1 – admin enters their registered email."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'my-admin/forgot_password.html')

        user = User.objects.filter(email=email, role='admin').first()

        if not user:
            # Same message whether email exists or not — don't leak info
            messages.success(request, 'If this email is registered, you will receive a code.')
            return render(request, 'my-admin/forgot_password.html')

        # Generate OTP
        code = f"{random.randint(100000, 999999)}"
        now = timezone.now()
        request.session['admin_reset_code'] = code
        request.session['admin_reset_user_id'] = user.id
        request.session['admin_reset_expiry'] = (now + timedelta(minutes=10)).isoformat()
        request.session['admin_reset_sent_at'] = now.isoformat()

        from main.emails import send_admin_reset_code
        send_admin_reset_code(user, code)

        messages.success(request, 'A verification code has been sent to your email.')
        return redirect('admin_reset_otp')

    return render(request, 'my-admin/forgot_password.html')


def admin_reset_otp(request):
    """Step 2 – admin enters the 6-digit code."""
    if 'admin_reset_code' not in request.session:
        return redirect('admin_login')

    # Expired?
    expiry = datetime.fromisoformat(request.session['admin_reset_expiry'])
    if timezone.now() > expiry:
        for key in ('admin_reset_code', 'admin_reset_user_id', 'admin_reset_expiry', 'admin_reset_sent_at'):
            request.session.pop(key, None)
        messages.error(request, 'Verification code has expired. Please try again.')
        return redirect('admin_forgot_password')

    if request.method == 'POST':
        if request.POST.get('action') == 'resend':
            sent_at = datetime.fromisoformat(request.session['admin_reset_sent_at'])
            if (timezone.now() - sent_at).total_seconds() < 30:
                messages.error(request, 'Please wait before requesting a new code.')
            else:
                code = f"{random.randint(100000, 999999)}"
                now = timezone.now()
                request.session['admin_reset_code'] = code
                request.session['admin_reset_expiry'] = (now + timedelta(minutes=10)).isoformat()
                request.session['admin_reset_sent_at'] = now.isoformat()

                user = User.objects.get(id=request.session['admin_reset_user_id'])
                from main.emails import send_admin_reset_code
                send_admin_reset_code(user, code)
                messages.success(request, 'A new code has been sent to your email.')
            return redirect('admin_reset_otp')

        # Verify code
        entered_code = request.POST.get('code', '').strip()
        if entered_code == request.session['admin_reset_code']:
            # Code correct — let them set a new password
            request.session['admin_reset_verified'] = True
            request.session.pop('admin_reset_code', None)
            request.session.pop('admin_reset_expiry', None)
            request.session.pop('admin_reset_sent_at', None)
            return redirect('admin_reset_password')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')

    # Build masked email for the template
    user = User.objects.get(id=request.session['admin_reset_user_id'])
    email = user.email or ''
    if '@' in email:
        local, domain = email.split('@', 1)
        masked = (local[:2] + '***' + local[-1]) if len(local) > 3 else (local[0] + '***')
        masked_email = masked + '@' + domain
    else:
        masked_email = email

    sent_at = datetime.fromisoformat(request.session['admin_reset_sent_at'])
    resend_wait = int(max(0, 30 - (timezone.now() - sent_at).total_seconds()))

    return render(request, 'my-admin/reset_otp.html', {
        'masked_email': masked_email,
        'resend_wait': resend_wait,
    })


def admin_reset_password(request):
    """Step 3 – admin sets their new password."""
    if not request.session.get('admin_reset_verified'):
        return redirect('admin_login')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        errors = []
        if not new_password or not confirm_password:
            errors.append('Both fields are required.')
        if new_password and len(new_password) < 8:
            errors.append('Password must be at least 8 characters.')
        if new_password and new_password != confirm_password:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'my-admin/reset_password.html')

        # Update password
        user = User.objects.get(id=request.session['admin_reset_user_id'])
        user.set_password(new_password)
        user.save()

        # Clear all reset session data
        request.session.pop('admin_reset_user_id', None)
        request.session.pop('admin_reset_verified', None)

        messages.success(request, 'Password has been reset successfully. Please login.')
        return redirect('admin_login')

    return render(request, 'my-admin/reset_password.html')


@admin_required
def admin_logout(request):
    """Logout admin user by clearing JWT cookies."""
    messages.success(request, 'You have been logged out successfully.')
    response = redirect('admin_login')
    return clear_jwt_cookies(response)


@admin_required
def admin_dashboard(request):
    """Admin dashboard view."""
    from main.models import Job, JobApplication

    total_users = User.objects.filter(role='user').count()
    total_jobs = Job.objects.filter(status='active').count()
    total_applications = JobApplication.objects.count()
    pending_applications = JobApplication.objects.filter(status='pending').count()

    # Recent applications (latest 5)
    recent_applications = JobApplication.objects.select_related('job').order_by('-created_at')[:5]

    # Application status breakdown
    app_status = {
        'pending': JobApplication.objects.filter(status='pending').count(),
        'reviewed': JobApplication.objects.filter(status='reviewed').count(),
        'shortlisted': JobApplication.objects.filter(status='shortlisted').count(),
        'accepted': JobApplication.objects.filter(status='accepted').count(),
        'rejected': JobApplication.objects.filter(status='rejected').count(),
    }

    context = {
        'user': request.user,
        'total_users': total_users,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'recent_applications': recent_applications,
        'app_status': app_status,
    }
    return render(request, 'my-admin/dashboard.html', context)


# =============================================================================
# USER AUTHENTICATION
# =============================================================================

@guest_only(redirect_to='home')
def user_register(request):
    """Register a new user."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Validation
        errors = []
        password_error = ''

        if not username:
            errors.append('Username is required.')
        if not email:
            errors.append('Email is required.')
        if not password:
            errors.append('Password is required.')

        if password and len(password) < 6:
            password_error = 'Password must be at least 6 characters.'

        if password and password != password2:
            password_error = 'Passwords do not match.'

        # Check uniqueness
        if username and User.objects.filter(username=username).exists():
            errors.append('Username already exists.')

        if email and User.objects.filter(email=email).exists():
            errors.append('Email already registered.')

        if errors or password_error:
            for error in errors:
                messages.error(request, error)
            return render(request, 'user/register.html', {
                'form_data': {
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                },
                'password_error': password_error,
            })

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number if phone_number else None,
                role='user',
                is_staff=False,
            )
            UserDocument.objects.create(user=user)

            # Send OTP — user must verify before onboarding
            code = f"{random.randint(100000, 999999)}"
            now = timezone.now()
            request.session['otp_code'] = code
            request.session['otp_user_id'] = user.id
            request.session['otp_expiry'] = (now + timedelta(minutes=10)).isoformat()
            request.session['otp_sent_at'] = now.isoformat()
            request.session['otp_next_page'] = 'complete_profile'

            from main.emails import send_verification_code
            send_verification_code(user, code)

            messages.success(request, 'Account created! Please verify your email to continue.')
            return redirect('verify_email')

        except Exception as e:
            messages.error(request, 'Error creating account. Please try again.')
            return render(request, 'user/register.html')

    return render(request, 'user/register.html')


@guest_only(redirect_to='home')
def user_login(request):
    """
    Login view for users.
    Accepts username, email, or phone number with password.
    If the user has never verified their email (is_email_verified=False),
    an OTP is sent and they land on verify_email before being logged in.
    Already-verified users are logged in directly.
    """
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')

        if not identifier or not password:
            messages.error(request, 'Please provide login credentials.')
            return render(request, 'user/login.html')

        # Find user by username, email, or phone number
        user = User.objects.filter(
            Q(username=identifier) |
            Q(email=identifier) |
            Q(phone_number=identifier)
        ).first()

        if user and user.check_password(password):
            if user.role == 'user':
                if not user.is_email_verified:
                    # First-time verification still pending — send OTP
                    code = f"{random.randint(100000, 999999)}"
                    now = timezone.now()
                    request.session['otp_code'] = code
                    request.session['otp_user_id'] = user.id
                    request.session['otp_expiry'] = (now + timedelta(minutes=10)).isoformat()
                    request.session['otp_sent_at'] = now.isoformat()
                    request.session['otp_next_page'] = 'complete_profile' if not user.is_profile_complete else request.GET.get('next', 'home')

                    from main.emails import send_verification_code
                    send_verification_code(user, code)
                    return redirect('verify_email')

                # Already verified — log in directly
                tokens = get_tokens_for_user(user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')

                if not user.is_profile_complete:
                    next_page = 'complete_profile'
                else:
                    next_page = request.GET.get('next', 'home')

                response = redirect(next_page)
                return set_jwt_cookies(response, tokens)
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'user/login.html')


def verify_email(request):
    """
    OTP verification page shown after traditional login.
    GET  – renders the 6-box code entry form.
    POST (action=verify)  – checks the code and logs the user in on match.
    POST (action=resend)  – regenerates + re-sends the code (30 s cooldown).
    """
    # No OTP pending → back to login
    if 'otp_code' not in request.session:
        return redirect('user_login')

    # Expired?
    expiry = datetime.fromisoformat(request.session['otp_expiry'])
    if timezone.now() > expiry:
        for key in ('otp_code', 'otp_user_id', 'otp_expiry', 'otp_sent_at', 'otp_next_page'):
            request.session.pop(key, None)
        messages.error(request, 'Verification code has expired. Please login again.')
        return redirect('user_login')

    if request.method == 'POST':
        if request.POST.get('action') == 'resend':
            sent_at = datetime.fromisoformat(request.session['otp_sent_at'])
            if (timezone.now() - sent_at).total_seconds() < 30:
                messages.error(request, 'Please wait before requesting a new code.')
            else:
                code = f"{random.randint(100000, 999999)}"
                now = timezone.now()
                request.session['otp_code'] = code
                request.session['otp_expiry'] = (now + timedelta(minutes=10)).isoformat()
                request.session['otp_sent_at'] = now.isoformat()

                user = User.objects.get(id=request.session['otp_user_id'])
                from main.emails import send_verification_code
                send_verification_code(user, code)
                messages.success(request, 'A new code has been sent to your email.')
            return redirect('verify_email')

        # --- verify action ---
        entered_code = request.POST.get('code', '').strip()
        if entered_code == request.session['otp_code']:
            user = User.objects.get(id=request.session['otp_user_id'])
            next_page = request.session.get('otp_next_page', 'home')

            # Mark email as verified (one-time flag)
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save(update_fields=['is_email_verified'])

            # Clear OTP session data
            for key in ('otp_code', 'otp_user_id', 'otp_expiry', 'otp_sent_at', 'otp_next_page'):
                request.session.pop(key, None)

            tokens = get_tokens_for_user(user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            response = redirect(next_page)
            return set_jwt_cookies(response, tokens)
        else:
            messages.error(request, 'Invalid verification code. Please try again.')

    # --- build context for the template ---
    user = User.objects.get(id=request.session['otp_user_id'])
    email = user.email or ''
    if '@' in email:
        local, domain = email.split('@', 1)
        masked = (local[:2] + '***' + local[-1]) if len(local) > 3 else (local[0] + '***')
        masked_email = masked + '@' + domain
    else:
        masked_email = email

    sent_at = datetime.fromisoformat(request.session['otp_sent_at'])
    resend_wait = int(max(0, 30 - (timezone.now() - sent_at).total_seconds()))

    return render(request, 'user/verify_email.html', {
        'masked_email': masked_email,
        'resend_wait': resend_wait,
    })


@user_required
def user_logout(request):
    """Logout user by clearing JWT cookies."""
    messages.success(request, 'You have been logged out successfully.')
    response = redirect('home')
    return clear_jwt_cookies(response)


# =============================================================================
# GOOGLE OAUTH AUTHENTICATION
# =============================================================================

@guest_only(redirect_to='home')
def google_login(request):
    """
    Redirect user to Google OAuth consent screen.
    """
    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state

    # Google OAuth authorization URL
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"

    # Build the callback URL
    callback_url = request.build_absolute_uri('/auth/google/callback/')

    # OAuth parameters
    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': callback_url,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'offline',
        'prompt': 'select_account',
    }

    auth_url = f"{google_auth_url}?{urlencode(params)}"

    return redirect(auth_url)


def google_callback(request):
    """
    Handle Google OAuth callback.
    Exchange authorization code for tokens, get user info, and login/register user.
    """
    # Verify state token
    state = request.GET.get('state')
    stored_state = request.session.get('google_oauth_state')

    if not state or state != stored_state:
        messages.error(request, 'Invalid state token. Please try again.')
        return redirect('user_login')

    # Clear state from session
    del request.session['google_oauth_state']

    # Check for errors
    error = request.GET.get('error')
    if error:
        messages.error(request, f'Google login failed: {error}')
        return redirect('user_login')

    # Get authorization code
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'No authorization code received.')
        return redirect('user_login')

    # Build the callback URL (must match exactly)
    callback_url = request.build_absolute_uri('/auth/google/callback/')

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': callback_url,
    }

    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
    except requests.RequestException as e:
        messages.error(request, 'Failed to exchange authorization code.')
        return redirect('user_login')

    # Get user info from Google
    access_token = tokens.get('access_token')
    if not access_token:
        messages.error(request, 'No access token received.')
        return redirect('user_login')

    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        google_user = userinfo_response.json()
    except requests.RequestException as e:
        messages.error(request, 'Failed to get user information from Google.')
        return redirect('user_login')

    # Extract user data from Google response
    google_id = google_user.get('id')
    email = google_user.get('email')
    email_verified = google_user.get('verified_email', False)
    first_name = google_user.get('given_name', '')
    last_name = google_user.get('family_name', '')
    picture_url = google_user.get('picture', '')

    if not email:
        messages.error(request, 'Email not provided by Google.')
        return redirect('user_login')

    if not email_verified:
        messages.error(request, 'Google email is not verified. Please verify your email and try again.')
        return redirect('user_login')

    # Try to find existing user by google_id or email
    user = User.objects.filter(Q(google_id=google_id) | Q(email=email)).first()

    if user:
        # Existing user - link Google ID if not already linked
        if not user.google_id:
            user.google_id = google_id

        # Update profile picture URL if not set
        if picture_url and not user.profile_picture_url and not user.profile_picture:
            user.profile_picture_url = picture_url

        user.save()

        # Check if user is not admin
        if user.role != 'user':
            messages.error(request, 'This account cannot login here.')
            return redirect('user_login')

    else:
        # Create new user
        # Generate a unique username from email
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            google_id=google_id,
            auth_provider='google',
            profile_picture_url=picture_url,
            role='user',
            is_active=True,
            is_email_verified=True,   # Google already verified the email
        )
        # Set unusable password for Google users
        user.set_unusable_password()
        user.save()
        UserDocument.objects.create(user=user)

    # Generate JWT tokens
    jwt_tokens = get_tokens_for_user(user)

    messages.success(request, f'Welcome, {user.first_name or user.username}!')

    # Redirect to profile completion if not done yet
    if not user.is_profile_complete:
        response = redirect('complete_profile')
    else:
        response = redirect('home')

    return set_jwt_cookies(response, jwt_tokens)


# =============================================================================
# USER PROFILE
# =============================================================================

@user_required
def user_profile(request):
    """User profile view."""
    document, _ = UserDocument.objects.get_or_create(user=request.user)
    context = {
        'user': request.user,
        'document': document,
    }
    return render(request, 'user/profile.html', context)


@user_required
def edit_profile(request):
    """User edit profile view."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        profile_picture = request.FILES.get('profile_picture')
        skill_names = [s.strip() for s in request.POST.getlist('user_skills') if s.strip()]

        errors = []

        if not email:
            errors.append('Email is required.')

        if email and User.objects.filter(email=email).exclude(id=request.user.id).exists():
            errors.append('This email is already in use.')

        if phone_number and User.objects.filter(phone_number=phone_number).exclude(id=request.user.id).exists():
            errors.append('This phone number is already in use.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'user/edit_profile.html', {
                'user': request.user,
                'user_skills': skill_names,
            })

        try:
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone_number = phone_number if phone_number else None
            user.address = address

            if profile_picture:
                user.profile_picture = profile_picture

            user.save()

            # Save user skills
            UserSkill.objects.filter(user=user).delete()
            for name in skill_names:
                UserSkill.objects.create(user=user, name=name)

            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')

        except Exception as e:
            messages.error(request, 'Error updating profile. Please try again.')
            return render(request, 'user/edit_profile.html', {
                'user': request.user,
                'user_skills': skill_names,
            })

    # Pre-populate with current skills
    current_skills = list(request.user.user_skills.values_list('name', flat=True))
    return render(request, 'user/edit_profile.html', {
        'user': request.user,
        'user_skills': current_skills,
    })


@user_required
def change_password(request):
    """User change password view."""
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        errors = []

        if not old_password or not new_password or not confirm_password:
            errors.append('All fields are required.')

        if old_password and not request.user.check_password(old_password):
            errors.append('Current password is incorrect.')

        if new_password and new_password != confirm_password:
            errors.append('New passwords do not match.')

        if new_password and old_password == new_password:
            errors.append('New password must be different from current password.')

        if new_password and len(new_password) < 8:
            errors.append('New password must be at least 8 characters long.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'user/change_password.html')

        try:
            user = request.user
            user.set_password(new_password)
            user.save()

            # Generate new tokens since password changed
            tokens = get_tokens_for_user(user)

            messages.success(request, 'Password changed successfully!')
            response = redirect('user_profile')
            return set_jwt_cookies(response, tokens)

        except Exception as e:
            messages.error(request, 'Error changing password. Please try again.')
            return render(request, 'user/change_password.html')

    return render(request, 'user/change_password.html')


# =============================================================================
# PROFILE COMPLETION
# =============================================================================

@user_required
def complete_profile(request):
    """Profile completion page shown after first login."""
    user = request.user
    document, _ = UserDocument.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Handle skip
        if request.POST.get('action') == 'skip':
            user.is_profile_complete = True
            user.save()
            return redirect('home')

        # Get form data
        phone_number = request.POST.get('phone_number', '').strip()
        passport_number = request.POST.get('passport_number', '').strip()
        profile_picture = request.FILES.get('profile_picture')
        passport_photo = request.FILES.get('passport_photo')
        cv = request.FILES.get('cv')
        skill_names = [s.strip() for s in request.POST.getlist('user_skills') if s.strip()]

        # Validate files
        errors = []
        if profile_picture:
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if profile_picture.content_type not in allowed_types:
                errors.append('Profile picture must be JPG or PNG.')
            if profile_picture.size > 5 * 1024 * 1024:
                errors.append('Profile picture must be less than 5MB.')

        if passport_photo:
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if passport_photo.content_type not in allowed_types:
                errors.append('Passport photo must be JPG or PNG.')
            if passport_photo.size > 5 * 1024 * 1024:
                errors.append('Passport photo must be less than 5MB.')

        if cv:
            allowed_cv_types = ['application/pdf', 'application/msword',
                                'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if cv.content_type not in allowed_cv_types:
                errors.append('CV must be PDF or Word document.')
            if cv.size > 10 * 1024 * 1024:
                errors.append('CV must be less than 10MB.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'user/complete_profile.html', {
                'document': document,
                'user_skills': skill_names,
            })

        # Save to User
        if phone_number:
            user.phone_number = phone_number
        if profile_picture:
            user.profile_picture = profile_picture
        user.is_profile_complete = True
        user.save()

        # Save user skills
        UserSkill.objects.filter(user=user).delete()
        for name in skill_names:
            UserSkill.objects.create(user=user, name=name)

        # Save documents
        if passport_number:
            document.passport_number = passport_number
        if passport_photo:
            document.passport_photo = passport_photo
        if cv:
            document.cv = cv
        document.save()

        messages.success(request, 'Profile completed successfully!')
        return redirect('home')

    context = {
        'document': document,
        'user_skills': [],
    }
    return render(request, 'user/complete_profile.html', context)


@user_required
def edit_documents(request):
    """User edit documents view."""
    document, _ = UserDocument.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        passport_number = request.POST.get('passport_number', '').strip()
        passport_photo = request.FILES.get('passport_photo')
        cv = request.FILES.get('cv')

        errors = []

        if passport_photo:
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if passport_photo.content_type not in allowed_types:
                errors.append('Passport photo must be JPG or PNG.')
            if passport_photo.size > 5 * 1024 * 1024:
                errors.append('Passport photo must be less than 5MB.')

        if cv:
            allowed_cv_types = ['application/pdf', 'application/msword',
                                'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if cv.content_type not in allowed_cv_types:
                errors.append('CV must be PDF or Word document.')
            if cv.size > 10 * 1024 * 1024:
                errors.append('CV must be less than 10MB.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'user/edit_documents.html', {'document': document})

        document.passport_number = passport_number if passport_number else None
        if passport_photo:
            document.passport_photo = passport_photo
        if cv:
            document.cv = cv
        document.save()

        messages.success(request, 'Documents updated successfully!')
        return redirect('user_profile')

    return render(request, 'user/edit_documents.html', {'document': document})


# =============================================================================
# PLACEHOLDER VIEWS (to be implemented later)
# =============================================================================

def home(request):
    """Home page view."""
    from main.models import Job

    # Get latest active jobs for home page carousel
    featured_jobs = Job.objects.filter(status='active').order_by('-is_urgent', '-created_at')[:6]

    context = {
        'featured_jobs': featured_jobs,
    }
    return render(request, 'user/home.html', context)
