from .auth_views import (
    # Admin auth
    admin_register,
    admin_login,
    admin_forgot_password,
    admin_reset_otp,
    admin_reset_password,
    admin_logout,
    admin_dashboard,
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
)

from .admin_profile_views import (
    admin_profile,
    admin_edit_profile,
    admin_change_password,
)

from .company_views import (
    company_profile,
    company_edit,
)

from .job_views import (
    job_list,
    job_add,
    job_edit,
    job_delete,
    job_detail,
)

from .skill_views import (
    skill_list,
    skill_add,
    skill_edit,
    skill_delete,
)

from .user_job_views import (
    user_jobs_list,
    user_job_detail,
    apply_for_job,
    application_success,
    user_my_applications,
    user_application_detail,
)

from .application_views import (
    application_list,
    application_detail,
    application_update_status,
    application_delete,
)

__all__ = [
    # Admin auth
    'admin_register',
    'admin_login',
    'admin_forgot_password',
    'admin_reset_otp',
    'admin_reset_password',
    'admin_logout',
    'admin_dashboard',
    # Admin profile
    'admin_profile',
    'admin_edit_profile',
    'admin_change_password',
    # Company
    'company_profile',
    'company_edit',
    # Jobs
    'job_list',
    'job_add',
    'job_edit',
    'job_delete',
    'job_detail',
    # Skills
    'skill_list',
    'skill_add',
    'skill_edit',
    'skill_delete',
    # User auth
    'user_register',
    'user_login',
    'verify_email',
    'user_logout',
    # Google OAuth
    'google_login',
    'google_callback',
    # User profile
    'user_profile',
    'edit_profile',
    'change_password',
    # Profile completion
    'complete_profile',
    # Documents
    'edit_documents',
    # Home
    'home',
    # User jobs
    'user_jobs_list',
    'user_job_detail',
    'apply_for_job',
    'application_success',
    'user_my_applications',
    'user_application_detail',
    # Admin applications
    'application_list',
    'application_detail',
    'application_update_status',
    'application_delete',
]
