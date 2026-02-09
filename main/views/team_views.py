"""
Admin views for managing team members.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import TeamMember
from main.decorators import admin_required


@admin_required
def team_list(request):
    """List all team members (admin panel)."""
    members = TeamMember.objects.all().order_by('display_order', 'id')

    context = {
        'members': members,
        'active_count': members.filter(is_active=True).count(),
        'inactive_count': members.filter(is_active=False).count(),
    }
    return render(request, 'my-admin/team/list.html', context)


@admin_required
def team_add(request):
    """Add a new team member."""
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        position = request.POST.get('position', '').strip()
        bio = request.POST.get('bio', '').strip()
        photo = request.FILES.get('photo')
        facebook_url = request.POST.get('facebook_url', '').strip()
        instagram_url = request.POST.get('instagram_url', '').strip()
        whatsapp_number = request.POST.get('whatsapp_number', '').strip()
        display_order = request.POST.get('display_order', '0')
        is_active = request.POST.get('is_active') == 'on'

        # Validation
        if not name:
            messages.error(request, 'Name is required.')
            return redirect('team_add')

        if not position:
            messages.error(request, 'Position is required.')
            return redirect('team_add')

        if not bio:
            messages.error(request, 'Bio is required.')
            return redirect('team_add')

        if not photo:
            messages.error(request, 'Photo is required.')
            return redirect('team_add')

        # Validate photo file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if photo.content_type not in allowed_types:
            messages.error(request, 'Photo must be JPG, PNG, or WEBP.')
            return redirect('team_add')

        # Validate photo size (max 5MB)
        if photo.size > 5 * 1024 * 1024:
            messages.error(request, 'Photo size must not exceed 5MB.')
            return redirect('team_add')

        # Create team member
        try:
            member = TeamMember.objects.create(
                name=name,
                position=position,
                bio=bio,
                photo=photo,
                facebook_url=facebook_url if facebook_url else None,
                instagram_url=instagram_url if instagram_url else None,
                whatsapp_number=whatsapp_number if whatsapp_number else None,
                display_order=int(display_order),
                is_active=is_active,
            )
            messages.success(request, f'{name} added successfully!')
            return redirect('team_list')
        except Exception as e:
            messages.error(request, f'Error adding team member: {str(e)}')
            return redirect('team_add')

    return render(request, 'my-admin/team/add.html')


@admin_required
def team_edit(request, pk):
    """Edit an existing team member."""
    member = get_object_or_404(TeamMember, pk=pk)

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        position = request.POST.get('position', '').strip()
        bio = request.POST.get('bio', '').strip()
        photo = request.FILES.get('photo')  # Optional on edit
        facebook_url = request.POST.get('facebook_url', '').strip()
        instagram_url = request.POST.get('instagram_url', '').strip()
        whatsapp_number = request.POST.get('whatsapp_number', '').strip()
        display_order = request.POST.get('display_order', '0')
        is_active = request.POST.get('is_active') == 'on'

        # Validation
        if not name:
            messages.error(request, 'Name is required.')
            return redirect('team_edit', pk=pk)

        if not position:
            messages.error(request, 'Position is required.')
            return redirect('team_edit', pk=pk)

        if not bio:
            messages.error(request, 'Bio is required.')
            return redirect('team_edit', pk=pk)

        # Update fields
        member.name = name
        member.position = position
        member.bio = bio
        member.facebook_url = facebook_url if facebook_url else None
        member.instagram_url = instagram_url if instagram_url else None
        member.whatsapp_number = whatsapp_number if whatsapp_number else None
        member.display_order = int(display_order)
        member.is_active = is_active

        # Update photo if provided
        if photo:
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if photo.content_type not in allowed_types:
                messages.error(request, 'Photo must be JPG, PNG, or WEBP.')
                return redirect('team_edit', pk=pk)

            if photo.size > 5 * 1024 * 1024:
                messages.error(request, 'Photo size must not exceed 5MB.')
                return redirect('team_edit', pk=pk)

            member.photo = photo

        try:
            member.save()
            messages.success(request, f'{name} updated successfully!')
            return redirect('team_list')
        except Exception as e:
            messages.error(request, f'Error updating team member: {str(e)}')
            return redirect('team_edit', pk=pk)

    context = {'member': member}
    return render(request, 'my-admin/team/edit.html', context)


@admin_required
def team_delete(request, pk):
    """Delete a team member."""
    member = get_object_or_404(TeamMember, pk=pk)

    if request.method == 'POST':
        member_name = member.name
        member.delete()
        messages.success(request, f'{member_name} deleted successfully!')
        return redirect('team_list')

    context = {'member': member}
    return render(request, 'my-admin/team/delete.html', context)


@admin_required
def team_toggle_status(request, pk):
    """Quick toggle active/inactive status (AJAX-friendly)."""
    if request.method == 'POST':
        member = get_object_or_404(TeamMember, pk=pk)
        member.is_active = not member.is_active
        member.save()

        status_text = 'activated' if member.is_active else 'deactivated'
        messages.success(request, f'{member.name} {status_text}!')

    return redirect('team_list')
