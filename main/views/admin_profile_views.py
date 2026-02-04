from django.shortcuts import render, redirect
from django.contrib import messages
from main.models import User
from main.decorators import admin_required
from .auth_views import get_tokens_for_user, set_jwt_cookies


@admin_required
def admin_profile(request):
    """Admin profile view."""
    return render(request, 'my-admin/profile/profile.html', {'user': request.user})


@admin_required
def admin_edit_profile(request):
    """Admin edit profile view."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        profile_picture = request.FILES.get('profile_picture')

        errors = []

        if not email:
            errors.append('Email is required.')

        # Check if email is taken by another user
        if email and User.objects.filter(email=email).exclude(id=request.user.id).exists():
            errors.append('This email is already in use.')

        # Check if phone is taken by another user
        if phone_number and User.objects.filter(phone_number=phone_number).exclude(id=request.user.id).exists():
            errors.append('This phone number is already in use.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'my-admin/profile/edit_profile.html', {'user': request.user})

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

            messages.success(request, 'Profile updated successfully!')
            return redirect('admin_profile')

        except Exception as e:
            messages.error(request, 'Error updating profile. Please try again.')
            return render(request, 'my-admin/profile/edit_profile.html', {'user': request.user})

    return render(request, 'my-admin/profile/edit_profile.html', {'user': request.user})


@admin_required
def admin_change_password(request):
    """Admin change password view."""
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
            return render(request, 'my-admin/profile/change_password.html')

        try:
            user = request.user
            user.set_password(new_password)
            user.save()

            # Generate new tokens since password changed
            tokens = get_tokens_for_user(user)

            messages.success(request, 'Password changed successfully!')
            response = redirect('admin_profile')
            return set_jwt_cookies(response, tokens)

        except Exception as e:
            messages.error(request, 'Error changing password. Please try again.')
            return render(request, 'my-admin/profile/change_password.html')

    return render(request, 'my-admin/profile/change_password.html')
