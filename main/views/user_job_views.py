from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from main.models import Job, Skill, JobApplication, UserDocument
from main.decorators import user_required
from main.emails import send_application_confirmation, send_new_application_alert


def user_jobs_list(request):
    """Public jobs listing page."""
    # Get only active jobs
    jobs = Job.objects.filter(status='active').order_by('-is_urgent', '-created_at')

    # Search
    search = request.GET.get('search', '').strip()
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(company_name__icontains=search) |
            Q(description__icontains=search)
        )

    # Country filter
    country = request.GET.get('country', '')
    if country:
        jobs = jobs.filter(country=country)

    # Get unique countries for filter dropdown
    countries = Job.objects.filter(status='active').values_list('country', flat=True).distinct()
    from main.models.job_model import COUNTRY_CHOICES
    country_dict = dict(COUNTRY_CHOICES)
    available_countries = [(code, country_dict.get(code, code)) for code in countries]
    available_countries.sort(key=lambda x: x[1])

    # Pagination
    paginator = Paginator(jobs, 9)  # 9 jobs per page (3x3 grid)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'jobs': page_obj,
        'search': search,
        'selected_country': country,
        'countries': available_countries,
        'total_jobs': paginator.count,
    }
    return render(request, 'user/jobs/list.html', context)


def user_job_detail(request, slug):
    """Public job detail page."""
    job = get_object_or_404(Job, slug=slug, status='active')

    # Get user's latest application for this job (if any)
    user_application = None
    if request.user.is_authenticated:
        user_application = JobApplication.objects.filter(job=job, user=request.user).order_by('-created_at').first()

    # Get related jobs (same country or similar skills)
    related_jobs = Job.objects.filter(
        status='active'
    ).exclude(id=job.id).filter(
        Q(country=job.country) | Q(skills__in=job.skills.all())
    ).distinct()[:3]

    context = {
        'job': job,
        'related_jobs': related_jobs,
        'user_application': user_application,
    }
    return render(request, 'user/jobs/detail.html', context)


