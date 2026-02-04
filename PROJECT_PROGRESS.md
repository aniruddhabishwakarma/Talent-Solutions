# Talent Solutions - Project Progress Document

## Important Note for Next Session
**File Operations:** When deleting, copying, or moving any file or folder, Claude will inform the user about which files need to be moved/deleted/copied, and the user will perform these operations manually.

---

## Project Overview
Converted an existing Django e-commerce project into a **Job Portal** called **Talent Solutions**.

---

## What We Did

### 1. Project Rename
- Renamed project folder from `retail_ecommerce` to `talent_solutions`
- Updated all references in:
  - `manage.py`
  - `settings.py`
  - `wsgi.py`
  - `asgi.py`

### 2. JWT Authentication Implementation
- Installed packages: `djangorestframework`, `djangorestframework-simplejwt`
- Created JWT middleware (`main/middleware.py`) for cookie-based authentication
- JWT tokens stored in HTTP-only cookies for security
- Token lifetime: Access (1 day), Refresh (7 days)

### 3. Flexible Login System
- Admin can login using **username**, **email**, OR **phone number** + password
- Shows "Invalid credentials" error for wrong login attempts
- Two users can login simultaneously (stateless JWT)

### 4. User Model Changes
- Updated roles: `admin`, `user`
- Made `phone_number` field unique
- Fields: username, email, password, first_name, last_name, phone_number, address, profile_picture, role

### 5. Custom Decorators (`main/decorators.py`)
- `@admin_required` - Only admin users can access
- `@user_required` - Only regular users can access
- `@guest_only` - Only non-authenticated users can access

### 6. Admin Profile Management
- **My Profile** - View profile information
- **Edit Profile** - Change photo, name, email, phone, address
- **Change Password** - Separate page for password change

Templates moved to: `main/templates/my-admin/profile/`
- `profile.html`
- `edit_profile.html`
- `change_password.html`

### 7. Company Profile Feature
Created a singleton Company model for storing company information.

**Model:** `main/models/company_model.py`

**Fields:**
| Section | Fields |
|---------|--------|
| Basic Info | company_name, logo, tagline, website, industry, company_type, company_size, founded_year |
| Contact | email, phone, alternate_phone |
| Address | address, city, state, country, postal_code |
| About | about (description) |
| Social Media | facebook, twitter, instagram |

**Views:** `main/views/company_views.py`
- `company_profile` - View company info
- `company_edit` - Edit company info

**Templates:** `main/templates/my-admin/company/`
- `profile.html`
- `edit.html`

**URLs:**
- `/my-admin/company/` - View company profile
- `/my-admin/company/edit/` - Edit company profile

### 8. Sidebar Updates
- Added "Company" section with Company Profile link
- Account section with My Profile link
- System section with View Site and Logout

### 9. Branding Updates
- Changed "Retail Admin" to "Talent Solutions" in navbar
- Updated base.html title to "Talent Solutions Admin"

### 10. Admin Panel Root URL
- `/my-admin/` now redirects to dashboard
- If not logged in, redirects to login page automatically

### 11. Skill Model (`main/models/skill_model.py`)
Skills that can be assigned to jobs.

| Field | Type | Description |
|-------|------|-------------|
| name | CharField | Skill name (unique) |
| slug | SlugField | URL-friendly name (auto-generated) |
| created_at | BigInteger | Epoch milliseconds (auto) |

**Views:** `main/views/skill_views.py`
- `skill_list` - List all skills
- `skill_add` - Add new skill
- `skill_edit` - Edit skill
- `skill_delete` - Delete skill

**Templates:** `main/templates/my-admin/skills/`
- `list.html`, `add.html`, `edit.html`, `delete.html`

### 12. Job Model (`main/models/job_model.py`)
Job postings for overseas employment (Gulf recruitment agency).

| Category | Field | Type | Description |
|----------|-------|------|-------------|
| Basic | title | CharField | Job title |
| | company_name | CharField | Company name for the job |
| | slug | SlugField | URL-friendly (auto) |
| | description | TextField | Full description with benefits |
| Location | country | CharField | All countries dropdown (flat list) |
| | city | CharField | City (optional) |
| Contract | contract_duration | Integer | Duration in months (optional) |
| Benefits | fooding | Boolean | Is food provided? (Yes/No radio) |
| | lodging | Boolean | Is lodging/accommodation provided? (Yes/No radio) |
| | overtime_available | Boolean | Is overtime available? (Yes/No radio) |
| Salary | salary | Decimal | Monthly salary |
| | salary_currency | CharField | USD, AED, SAR, QAR, KWD, BHD, OMR, etc. |
| Requirements | skills | M2M | Link to Skill model |
| | education | CharField | Education required |
| | experience_years | Integer | Min years experience |
| | age_min | Integer | Minimum age |
| | age_max | Integer | Maximum age |
| | gender | CharField | Male, Female, Any |
| Vacancies | vacancies | Integer | Number of openings |
| Status | status | CharField | Draft, Active, Closed (auto based on deadline) |
| | deadline | DateField | Application deadline |
| | is_urgent | Boolean | Urgent hiring flag |
| Timestamps | created_at | BigInteger | Epoch ms (auto) |
| | updated_at | BigInteger | Epoch ms (auto on save) |
| Relations | posted_by | FK | Admin who posted |

