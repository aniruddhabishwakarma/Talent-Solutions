from django.urls import path
from django.shortcuts import redirect
from main.views import (
    # Admin auth
    admin_register,
    admin_login,
    admin_forgot_password,
    admin_reset_otp,
    admin_reset_password,
    admin_logout,
    admin_dashboard,
    # Admin profile
    admin_profile,
    admin_edit_profile,
    admin_change_password,
    # Company
    company_profile,
    company_edit,
    # Jobs (Admin)
    job_list,
    job_add,
    job_edit,
    job_delete,
    job_detail,
    # Skills
    skill_list,
    skill_add,
    skill_edit,
    skill_delete,
    # User auth
    user_register,
    user_login,
    verify_email,
    user_logout,
    # Google OAuth
    google_login,
    google_callback,
    # User profile
    user_profile,
    edit_profile,
    change_password,
    # Profile completion
    complete_profile,
    # Documents
    edit_documents,
    # Home
    home,
    # User jobs
    user_jobs_list,
    user_job_detail,
    apply_for_job,
    application_success,
    user_my_applications,
    user_application_detail,
    # Admin applications
    application_list,
    application_detail,
    application_update_status,
    application_delete,
)

urlpatterns = [
    # Home
    path('', home, name='home'),

    # User authentication
    path('register/', user_register, name='user_register'),
    path('login/', user_login, name='user_login'),
    path('verify-email/', verify_email, name='verify_email'),
    path('logout/', user_logout, name='user_logout'),

    # Google OAuth
    path('auth/google/', google_login, name='google_login'),
    path('auth/google/callback/', google_callback, name='google_callback'),

    # User profile
    path('profile/', user_profile, name='user_profile'),
    path('profile/complete/', complete_profile, name='complete_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/edit-documents/', edit_documents, name='edit_documents'),
    path('profile/change-password/', change_password, name='change_password'),

    # User jobs
    path('jobs/', user_jobs_list, name='user_jobs_list'),
    path('jobs/<slug:slug>/', user_job_detail, name='user_job_detail'),
    path('jobs/<slug:slug>/apply/', apply_for_job, name='apply_for_job'),
    path('jobs/<slug:slug>/apply/success/', application_success, name='application_success'),

    # My applications
    path('my-applications/', user_my_applications, name='user_my_applications'),
    path('my-applications/<int:pk>/', user_application_detail, name='user_application_detail'),

    # Admin panel - redirect to dashboard
    path('my-admin/', lambda request: redirect('admin_dashboard'), name='admin_home'),

    # Admin authentication
    path('my-admin/register/', admin_register, name='admin_register'),
    path('my-admin/login/', admin_login, name='admin_login'),
    path('my-admin/forgot-password/', admin_forgot_password, name='admin_forgot_password'),
    path('my-admin/reset-otp/', admin_reset_otp, name='admin_reset_otp'),
    path('my-admin/reset-password/', admin_reset_password, name='admin_reset_password'),
    path('my-admin/logout/', admin_logout, name='admin_logout'),
    path('my-admin/dashboard/', admin_dashboard, name='admin_dashboard'),

    # Admin profile
    path('my-admin/profile/', admin_profile, name='admin_profile'),
    path('my-admin/profile/edit/', admin_edit_profile, name='admin_edit_profile'),
    path('my-admin/profile/change-password/', admin_change_password, name='admin_change_password'),

    # Company
    path('my-admin/company/', company_profile, name='company_profile'),
    path('my-admin/company/edit/', company_edit, name='company_edit'),

    # Jobs
    path('my-admin/jobs/', job_list, name='job_list'),
    path('my-admin/jobs/add/', job_add, name='job_add'),
    path('my-admin/jobs/<slug:slug>/', job_detail, name='job_detail'),
    path('my-admin/jobs/<slug:slug>/edit/', job_edit, name='job_edit'),
    path('my-admin/jobs/<slug:slug>/delete/', job_delete, name='job_delete'),

    # Skills
    path('my-admin/skills/', skill_list, name='skill_list'),
    path('my-admin/skills/add/', skill_add, name='skill_add'),
    path('my-admin/skills/<slug:slug>/edit/', skill_edit, name='skill_edit'),
    path('my-admin/skills/<slug:slug>/delete/', skill_delete, name='skill_delete'),

    # Applications
    path('my-admin/applications/', application_list, name='application_list'),
    path('my-admin/applications/<int:pk>/', application_detail, name='application_detail'),
    path('my-admin/applications/<int:pk>/update-status/', application_update_status, name='application_update_status'),
    path('my-admin/applications/<int:pk>/delete/', application_delete, name='application_delete'),
]