def apply_for_job(request, slug):
    """Job application page."""
    job = get_object_or_404(Job, slug=slug, status='active')
    skills = Skill.objects.all()

    # Check if job deadline has passed
    from django.utils import timezone
    if job.deadline < timezone.now().date():
        messages.error(request, 'This job application deadline has passed.')
        return redirect('user_job_detail', slug=slug)

    # Check if user has already applied (if logged in) — allow reapply only if rejected
    if request.user.is_authenticated:
        existing_application = JobApplication.objects.filter(job=job, user=request.user).order_by('-created_at').first()
        if existing_application and existing_application.status != 'rejected':
            messages.info(request, 'You have already applied for this job.')
            return redirect('user_job_detail', slug=slug)

    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('full_name', '').strip()
        contact_number = request.POST.get('contact_number', '').strip()
        passport_number = request.POST.get('passport_number', '').strip()
        passport_photo = request.FILES.get('passport_photo')
        selected_skills = request.POST.getlist('skills')
        cv = request.FILES.get('cv')

        # Check if user already has a passport photo saved
        existing_passport_photo = None
        if request.user.is_authenticated:
            try:
                existing_passport_photo = request.user.documents.passport_photo
            except UserDocument.DoesNotExist:
                pass

        # Validation
        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not contact_number:
            errors.append('Contact number is required.')
        if not passport_number:
            errors.append('Passport number is required.')
        if not passport_photo and not existing_passport_photo:
            errors.append('Passport photo is required.')
        if not selected_skills:
            errors.append('Please select at least one skill.')

        # Validate passport photo type
        if passport_photo:
            allowed_image_types = ['image/jpeg', 'image/png', 'image/jpg']
            if passport_photo.content_type not in allowed_image_types:
                errors.append('Passport photo must be a JPG or PNG image.')
            if passport_photo.size > 5 * 1024 * 1024:  # 5MB limit
                errors.append('Passport photo must be less than 5MB.')

        # Validate CV type if provided
        if cv:
            allowed_cv_types = ['application/pdf', 'application/msword',
                               'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if cv.content_type not in allowed_cv_types:
                errors.append('CV must be a PDF or Word document.')
            if cv.size > 10 * 1024 * 1024:  # 10MB limit
                errors.append('CV must be less than 10MB.')

        if errors:
            for error in errors:
                messages.error(request, error)
            context = {
                'job': job,
                'skills': skills,
                'form_data': {
                    'full_name': full_name,
                    'contact_number': contact_number,
                    'passport_number': passport_number,
                    'selected_skills': selected_skills,
                }
            }
            return render(request, 'user/jobs/apply.html', context)

        # Create application
        application = JobApplication(
            job=job,
            full_name=full_name,
            contact_number=contact_number,
            passport_number=passport_number,
            passport_photo=passport_photo if passport_photo else existing_passport_photo,
        )

        # Set user if logged in
        if request.user.is_authenticated:
            application.user = request.user

        # Set CV if provided
        if cv:
            application.cv = cv

        application.save()

        # Add skills (after saving the application)
        for skill_id in selected_skills:
            try:
                skill = Skill.objects.get(id=skill_id)
                application.skills.add(skill)
            except Skill.DoesNotExist:
                pass

        # Save info back to user profile if not already set
        if request.user.is_authenticated:
            user = request.user
            if not user.phone_number and contact_number:
                user.phone_number = contact_number
                user.save()

            doc, _ = UserDocument.objects.get_or_create(user=user)
            doc_updated = False
            if not doc.passport_number and passport_number:
                doc.passport_number = passport_number
                doc_updated = True
            if not doc.passport_photo and passport_photo:
                doc.passport_photo = passport_photo
                doc_updated = True
            if not doc.cv and cv:
                doc.cv = cv
                doc_updated = True
            if doc_updated:
                doc.save()

        # Send confirmation to applicant + alert to admin
        send_application_confirmation(application)
        send_new_application_alert(application)

        messages.success(request, 'Your application has been submitted successfully!')
        return redirect('application_success', slug=slug)

    # Pre-fill from user profile if logged in
    form_data = {}
    existing_passport_photo = None
    existing_cv = None
    rejection_reason = None
    if request.user.is_authenticated:
        form_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
            'contact_number': request.user.phone_number or '',
        }
        try:
            doc = request.user.documents
            form_data['passport_number'] = doc.passport_number or ''
            existing_passport_photo = doc.passport_photo if doc.passport_photo else None
            existing_cv = doc.cv if doc.cv else None
        except UserDocument.DoesNotExist:
            pass

        # Pass rejection reason if reapplying after rejection
        if existing_application and existing_application.status == 'rejected':
            rejection_reason = existing_application.rejection_reason

    context = {
        'job': job,
        'skills': skills,
        'form_data': form_data,
        'existing_passport_photo': existing_passport_photo,
        'existing_cv': existing_cv,
        'rejection_reason': rejection_reason,
    }
    return render(request, 'user/jobs/apply.html', context)


def application_success(request, slug):
    """Application success page."""
    job = get_object_or_404(Job, slug=slug)
    return render(request, 'user/jobs/application_success.html', {'job': job})


@user_required
def user_my_applications(request):
    """List all applications submitted by the logged-in user."""
    applications = JobApplication.objects.filter(
        user=request.user
    ).select_related('job').prefetch_related('skills').order_by('-created_at')

    # Status filter
    selected_status = request.GET.get('status', '')
    if selected_status:
        applications = applications.filter(status=selected_status)

    # Status counts for filter tabs
    all_apps = JobApplication.objects.filter(user=request.user)
    status_counts = {
        'all': all_apps.count(),
        'pending': all_apps.filter(status='pending').count(),
        'reviewed': all_apps.filter(status='reviewed').count(),
        'shortlisted': all_apps.filter(status='shortlisted').count(),
        'accepted': all_apps.filter(status='accepted').count(),
        'rejected': all_apps.filter(status='rejected').count(),
    }

    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'applications': page_obj,
        'selected_status': selected_status,
        'status_counts': status_counts,
    }
    return render(request, 'user/applications/list.html', context)


@user_required
def user_application_detail(request, pk):
    """Detail view for a single application — only accessible by the owner."""
    application = get_object_or_404(
        JobApplication.objects.select_related('job').prefetch_related('skills'),
        pk=pk,
        user=request.user,
    )
    context = {
        'application': application,
    }
    return render(request, 'user/applications/detail.html', context)