**Auto Status Logic:**
- If deadline passed → status = **Closed** (automatic)
- If deadline future & status active → stays **Active**
- Draft stays **Draft** regardless of deadline

**Views:** `main/views/job_views.py`
- `job_list` - List all jobs (with multiple filters)
- `job_add` - Add new job
- `job_edit` - Edit job
- `job_delete` - Delete job
- `job_detail` - View job details

**Templates:** `main/templates/my-admin/jobs/`
- `list.html`, `add.html`, `edit.html`, `delete.html`, `detail.html`

### 13. Job List Page Improvements
- **Multiple Filters:** Status, Country, Urgent Only
- **Filter Bar:** All filters in one row with "Add New Job" button on the far right
- **Clear Filters:** Button appears when any filter is active
- **Table Columns:** Job Title, Company, Country, Salary, Vacancies, Deadline, Status, Actions

### 14. Tag-Style Skill Input
Skills are added directly in job forms (add/edit) using tag-style input:
- Type skill name and press Enter or click Add
- Skills appear as removable tags
- Skills are created automatically if they don't exist (using `get_or_create`)
- Comma-separated skills stored in hidden field

### 15. Job Detail Page Redesign
Professional layout with better organization:

**Header Section:**
- Breadcrumb navigation at top ("Back to Jobs / Job Title")
- Job title with URGENT badge and status badge
- Company name and location with icon
- Edit and Delete buttons on the right side

**Quick Stats Section:**
4 stat cards showing key information at a glance:
- Monthly Salary (green icon)
- Vacancies (blue icon)
- Deadline (yellow icon)
- Overtime Available (purple icon)

**Content Grid:**
- Left column (2/3): Job Description, Required Skills
- Right column (1/3): Job Details, Benefits (Fooding, Lodging, Overtime), Requirements, Meta Information

**Card Styling:**
- Each card has an icon in the title
- Clean info rows with label and value
- Responsive design for mobile

### 16. Sidebar Collapsed State Fix
Fixed icons visibility when sidebar is collapsed:

**Icon Display:**
- Icons are now visible and centered (48x48px buttons)
- Menu sections are centered in collapsed state
- Text, titles, and badges are properly hidden

**Tooltips:**
- Hover over any icon shows tooltip with menu name
- Tooltip appears on the right side of the icon
- Smooth fade-in animation

### 17. Job Model Restructure (Session 3)
Replaced Job Type field with Benefits fields:

**Removed:**
- `job_type` field (Full-time, Part-time, Contract, Temporary)

**Added:**
- `fooding` (Boolean) - Is food provided? Displayed as Yes/No radio buttons
- `lodging` (Boolean) - Is lodging/accommodation provided? Displayed as Yes/No radio buttons
- `overtime_available` (Boolean) - Is overtime available? Displayed as Yes/No radio buttons

**UI Changes:**
- Job add/edit forms now show radio buttons (Yes/No) for Fooding, Lodging, and Overtime
- Job detail page shows "Benefits" section with Fooding, Lodging, Overtime info
- Quick stats card now shows "Overtime" instead of "Job Type"
- Job list filter bar no longer has Job Type filter
- Admin panel updated to include new fields in list_display and filters

**Migration:** `main/migrations/0005_add_benefits_remove_job_type.py`

### 18. Admin Profile Views Refactoring (Session 3)
Moved admin profile view functions to a separate file for better organization.

**New File:** `main/views/admin_profile_views.py`

**Views Moved:**
- `admin_profile` - View admin profile
- `admin_edit_profile` - Edit admin profile
- `admin_change_password` - Change admin password

**Updated Files:**
- `main/views/auth_views.py` - Removed admin profile views
- `main/views/__init__.py` - Updated imports to include new file

### 19. User Panel - Base Template & Login Page (Session 3)
Created new user panel with proper template inheritance structure.

**Design Specs:**
- Background: `linear-gradient(115.6deg, #004A98 6.49%, #001832 104.59%)`
- White login card with rounded corners (20px)
- Fully responsive for all screen sizes

**Base Template (`main/templates/user/base.html`):**
- Includes navbar component
- Toast notification system
- Footer with company info, quick links, services, contact
- Blocks: `title`, `extra_css`, `body_class`, `main_class`, `content`, `footer`, `extra_js`
- Default gradient background (can be overridden)

