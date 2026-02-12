from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import ContactMessage
from main.decorators import admin_required


@admin_required
def contact_messages_list(request):
    """
    Display all contact messages with filtering options
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '').strip()

    # Base queryset
    messages_list = ContactMessage.objects.all()

    # Apply filters
    if status_filter == 'unread':
        messages_list = messages_list.filter(is_read=False)
    elif status_filter == 'read':
        messages_list = messages_list.filter(is_read=True)
    elif status_filter == 'replied':
        messages_list = messages_list.filter(replied_at__isnull=False)

    # Apply search
    if search_query:
        messages_list = messages_list.filter(
            full_name__icontains=search_query
        ) | messages_list.filter(
            email__icontains=search_query
        ) | messages_list.filter(
            subject__icontains=search_query
        )

    # Get counts for stats
    total_count = ContactMessage.objects.count()
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    read_count = ContactMessage.objects.filter(is_read=True).count()
    replied_count = ContactMessage.objects.filter(replied_at__isnull=False).count()

    context = {
        'messages_list': messages_list,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_count': total_count,
        'unread_count': unread_count,
        'read_count': read_count,
        'replied_count': replied_count,
    }

    return render(request, 'my-admin/contact/list.html', context)


@admin_required
def contact_message_detail(request, pk):
    """
    View a single contact message
    """
    message = get_object_or_404(ContactMessage, pk=pk)

    # Mark as read when viewed
    if not message.is_read:
        message.mark_as_read()

    if request.method == 'POST':
        # Update admin notes
        admin_notes = request.POST.get('admin_notes', '').strip()
        message.admin_notes = admin_notes

        # Mark as replied if checkbox is checked
        if request.POST.get('mark_replied'):
            message.mark_as_replied()

        message.save()
        messages.success(request, 'Message updated successfully!')
        return redirect('contact_messages_list')

    context = {
        'message': message,
    }

    return render(request, 'my-admin/contact/detail.html', context)


@admin_required
def contact_message_delete(request, pk):
    """
    Delete a contact message
    """
    message = get_object_or_404(ContactMessage, pk=pk)

    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Contact message deleted successfully!')
        return redirect('contact_messages_list')

    context = {
        'message': message,
    }

    return render(request, 'my-admin/contact/delete.html', context)


@admin_required
def contact_message_toggle_read(request, pk):
    """
    Toggle read/unread status via AJAX
    """
    message = get_object_or_404(ContactMessage, pk=pk)
    message.is_read = not message.is_read
    message.save()

    messages.success(request, f'Message marked as {"read" if message.is_read else "unread"}!')
    return redirect('contact_messages_list')
