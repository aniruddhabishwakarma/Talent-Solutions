from django.urls import path
from django.shortcuts import redirect
from main.views.auth_views import contact_popup
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
    # Team
    team_list,
    team_add,
    team_edit,
    team_delete,
    team_toggle_status,
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
    # Contact
    submit_contact,
    # Contact Admin
    contact_messages_list,
    contact_message_detail,
    contact_message_delete,
    contact_message_toggle_read,
    # Hero Photos
    hero_photo_list,
    hero_photo_add,
    hero_photo_delete,
    hero_photo_toggle,
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

    # Contact
    path("contact-popup/", contact_popup, name="contact_popup"),
    path("contact/submit/", submit_contact, name="submit_contact"),
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

    # Team
    path('my-admin/team/', team_list, name='team_list'),
    path('my-admin/team/add/', team_add, name='team_add'),
    path('my-admin/team/<int:pk>/edit/', team_edit, name='team_edit'),
    path('my-admin/team/<int:pk>/delete/', team_delete, name='team_delete'),
    path('my-admin/team/<int:pk>/toggle/', team_toggle_status, name='team_toggle_status'),

    # Applications
    path('my-admin/applications/', application_list, name='application_list'),
    path('my-admin/applications/<int:pk>/', application_detail, name='application_detail'),
    path('my-admin/applications/<int:pk>/update-status/', application_update_status, name='application_update_status'),
    path('my-admin/applications/<int:pk>/delete/', application_delete, name='application_delete'),

    # Contact Messages
    path('my-admin/contact-messages/', contact_messages_list, name='contact_messages_list'),
    path('my-admin/contact-messages/<int:pk>/', contact_message_detail, name='contact_message_detail'),
    path('my-admin/contact-messages/<int:pk>/delete/', contact_message_delete, name='contact_message_delete'),
    path('my-admin/contact-messages/<int:pk>/toggle-read/', contact_message_toggle_read, name='contact_message_toggle_read'),

    # Hero Photos
    path('my-admin/hero-photos/', hero_photo_list, name='hero_photo_list'),
    path('my-admin/hero-photos/add/', hero_photo_add, name='hero_photo_add'),
    path('my-admin/hero-photos/<int:pk>/delete/', hero_photo_delete, name='hero_photo_delete'),
    path('my-admin/hero-photos/<int:pk>/toggle/', hero_photo_toggle, name='hero_photo_toggle'),
]