**Navbar Component (`main/templates/user/components/navbar.html`):**
- Logo (circular gradient badge with blue/red colors)
- Navigation links: Home, About, Services, Jobs, Contact
- "Get in Touch" button (cyan/blue gradient, rounded)
- Authenticated users see avatar, name, and dropdown (Profile / Applications / Logout)
- Mobile responsive with hamburger menu
- Underline hover effect on nav links
- Phone number removed (was cluttering the navbar)

**Login Page (`main/templates/user/login.html`):**
- Extends `user/base.html`
- No footer (overridden with empty block)
- Email/Username field
- Password field
- Login button (blue gradient)
- "Or Signin with" divider
- "Continue with google" button
- "Dont have an account? Signup" link (gradient text)

### 20. User Registration & Onboarding Flow (Session 4)

**Registration fixes (`main/views/auth_views.py` + `register.html`):**
- Fixed field name mismatch: view was reading `password_confirm` but template sent `password2` — registration was completely broken
- Password mismatch error now displays inline under the confirm password field (red text) instead of as a toast
- Client-side JS validates password length (min 6) and match in real time while typing

**Auto-login after registration:**
- On successful registration, JWT tokens are generated and set immediately
- User is redirected straight to `complete_profile` onboarding — no need to log in again

**Profile completion onboarding (`complete_profile` view + template):**
- Step 1 of 3 page shown after first registration/login
- Collects: phone number, passport number, passport photo, CV upload, user skills
- Fixed critical bug: a nested `<form>` inside the main form had a hidden `action=skip` input — browsers included it in every POST, so "Save & Continue" was silently hitting the skip branch and never saving any data. Removed nested forms entirely; both Save and Skip are now buttons inside the single form with `name="action"` values
- `is_profile_complete` flag is set on the User model after save or skip
- Returning users who haven't completed onboarding are redirected here on login

### 21. UserSkill Model — Separate from Job Skills (Session 4)

Previously users shared the same `Skill` model used for job postings (admin-managed). Now split into two distinct entities:

**`Skill` model** — unchanged, used only for job postings (`Job.skills` M2M). Managed by admins via the skills CRUD pages.

**`UserSkill` model** (`main/models/user_skill_model.py`) — freeform skills entered by users themselves:
- `user` — ForeignKey to User (`related_name='user_skills'`)
- `name` — CharField (max 100)
- `unique_together = ('user', 'name')`
- `db_table = 'user_skills'`

**Migration:** `0009_replace_user_skills_with_userskill.py`
- Removes old M2M `user.skills` field
- Creates `UserSkill` table

**UI:** Tag-style input used in `complete_profile.html` and `edit_profile.html`:
- Type a skill name, press Enter or click Add
- Tags appear as removable chips (× to remove)
- Hidden inputs `name="user_skills"` are dynamically created by JS
- Duplicate check is case-insensitive

### 22. User Profile & Documents (Session 4)

**UserDocument model** (already existed) stores passport number, passport photo, and CV for each user — one-to-one with User. Created automatically on user registration.

**Profile page (`profile.html`):**
- Displays all user info: name, email, phone, address, profile picture
- Shows skills from `user.user_skills` (the new UserSkill model)
- Shows passport number, passport photo, and CV from the linked UserDocument
- Edit Profile and Edit Documents buttons

**Edit Documents page (`edit_documents.html`):**
- Upload/update passport photo and CV
- Edit passport number
- File type and size validation (passport: JPG/PNG ≤5MB, CV: PDF/Word ≤10MB)

### 23. Navbar Theming — Dark/Light Mode (Session 4)

The home page has alternating dark and light sections. The navbar dynamically switches between dark (transparent) and light (white) styles based on scroll position using `updateNavbar()` in `home.html`.

All inner pages (profile, edit, jobs, apply, etc.) force the navbar into light mode using a consistent inline script block:
- Sets navbar background to white with shadow
- Changes nav links, logo text, mobile button, user name, and chevron from white to gray
- Pattern applied uniformly across: `profile.html`, `edit_profile.html`, `edit_documents.html`, `complete_profile.html`, `jobs/detail.html`, `jobs/apply.html`

### 24. Home Page & Job Card UI Fixes (Session 4)

- Removed company-initial avatar (colored circle with first letter) from job cards on the home page — cards now show just the job info without the redundant avatar
- Hero section: changed "View Profile" button (for logged-in users) to "Get Started" linking to the `#jobs` section on the same page

### 25. Job Apply Page Improvements (Session 4)

- Removed company-initial avatar from the job summary card at the top of the apply page
- Passport photo thumbnail (if already uploaded) is now clickable — opens a full-size image modal with a dark backdrop overlay
- Modal closes on backdrop click or × button
- Replaced stale navbar script references throughout apply.html and detail.html

