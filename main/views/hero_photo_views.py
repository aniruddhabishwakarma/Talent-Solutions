"""
Admin views for managing hero gallery photos.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import HeroPhoto
from main.decorators import admin_required


@admin_required
def hero_photo_list(request):
    """List all hero photos (admin panel)."""
    photos = HeroPhoto.objects.all().order_by('display_order', 'id')
    context = {
        'photos': photos,
        'active_count': photos.filter(is_active=True).count(),
        'inactive_count': photos.filter(is_active=False).count(),
    }
    return render(request, 'my-admin/hero-photos/list.html', context)


@admin_required
def hero_photo_add(request):
    """Add a new hero photo."""
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '').strip()
        display_order = request.POST.get('display_order', '0')
        is_active = request.POST.get('is_active') == 'on'

        if not image:
            messages.error(request, 'Image is required.')
            return redirect('hero_photo_add')

        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if image.content_type not in allowed_types:
            messages.error(request, 'Image must be JPG, PNG, or WEBP.')
            return redirect('hero_photo_add')

        if image.size > 10 * 1024 * 1024:
            messages.error(request, 'Image size must not exceed 10MB.')
            return redirect('hero_photo_add')

        try:
            HeroPhoto.objects.create(
                image=image,
                caption=caption if caption else None,
                display_order=int(display_order),
                is_active=is_active,
            )
            messages.success(request, 'Photo added successfully!')
            return redirect('hero_photo_list')
        except Exception as e:
            messages.error(request, f'Error adding photo: {str(e)}')
            return redirect('hero_photo_add')

    return render(request, 'my-admin/hero-photos/add.html')


@admin_required
def hero_photo_delete(request, pk):
    """Delete a hero photo."""
    photo = get_object_or_404(HeroPhoto, pk=pk)

    if request.method == 'POST':
        photo.delete()
        messages.success(request, 'Photo deleted successfully!')
        return redirect('hero_photo_list')

    context = {'photo': photo}
    return render(request, 'my-admin/hero-photos/delete.html', context)


@admin_required
def hero_photo_toggle(request, pk):
    """Toggle active/inactive status."""
    if request.method == 'POST':
        photo = get_object_or_404(HeroPhoto, pk=pk)
        photo.is_active = not photo.is_active
        photo.save()
        status_text = 'activated' if photo.is_active else 'deactivated'
        messages.success(request, f'Photo {status_text}!')
    return redirect('hero_photo_list')
