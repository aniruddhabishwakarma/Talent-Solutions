from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import Job, Skill, COUNTRY_CHOICES
from main.decorators import admin_required


@admin_required
def job_list(request):
    """List all jobs."""
    jobs = Job.objects.all().select_related('posted_by').prefetch_related('skills')

    # Get filter values
    status_filter = request.GET.get('status', '')
    country_filter = request.GET.get('country', '')
    urgent_filter = request.GET.get('urgent', '')

    # Apply filters
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    if country_filter:
        jobs = jobs.filter(country=country_filter)
    if urgent_filter == '1':
        jobs = jobs.filter(is_urgent=True)

    context = {
        'jobs': jobs,
        'countries': COUNTRY_CHOICES,
        'status_filter': status_filter,
        'country_filter': country_filter,
        'urgent_filter': urgent_filter,
    }
    return render(request, 'my-admin/jobs/list.html', context)


@admin_required
def job_add(request):
    """Add a new job."""
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        description = request.POST.get('description', '').strip()
        country = request.POST.get('country', '')
        city = request.POST.get('city', '').strip()
        contract_duration = request.POST.get('contract_duration', '')
        fooding = request.POST.get('fooding') == 'yes'
        lodging = request.POST.get('lodging') == 'yes'
        overtime_available = request.POST.get('overtime_available') == 'yes'
        salary = request.POST.get('salary', '')
        salary_currency = request.POST.get('salary_currency', 'USD')
        education = request.POST.get('education', '').strip()
        experience_years = request.POST.get('experience_years', '0')
        age_min = request.POST.get('age_min', '')
        age_max = request.POST.get('age_max', '')
        gender = request.POST.get('gender', 'any')
        vacancies = request.POST.get('vacancies', '1')
        status = request.POST.get('status', 'draft')
        deadline = request.POST.get('deadline', '')
        is_urgent = request.POST.get('is_urgent') == 'on'
        skills_text = request.POST.get('skills_text', '')

        # Validation
        errors = []
        if not title:
            errors.append('Job title is required.')
        if not company_name:
            errors.append('Company name is required.')
        if not description:
            errors.append('Job description is required.')
        if not country:
            errors.append('Country is required.')
        if not salary:
            errors.append('Salary is required.')
        if not deadline:
            errors.append('Deadline is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'my-admin/jobs/add.html', {
                'countries': COUNTRY_CHOICES,
                'form_data': request.POST,
            })

        try:
            job = Job(
                title=title,
                company_name=company_name,
                description=description,
                country=country,
                city=city if city else None,
                contract_duration=int(contract_duration) if contract_duration else None,
                fooding=fooding,
                lodging=lodging,
                overtime_available=overtime_available,
                salary=salary,
                salary_currency=salary_currency,
                education=education if education else None,
                experience_years=int(experience_years) if experience_years else 0,
                age_min=int(age_min) if age_min else None,
                age_max=int(age_max) if age_max else None,
                gender=gender,
                vacancies=int(vacancies) if vacancies else 1,
                status=status,
                deadline=deadline,
                is_urgent=is_urgent,
                posted_by=request.user,
            )
            job.save()

            # Add skills - create if they don't exist
            if skills_text:
                skill_names = [s.strip() for s in skills_text.split(',') if s.strip()]
                skill_objects = []
                for name in skill_names:
                    skill, created = Skill.objects.get_or_create(name=name)
                    skill_objects.append(skill)
                job.skills.set(skill_objects)

            messages.success(request, f'Job "{title}" created successfully!')
            return redirect('job_list')

        except Exception as e:
            messages.error(request, f'Error creating job: {str(e)}')
            return render(request, 'my-admin/jobs/add.html', {
                'countries': COUNTRY_CHOICES,
                'form_data': request.POST,
            })

    context = {
        'countries': COUNTRY_CHOICES,
    }
    return render(request, 'my-admin/jobs/add.html', context)


@admin_required
def job_edit(request, slug):
    """Edit a job."""
    job = get_object_or_404(Job, slug=slug)

    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        description = request.POST.get('description', '').strip()
        country = request.POST.get('country', '')
        city = request.POST.get('city', '').strip()
        contract_duration = request.POST.get('contract_duration', '')
        fooding = request.POST.get('fooding') == 'yes'
        lodging = request.POST.get('lodging') == 'yes'
        overtime_available = request.POST.get('overtime_available') == 'yes'
        salary = request.POST.get('salary', '')
        salary_currency = request.POST.get('salary_currency', 'USD')
        education = request.POST.get('education', '').strip()
        experience_years = request.POST.get('experience_years', '0')
        age_min = request.POST.get('age_min', '')
        age_max = request.POST.get('age_max', '')
        gender = request.POST.get('gender', 'any')
        vacancies = request.POST.get('vacancies', '1')
        status = request.POST.get('status', 'draft')
        deadline = request.POST.get('deadline', '')
        is_urgent = request.POST.get('is_urgent') == 'on'
        skills_text = request.POST.get('skills_text', '')

        # Validation
        errors = []
        if not title:
            errors.append('Job title is required.')
        if not company_name:
            errors.append('Company name is required.')
        if not description:
            errors.append('Job description is required.')
        if not country:
            errors.append('Country is required.')
        if not salary:
            errors.append('Salary is required.')
        if not deadline:
            errors.append('Deadline is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'my-admin/jobs/edit.html', {
                'job': job,
                'countries': COUNTRY_CHOICES,
            })

        try:
            job.title = title
            job.company_name = company_name
            job.description = description
            job.country = country
            job.city = city if city else None
            job.contract_duration = int(contract_duration) if contract_duration else None
            job.fooding = fooding
            job.lodging = lodging
            job.overtime_available = overtime_available
            job.salary = salary
            job.salary_currency = salary_currency
            job.education = education if education else None
            job.experience_years = int(experience_years) if experience_years else 0
            job.age_min = int(age_min) if age_min else None
            job.age_max = int(age_max) if age_max else None
            job.gender = gender
            job.vacancies = int(vacancies) if vacancies else 1
            job.status = status
            job.deadline = deadline
            job.is_urgent = is_urgent
            job.save()

            # Update skills - create if they don't exist
            if skills_text:
                skill_names = [s.strip() for s in skills_text.split(',') if s.strip()]
                skill_objects = []
                for name in skill_names:
                    skill, created = Skill.objects.get_or_create(name=name)
                    skill_objects.append(skill)
                job.skills.set(skill_objects)
            else:
                job.skills.clear()

            messages.success(request, f'Job "{title}" updated successfully!')
            return redirect('job_list')

        except Exception as e:
            messages.error(request, f'Error updating job: {str(e)}')
            return render(request, 'my-admin/jobs/edit.html', {
                'job': job,
                'countries': COUNTRY_CHOICES,
            })

    context = {
        'job': job,
        'countries': COUNTRY_CHOICES,
    }
    return render(request, 'my-admin/jobs/edit.html', context)


@admin_required
def job_delete(request, slug):
    """Delete a job."""
    job = get_object_or_404(Job, slug=slug)

    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f'Job "{title}" deleted successfully!')
        return redirect('job_list')

    return render(request, 'my-admin/jobs/delete.html', {'job': job})


@admin_required
def job_detail(request, slug):
    """View job details."""
    job = get_object_or_404(Job, slug=slug)
    return render(request, 'my-admin/jobs/detail.html', {'job': job})