### 26. Admin Dashboard Rewrite (Session 5)

The dashboard was full of stale e-commerce leftovers (Orders, Revenue, Products, Stock Alerts) — none of which existed in the current app or were passed by the view. Completely rewritten.

**View (`main/views/auth_views.py` — `admin_dashboard`):**
- Now passes: `total_users`, `total_jobs`, `total_applications`, `pending_applications`, `recent_applications` (last 5), `app_status` (dict with count per status)

**Template (`main/templates/my-admin/dashboard.html`):**
- 4 stat cards: Total Users, Active Jobs, Total Applications, Pending Review
- Recent Applications table: last 5 applications with status badge and "View" link
- Status Overview: color-coded progress bars for all 5 statuses (pending, reviewed, shortlisted, accepted, rejected)

### 27. Application List Filter Fixes (Session 5)

Fixed two bugs in `main/templates/my-admin/applications/list.html`:
- **Status filter buttons** were dropping `search` and `job` query params when clicked — now all existing params are preserved in the href
- **Pagination links** were already preserving `status` and `search` but were missing `job` — added it

### 28. Rejection Reason Feature (Session 5)

When an application is rejected, the admin must now provide a reason. The reason is stored in the DB and will be emailed to the applicant later (mailing not yet implemented).

**Model (`main/models/application_model.py`):**
- Added `rejection_reason = models.TextField(blank=True, null=True)` field

**Migration:** `main/migrations/0010_add_rejection_reason_to_jobapplication.py`

**Admin view (`main/views/application_views.py` — `application_update_status`):**
- When `new_status == 'rejected'` and `rejection_reason` is empty → returns error "Please provide a reason for rejection"
- On valid rejection, saves `rejection_reason` to the application

**Admin template (`main/templates/my-admin/applications/detail.html`):**
- Status update form: selecting "Rejected" from the dropdown reveals a textarea for the rejection reason (JS toggle via `toggleRejectionReason()`)
- If reason is empty on submit, a client-side alert fires before the form posts
- After rejection is saved, a red card appears below the status form displaying the saved reason with a note: "This reason will be included in the rejection email"
- JS placed in `{% block extra_script %}` as raw JS (no `<script>` wrapper) — admin base.html's `extra_script` block is already inside a `<script>` tag

### 29. Reapply After Rejection — User Side (Session 5)

Users whose application was rejected can now reapply for the same job.

**View (`main/views/user_job_views.py`):**
- `user_job_detail`: Changed from passing a `has_applied` boolean to fetching the full `user_application` object (latest by `created_at`) and passing it to context
- `apply_for_job`: The "already applied" guard now only blocks if `existing_application.status != 'rejected'` — rejected users pass through to the apply form

**Job detail page (`main/templates/user/jobs/detail.html`):**
- If `user_application` exists and status is `rejected`: shows a red card with "Your application was rejected", the rejection reason text, and a "Reapply" button (same cyan gradient style as Apply Now)
- If applied but not rejected: shows green "Already Applied" badge (unchanged)

### 30. Red Marker on Passport Photo Field When Reapplying (Session 5)

When a user lands on the apply page after a rejection, the passport photo upload field is highlighted in red and the rejection reason is shown above it — drawing attention to the field that likely caused the rejection.

**View (`main/views/user_job_views.py` — `apply_for_job` GET handler):**
- When `existing_application` exists and is rejected, passes `rejection_reason` into the template context

**Template (`main/templates/user/jobs/apply.html`):**
- Added `.file-upload.rejected` CSS class: red dashed border (`#ef4444`) with light red background (`#fef2f2`)
- A red warning card (with warning icon) appears above the passport photo upload when `rejection_reason` exists — shows "Previous application was rejected" and the reason text
- The `.file-upload` div gets the `rejected` class when reapplying, overriding the default green `has-file` class

### 31. Profile Picture Upload in Onboarding (Session 6)

Added a circular avatar upload to the `complete_profile` onboarding page so users can set a profile picture during first-time setup.

**Model** — no change needed. `User.profile_picture` (ImageField) and `User.profile_picture_url` (for Google OAuth) already existed. Added `upload_profile_picture` callable to `auth_model.py` for the new naming convention (see §33).

**Template (`complete_profile.html`):**
- Circular avatar area placed before "Contact Information"
- If user already has a picture (e.g. from Google OAuth) it is shown; otherwise a placeholder with a person icon is displayed
- Camera-badge overlay on the circle
- JS uses `FileReader` to show a live preview without uploading

**View (`auth_views.py` — `complete_profile` POST):**
- Reads `profile_picture` from `request.FILES`
- Validates: JPG/PNG only, max 5 MB
- Saves to `user.profile_picture`

