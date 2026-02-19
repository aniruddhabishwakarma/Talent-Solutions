from django.shortcuts import render, redirect
from django.contrib import messages
from main.models import Company
from main.decorators import admin_required


@admin_required
def company_profile(request):
    """View company profile."""
    company = Company.get_company()
    return render(request, 'my-admin/company/profile.html', {'company': company})


@admin_required
def company_edit(request):
    """Edit company profile."""
    company = Company.get_company()

    if request.method == 'POST':
        # Basic Information
        company.company_name = request.POST.get('company_name', '').strip()
        company.tagline = request.POST.get('tagline', '').strip() or None
        company.website = request.POST.get('website', '').strip() or None
        company.industry = request.POST.get('industry', '').strip() or None

        # Contact Details
        company.email = request.POST.get('email', '').strip()
        company.phone = request.POST.get('phone', '').strip()
        company.alternate_phone = request.POST.get('alternate_phone', '').strip() or None
        company.address = request.POST.get('address', '').strip()
        company.city = request.POST.get('city', '').strip()
        company.state = request.POST.get('state', '').strip()
        company.country = request.POST.get('country', '').strip()
        company.postal_code = request.POST.get('postal_code', '').strip()

        # Company Details
        company.about = request.POST.get('about', '').strip() or None
        founded_year = request.POST.get('founded_year', '').strip()
        company.founded_year = int(founded_year) if founded_year else None
        company.company_size = request.POST.get('company_size', '').strip() or None
        company.company_type = request.POST.get('company_type', '').strip() or None

        # Social Media
        company.facebook = request.POST.get('facebook', '').strip() or None
        company.twitter = request.POST.get('twitter', '').strip() or None
        company.instagram = request.POST.get('instagram', '').strip() or None
        company.tiktok = request.POST.get('tiktok', '').strip() or None
        company.youtube = request.POST.get('youtube', '').strip() or None
        company.whatsapp = request.POST.get('whatsapp', '').strip() or None

        # Legal Information
        company.registration_number = request.POST.get('registration_number', '').strip() or None
        company.license_number = request.POST.get('license_number', '').strip() or None
        company.pan_number = request.POST.get('pan_number', '').strip() or None

        # Google Maps
        company.google_maps_embed = request.POST.get('google_maps_embed', '').strip() or None

        # Logo
        if request.FILES.get('logo'):
            company.logo = request.FILES.get('logo')

        # Validation
        errors = []
        if not company.company_name:
            errors.append('Company name is required.')
        if not company.email:
            errors.append('Email is required.')
        if not company.phone:
            errors.append('Phone number is required.')
        if not company.address:
            errors.append('Address is required.')
        if not company.city:
            errors.append('City is required.')
        if not company.state:
            errors.append('State is required.')
        if not company.country:
            errors.append('Country is required.')
        if not company.postal_code:
            errors.append('Postal code is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'my-admin/company/edit.html', {'company': company})

        try:
            company.save()
            messages.success(request, 'Company profile updated successfully!')
            return redirect('company_profile')
        except Exception as e:
            messages.error(request, 'Error updating company profile. Please try again.')
            return render(request, 'my-admin/company/edit.html', {'company': company})

    return render(request, 'my-admin/company/edit.html', {'company': company})
