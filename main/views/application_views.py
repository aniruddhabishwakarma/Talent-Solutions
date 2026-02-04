from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from main.models import JobApplication, Job
from main.decorators import admin_required
from main.emails import send_application_status_update, send_rejection_email


@admin_required
def application_list(request):
    """List all job applications."""
    applications = JobApplication.objects.select_related('job', 'user').prefetch_related('skills').order_by('-created_at')

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        applications = applications.filter(status=status)

    # Filter by job
    job_id = request.GET.get('job', '')
    if job_id:
        applications = applications.filter(job_id=job_id)

    # Search
    search = request.GET.get('search', '').strip()
    if search:
        applications = applications.filter(
            Q(full_name__icontains=search) |
            Q(contact_number__icontains=search) |
            Q(passport_number__icontains=search) |
            Q(job__title__icontains=search)
        )

    # Get jobs for filter dropdown
    jobs = Job.objects.all().order_by('title')

    # Pagination
    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Status counts
    status_counts = {
        'all': JobApplication.objects.count(),
        'pending': JobApplication.objects.filter(status='pending').count(),
        'reviewed': JobApplication.objects.filter(status='reviewed').count(),
        'shortlisted': JobApplication.objects.filter(status='shortlisted').count(),
        'accepted': JobApplication.objects.filter(status='accepted').count(),
        'rejected': JobApplication.objects.filter(status='rejected').count(),
    }

    context = {
        'applications': page_obj,
        'jobs': jobs,
        'selected_status': status,
        'selected_job': job_id,
        'search': search,
        'status_counts': status_counts,
    }
    return render(request, 'my-admin/applications/list.html', context)


@admin_required
def application_detail(request, pk):
    """View application details."""
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'user').prefetch_related('skills'),
        pk=pk
    )

    context = {
        'application': application,
    }
    return render(request, 'my-admin/applications/detail.html', context)


@admin_required
def application_update_status(request, pk):
    """Update application status."""
    application = get_object_or_404(JobApplication, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '').strip()
        rejection_reason = request.POST.get('rejection_reason', '').strip()

        if new_status in dict(JobApplication._meta.get_field('status').choices):
            # Require rejection reason when rejecting
            if new_status == 'rejected' and not rejection_reason:
                messages.error(request, 'Please provide a reason for rejection.')
                return redirect('application_detail', pk=pk)

            application.status = new_status
            if admin_notes:
                application.admin_notes = admin_notes
            if new_status == 'rejected':
                application.rejection_reason = rejection_reason
            application.save()

            if new_status == 'rejected':
                send_rejection_email(application)
            else:
                send_application_status_update(application)

            messages.success(request, f'Application status updated to {application.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')

    return redirect('application_detail', pk=pk)


@admin_required
def application_delete(request, pk):
    """Delete an application."""
    application = get_object_or_404(JobApplication, pk=pk)

    if request.method == 'POST':
        job_title = application.job.title
        application.delete()
        messages.success(request, f'Application for "{job_title}" has been deleted.')
        return redirect('application_list')

    return redirect('application_detail', pk=pk)