### 32. File Upload Previews on Apply Page (Session 6)

When uploading a passport photo or CV on the job-apply form, users now see a visual confirmation that the file was picked — previously the UI gave no feedback at all.

**Passport photo:** `FileReader` reads the selected file and renders a thumbnail (`w-28 h-20`, rounded) in a hidden preview div. The placeholder text disappears.

**CV:** A green document-icon block (`w-10 h-12`) appears with the truncated filename beside it.

Both previews are purely client-side; no extra round-trip to the server.

### 33. Custom File Naming Convention (Session 6)

All uploaded files were previously saved with whatever filename the user's OS gave them (e.g. `IMG_4823.jpg`). Replaced with deterministic, collision-safe paths using callable `upload_to` functions.

**Pattern:** `{category}/{user_id}_{type}_{uuid8}.{ext}`

| Model | Field | Example path |
|-------|-------|--------------|
| User | profile_picture | `profile_pictures/42_profile_a1b2c3d4.jpg` |
| JobApplication | passport_photo | `applications/passport_photos/42_passport_e5f6a7b8.png` |
| JobApplication | cv | `applications/cvs/42_cv_c9d0e1f2.pdf` |
| UserDocument | passport_photo | `documents/passport_photos/42_passport_11223344.jpg` |
| UserDocument | cv | `documents/cvs/42_cv_55667788.pdf` |

`uuid4().hex[:8]` keeps names short while keeping collisions astronomically unlikely. Existing files on disk keep their old names; only new uploads use the new convention.

**Migration:** `0011_update_upload_to_conventions.py` — 5 `AlterField` ops, no DB schema change (cosmetic migration only).

### 34. My Applications — List & Detail Pages (Session 6)

Logged-in users can now see and track every application they have submitted.

**Views (`user_job_views.py`):**
- `user_my_applications` — filters by `user`, supports `?status=` query param, computes per-status counts, paginates at 10
- `user_application_detail` — fetches by `pk` with a `user=request.user` guard (returns 404 if not theirs)

**Templates:**
- `applications/list.html` — status-filter tabs (All / Pending / Reviewed / Shortlisted / Accepted / Rejected) with live counts. Cards show job title, company, country, applied date, color-coded status badge, salary, and a "View Details" link. Rejected cards show a truncated rejection-reason snippet. Empty state + pagination (preserves active status filter in prev/next hrefs).
- `applications/detail.html` — breadcrumb, two-column layout. Left: job-info card with gradient header, status card with a 4-step progress bar (dots + bars colored by current status), rejection-reason card + Reapply button when rejected. Right: applicant info, skills as cyan pills, passport-photo with click-to-enlarge modal, CV download link, "View Job Listing" button.

**Navbar fix (`navbar.html`):**
- Desktop dropdown "My Applications" href was pointing at `user_jobs_list` — changed to `user_my_applications`
- Mobile menu was missing the link entirely — added it

**URLs:**
- `/my-applications/` → `user_my_applications`
- `/my-applications/<int:pk>/` → `user_application_detail`

### 35. User Job Detail Page Redesign (Session 6)

Full rewrite of `jobs/detail.html` to visually match the jobs list page theme — removed all colored icon boxes, aligned card/pill/label conventions with the list.

**Hero:** badges row (Urgent + Active), title, company, location, quick-meta line with `·` separators (openings · contract · deadline), salary in green-600, CTA block (Apply Now / Reapply / Already Applied / Sign in to Apply — all original logic preserved).

**Main grid (2/3 + 1/3):**
- Left: Job Description (`.prose-desc` CSS for line-height), Required Skills as cyan pills, bottom "Ready to apply?" CTA card
- Right: Benefits as label/value rows with gray-100 checkmark pills (same as list), Requirements as clean divide-y rows, Share buttons (Facebook, Twitter, WhatsApp, Copy link)

**Related jobs:** cards use the exact same structure as the list page (title, company, location, salary pill, benefit pills, footer meta).

### 36. Home Page Jobs Carousel (Session 6)

Converted the jobs section on the home page from a vertical stack of 3 cards to a horizontal scrolling carousel.

**View change (`auth_views.py`):** bumped `featured_jobs` from `[:3]` to `[:6]` so the carousel has enough cards to scroll.

**Carousel structure:**
- Cards are fixed-width (`w-72 sm:w-80`), laid out in a `flex gap-4` row inside an `overflow-hidden` container
- Each card: gradient company-logo square, cyan title, company · country meta, green salary pill, right-arrow chevron
- Prev / Next buttons: `bg-gradient-to-r from-cyan-500 to-blue-600` rounded circles, positioned absolutely on the left/right edges. Start hidden; JS toggles them based on scroll position

