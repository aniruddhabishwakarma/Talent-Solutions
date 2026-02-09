from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from main.models import User, Company, Skill, Job, JobApplication


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin configuration
    """
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_staff', 'is_active', 'created_at']
    list_filter = ['role', 'is_staff', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'address', 'profile_picture')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'address', 'email', 'first_name', 'last_name')
        }),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Company admin configuration
    """
    list_display = ['company_name', 'email', 'phone', 'city', 'country', 'updated_at']
    search_fields = ['company_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('company_name', 'logo', 'tagline', 'website', 'industry')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'alternate_phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Company Details', {
            'fields': ('about', 'founded_year', 'company_size', 'company_type')
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'instagram', 'tiktok', 'youtube', 'whatsapp')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Skill admin configuration
    """
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """
    Job admin configuration
    """
    list_display = ['title', 'country', 'salary', 'salary_currency', 'status', 'deadline', 'is_urgent', 'fooding', 'lodging', 'overtime_available']
    list_filter = ['status', 'country', 'is_urgent', 'gender', 'fooding', 'lodging', 'overtime_available']
    search_fields = ['title', 'description', 'city']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['skills']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'company_name', 'description')
        }),
        ('Location', {
            'fields': ('country', 'city')
        }),
        ('Job Details', {
            'fields': ('contract_duration', 'vacancies', 'is_urgent')
        }),
        ('Benefits', {
            'fields': ('fooding', 'lodging', 'overtime_available')
        }),
        ('Salary', {
            'fields': ('salary', 'salary_currency')
        }),
        ('Requirements', {
            'fields': ('skills', 'education', 'experience_years', 'age_min', 'age_max', 'gender')
        }),
        ('Status', {
            'fields': ('status', 'deadline', 'posted_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """
    Job Application admin configuration
    """
    list_display = ['full_name', 'job', 'contact_number', 'passport_number', 'status', 'created_at_datetime']
    list_filter = ['status', 'job', 'created_at']
    search_fields = ['full_name', 'contact_number', 'passport_number', 'job__title']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['skills']
    list_editable = ['status']

    fieldsets = (
        ('Applicant Information', {
            'fields': ('full_name', 'contact_number', 'user')
        }),
        ('Passport Details', {
            'fields': ('passport_number', 'passport_photo')
        }),
        ('Application Details', {
            'fields': ('job', 'skills', 'cv')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