**JS (IIFE, no globals except `carouselSlide`):**
- `getCardWidth()` reads the first card's `offsetWidth` + 16 px gap dynamically
- `visibleCount()` = how many cards fit; `maxIndex()` = total cards minus visible
- Prev hidden at index 0; next hidden at max index
- Resize handler clamps index and re-renders
- Existing `reveal` / `reveal-children` scroll animations preserved

### 37. Jobs List & Detail — Logo Removal + Filter Sidebar Rearranged (Session 6)

**`jobs/list.html`:**
- Removed the gradient company-initial square from every job card. Job info now takes the full card width
- Added two new footer-row items that were missing: **contract duration** ("X month(s)", calendar icon) and **experience required** ("X+ yr exp", clock icon). Both conditional — only shown when the field is set
- Filter sidebar moved from left to right using flexbox `order` (`lg:order-2` on sidebar, `lg:order-1` on job list). Widened from `lg:w-64` to `lg:w-80`. On mobile it still stacks on top naturally

**`jobs/detail.html`:**
- Hero: gradient logo square removed. Title, badges, company, location and quick-meta sit flush left. Added `experience_years` ("X+ yr exp") to the meta line — it was already showing contract duration and deadline but was missing experience
- Related-jobs cards: mini logo squares removed. Each card now goes straight to title → company → location. Footer row got the same contract + experience fields as the list page

### 38. My Applications Page Height Fix (Session 6)

The applications list and detail pages had no minimum height — when there were few or no applications the footer sat mid-screen instead of at the bottom.

**Both `applications/list.html` and `applications/detail.html`:**
- `main_class` block changed from `pt-20` to `min-h-screen pt-20 flex flex-col` — makes `<main>` at least full-viewport height and a flex column
- The content `<section>` got `flex-1` — stretches to fill remaining space after the page-header section, pushing the footer below the fold

### 39. Brevo Email System (Session 6)

Set up end-to-end transactional email via Brevo SMTP relay. Three email types are live; two sender slots are reserved for future use.

**Credentials (`.env`):**
- `BREVO_SMTP_LOGIN` / `BREVO_SMTP_PASSWORD` — relay credentials

**SMTP config (`settings.py`):**
- Host: `smtp-relay.brevo.com`, Port: `2525`, TLS: enabled
- `EMAIL_SENDERS` dict holds five named sender addresses (all currently routed through the single verified address `no-reply@projekthub.com`; swap individual keys to dedicated verified addresses when ready)

| Key | Current address | Purpose |
|-----|-----------------|---------|
| welcome | no-reply@projekthub.com | Application-submitted confirmation → applicant |
| hr | no-reply@projekthub.com | Status-update email → applicant |
| recruitment | no-reply@projekthub.com | New-application alert → admin |
| support | no-reply@projekthub.com | Account / login verification (planned) |
| notifications | notifications@projekthub.com | General notifications (ready) |

**Email module (`main/emails.py`):**
- `_send(sender_key, to, subject, plain, html)` — shared helper, wraps `EmailMessage`, catches all exceptions (logs, never crashes the view)
- `send_application_confirmation(application)` — fires on submit. Skipped silently if applicant has no email. HTML email with job/company/status table
- `send_new_application_alert(application)` — fires on submit. Sends to every User with `role=admin` that has an email set
- `send_application_status_update(application)` — fires when admin changes status. Includes a color-coded status badge and, for rejections, a red reason card. No-op if status is still `pending`

**Wired into views:**
- `user_job_views.py` — after `application.save()` calls `send_application_confirmation` + `send_new_application_alert`
- `application_views.py` — after status save calls `send_application_status_update`

---

## Files Created/Modified

### New Files
- `main/models/company_model.py`
- `main/models/skill_model.py`
- `main/models/job_model.py`
- `main/models/application_model.py`
- `main/models/user_skill_model.py`
- `main/views/company_views.py`
- `main/views/skill_views.py`
- `main/views/job_views.py`
- `main/views/admin_profile_views.py`
- `main/views/user_job_views.py`
- `main/views/application_views.py`
- `main/middleware.py`
- `main/decorators.py`
- `main/templates/my-admin/company/profile.html`
- `main/templates/my-admin/company/edit.html`
- `main/templates/my-admin/profile/profile.html`
- `main/templates/my-admin/profile/edit_profile.html`
- `main/templates/my-admin/profile/change_password.html`
- `main/templates/my-admin/jobs/list.html`
- `main/templates/my-admin/jobs/add.html`
- `main/templates/my-admin/jobs/edit.html`
- `main/templates/my-admin/jobs/delete.html`
- `main/templates/my-admin/jobs/detail.html`
- `main/templates/my-admin/skills/list.html`
- `main/templates/my-admin/skills/add.html`
- `main/templates/my-admin/skills/edit.html`
- `main/templates/my-admin/skills/delete.html`
- `main/templates/my-admin/applications/list.html`
- `main/templates/my-admin/applications/detail.html`
- `main/templates/user/home.html`
- `main/templates/user/profile.html`
- `main/templates/user/edit_profile.html`
- `main/templates/user/edit_documents.html`
- `main/templates/user/complete_profile.html`
- `main/templates/user/jobs/list.html`
- `main/templates/user/jobs/detail.html`
- `main/templates/user/jobs/apply.html`
- `main/migrations/0003_skill_job.py`
- `main/migrations/0006_add_job_application.py`
- `main/migrations/0007_add_google_oauth_fields.py`
- `main/migrations/0008_add_user_skills_profile_complete_and_user_document.py`
- `main/migrations/0009_replace_user_skills_with_userskill.py`
- `main/migrations/0010_add_rejection_reason_to_jobapplication.py`
- `main/migrations/0011_update_upload_to_conventions.py`
- `main/emails.py`
- `main/templates/user/applications/list.html`
- `main/templates/user/applications/detail.html`
- `requirements.txt`

### Modified Files
- `manage.py`
- `talent_solutions/settings.py`
- `talent_solutions/wsgi.py`
- `talent_solutions/asgi.py`
- `main/models/__init__.py`
- `main/models/auth_model.py` (removed old M2M skills field, added Google OAuth fields, profile_complete flag)
- `main/views/__init__.py`
- `main/views/auth_views.py` (registration fix, auto-login, onboarding, UserSkill handling)
- `main/urls.py`
- `main/admin.py`
- `main/templates/my-admin/base.html` (sidebar collapsed state, tooltips)
- `main/templates/my-admin/components/navbar.html`
- `main/templates/my-admin/components/sidebar.html` (data-title attributes for tooltips)
- `main/templates/my-admin/login.html`
- `main/templates/my-admin/jobs/list.html` (filters, Add Job button placement)
- `main/templates/my-admin/jobs/detail.html` (complete redesign with quick stats)
- `main/templates/my-admin/jobs/add.html` (tag-style skill input, company_name field)
- `main/templates/my-admin/jobs/edit.html` (tag-style skill input)
- `main/views/job_views.py` (multiple filters, skill auto-create)
- `main/templates/user/components/navbar.html` (removed phone, added user dropdown)
- `main/templates/user/register.html` (inline password error, form data persistence)
- `main/templates/my-admin/dashboard.html` (full rewrite — stat cards, recent apps, status overview)
- `main/templates/my-admin/applications/list.html` (filter param preservation fix)
- `main/templates/my-admin/applications/detail.html` (rejection reason textarea + saved reason card)
- `main/templates/user/jobs/detail.html` (reapply button + rejection reason card for rejected users)
- `main/templates/user/jobs/apply.html` (red marker + rejection reason warning on passport photo field)
- `main/views/application_views.py` (rejection reason validation + save on status update)
- `main/views/user_job_views.py` (reapply guard, rejection_reason in context)
- `main/models/application_model.py` (added rejection_reason field, upload_to callables)
- `main/models/user_document_model.py` (upload_to callables)
- `.env` (added Brevo SMTP credentials)
- `main/templates/user/complete_profile.html` (profile picture upload UI)
- `main/templates/user/jobs/apply.html` (file upload previews)
- `main/templates/user/home.html` (jobs carousel)
- `main/templates/user/jobs/list.html` (logo removed, filter sidebar moved right + widened, contract/experience added)
- `main/templates/user/jobs/detail.html` (full redesign, logo removed, experience added)
- `main/templates/user/applications/list.html` (min-h-screen fix)
- `main/templates/user/applications/detail.html` (min-h-screen fix)

### Files to Delete (Old Templates)
- `main/templates/my-admin/profile.html`
- `main/templates/my-admin/edit_profile.html`
- `main/templates/my-admin/change_password.html`

---

## URLs Summary

### Admin URLs
| URL | Name | Description |
|-----|------|-------------|
| `/my-admin/` | admin_home | Redirects to dashboard |
| `/my-admin/login/` | admin_login | Admin login page |
| `/my-admin/register/` | admin_register | Admin registration |
| `/my-admin/logout/` | admin_logout | Admin logout |
| `/my-admin/dashboard/` | admin_dashboard | Admin dashboard |
| `/my-admin/profile/` | admin_profile | View admin profile |
| `/my-admin/profile/edit/` | admin_edit_profile | Edit admin profile |
| `/my-admin/profile/change-password/` | admin_change_password | Change password |
| `/my-admin/company/` | company_profile | View company profile |
| `/my-admin/company/edit/` | company_edit | Edit company profile |
| `/my-admin/jobs/` | job_list | List all jobs |
| `/my-admin/jobs/add/` | job_add | Add new job |
| `/my-admin/jobs/<slug>/` | job_detail | View job details |
| `/my-admin/jobs/<slug>/edit/` | job_edit | Edit job |
| `/my-admin/jobs/<slug>/delete/` | job_delete | Delete job |
| `/my-admin/skills/` | skill_list | List all skills |
| `/my-admin/skills/add/` | skill_add | Add new skill |
| `/my-admin/skills/<slug>/edit/` | skill_edit | Edit skill |
| `/my-admin/skills/<slug>/delete/` | skill_delete | Delete skill |

### User URLs
| URL | Name | Description |
|-----|------|-------------|
| `/` | home | Home page |
| `/login/` | user_login | User login |
| `/register/` | user_register | User registration (auto-login → onboarding) |
| `/logout/` | user_logout | User logout |
| `/auth/google/` | google_login | Google OAuth login |
| `/auth/google/callback/` | google_callback | Google OAuth callback |
| `/profile/` | user_profile | User profile |
| `/profile/complete/` | complete_profile | Onboarding (shown once after first login) |
| `/profile/edit/` | edit_profile | Edit user profile |
| `/profile/edit-documents/` | edit_documents | Edit passport & CV documents |
| `/profile/change-password/` | change_password | Change password |
| `/jobs/` | user_jobs_list | Browse all active jobs |
| `/jobs/<slug>/` | user_job_detail | View job details |
| `/jobs/<slug>/apply/` | apply_for_job | Apply for a job |
| `/jobs/<slug>/apply/success/` | application_success | Application submitted confirmation |
| `/my-applications/` | user_my_applications | List user's own applications (filterable by status) |
| `/my-applications/<id>/` | user_application_detail | View single application detail |

### Admin Application URLs
| URL | Name | Description |
|-----|------|-------------|
| `/my-admin/applications/` | application_list | List all applications |
| `/my-admin/applications/<id>/` | application_detail | View application details |
| `/my-admin/applications/<id>/update-status/` | application_update_status | Change application status |
| `/my-admin/applications/<id>/delete/` | application_delete | Delete application |

---

## Database
- Using **SQLite** (suitable for small-scale project)
- Tables: `users`, `company`, `skills`, `jobs`, `jobs_skills` (M2M), `user_skills`, `user_documents`, `job_applications`

---

## Key Bugs Fixed
1. **Registration broken** — View read `password_confirm` but template sent `password2`. Every registration attempt showed "Passwords do not match."
2. **Onboarding data never saved** — `complete_profile.html` had a nested `<form>` with a hidden `action=skip` input inside the main form. Browsers included it in every POST, so "Save & Continue" always hit the skip branch silently. Passport, phone, skills, and CV were never persisted despite `is_profile_complete` being set to True.
3. **Stale navbar references** — After removing the phone number element from navbar, multiple templates still referenced `.nav-phone` in their dark/light mode scripts, causing JS errors.
4. **Wrong block name in admin detail template** — Used `{% block extra_js %}` but admin `base.html` defines `{% block extra_script %}`. The rejection-reason JS was completely dropped from the output.
5. **Nested `<script>` tags in admin template** — After fixing the block name, the JS was still wrapped in `<script>...</script>`. But `extra_script` in admin `base.html` is already inside a `<script>` tag (lines 797–799), creating `<script><script>...</script></script>`. Browsers treat the inner tag as text, breaking all JS. Fixed by removing the wrapper and leaving raw JS in the block.
6. **Application list filter params lost** — Status filter buttons on the applications list page dropped `search` and `job` query params on click, resetting active filters.

---

## Next Steps (To Do)
1. ~~Build the Job Posting feature~~ DONE
2. ~~Job list with filters~~ DONE
3. ~~Job detail page redesign~~ DONE
4. ~~Sidebar collapsed state fix~~ DONE
5. ~~User side job viewing and application~~ DONE
6. ~~Job application system~~ DONE
7. ~~User registration & onboarding flow~~ DONE
8. ~~UserSkill model (separate from job skills)~~ DONE
9. ~~Google OAuth login~~ DONE
10. ~~Dashboard with statistics~~ DONE
11. ~~Rejection reason on application rejection~~ DONE
12. ~~Reapply flow for rejected applicants~~ DONE
13. ~~Send rejection reason via email to applicant~~ DONE (part of Brevo email system — §39)
14. ~~My Applications list & detail pages~~ DONE
15. ~~Home page jobs carousel~~ DONE
16. ~~Brevo transactional email system~~ DONE
17. Email verification on normal registration (planned — `support@` sender slot reserved)
18. Email verification on Google OAuth (planned)
19. More features as needed

---

*Last Updated: February 3, 2026 (Session 6)*
