"""
Email helpers — each function sends one type of email using the matching
sender from settings.EMAIL_SENDERS.  All sends are wrapped in try/except
so a transport failure never crashes the calling view.
"""

import logging
from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

SENDERS = settings.EMAIL_SENDERS


# ── internal helper ────────────────────────────────────────────────────────

def _send(sender_key, to, subject, plain_body, html_body):
    """Fire-and-forget wrapper around Django's EmailMessage."""
    try:
        msg = EmailMessage(
            subject=subject,
            body=plain_body,
            from_email=SENDERS[sender_key],
            to=[to] if isinstance(to, str) else to,
        )
        msg.content_subtype = 'html'
        msg.body = html_body          # HTML version
        msg.extra_headers = {'X-Mailer': 'Talent Solutions'}
        msg.send(fail_silently=False)
    except Exception as exc:  # noqa: BLE001
        logger.error("Email send failed (sender=%s, to=%s): %s", sender_key, to, exc)


# ── 0. Login verification code ─────────────────────────────────────────────
# Sender: support@

def send_verification_code(user, code):
    """6-digit OTP sent to the user right after a traditional login attempt."""
    if not user.email:
        return

    name = user.first_name or user.username
    subject = "Your Verification Code – Talent Solutions"

    html = f"""
    <div style="font-family:'Segoe UI',sans-serif; max-width:560px; margin:0 auto; color:#374151;">
      <h2 style="color:#0891b2; margin-bottom:8px;">Email Verification</h2>
      <p>Hi <strong>{name}</strong>,</p>
      <p>Use the code below to verify your identity and complete your login.</p>
      <div style="text-align:center; margin:28px 0;">
        <span style="display:inline-block; padding:16px 36px; background:#f0fdff;
                     border:2px solid #0891b2; border-radius:12px;
                     font-size:32px; font-weight:700; color:#0891b2; letter-spacing:8px;">
          {code}
        </span>
      </div>
      <p style="color:#6b7280; font-size:14px;">
         This code is valid for <strong>10 minutes</strong>. Do not share it with anyone.</p>
      <p style="color:#9ca3af; font-size:12px; margin-top:24px;">— Talent Solutions</p>
    </div>"""

    plain = (
        f"Hi {name},\n\n"
        f"Your verification code is: {code}\n\n"
        f"This code is valid for 10 minutes. Do not share it with anyone.\n\n"
        f"— Talent Solutions"
    )

    _send('support', user.email, subject, plain, html)


# ── 1. Application submitted – confirmation to applicant ──────────────────
# Sender: welcome@

def send_application_confirmation(application):
    """Sent to the applicant right after they submit."""
    if not application.user or not application.user.email:
        return

    job_title = application.job.title
    company   = application.job.company_name
    name      = application.full_name

    subject = f"Application Received – {job_title}"

    html = f"""
    <div style="font-family:'Segoe UI',sans-serif; max-width:560px; margin:0 auto; color:#374151;">
      <h2 style="color:#0891b2; margin-bottom:8px;">Application Received</h2>
      <p>Hi <strong>{name}</strong>,</p>
      <p>Thank you for applying for <strong>{job_title}</strong> at <strong>{company}</strong>.
         Your application has been received and is now under review.</p>
      <table style="width:100%; border-collapse:collapse; margin:16px 0;">
        <tr><td style="padding:6px 0; color:#6b7280; width:140px;">Job</td>
            <td style="padding:6px 0; font-weight:600;">{job_title}</td></tr>
        <tr><td style="padding:6px 0; color:#6b7280;">Company</td>
            <td style="padding:6px 0; font-weight:600;">{company}</td></tr>
        <tr><td style="padding:6px 0; color:#6b7280;">Status</td>
            <td style="padding:6px 0; font-weight:600; color:#f59e0b;">Pending</td></tr>
      </table>
      <p style="color:#6b7280; font-size:14px;">
         We will be in touch soon. You can track your application status from
         <em>My Applications</em> on your dashboard.</p>
      <p style="color:#9ca3af; font-size:12px; margin-top:24px;">— Talent Solutions</p>
    </div>"""

    plain = (
        f"Hi {name},\n\n"
        f"Thank you for applying for {job_title} at {company}.\n"
        f"Your application is now pending review.\n\n"
        f"— Talent Solutions"
    )

    _send('welcome', application.user.email, subject, plain, html)


# ── 2. New application alert – to internal admin ──────────────────────────
# Sender: recruitment@

def send_new_application_alert(application):
    """Sent to the admin user(s) when a new application arrives."""
    from main.models import User  # avoid circular at module level

    admins = User.objects.filter(role='admin', email__gt='').values_list('email', flat=True)
    if not admins:
        return

    job_title  = application.job.title
    company    = application.job.company_name
    name       = application.full_name
    contact    = application.contact_number

    subject = f"New Application – {job_title} ({name})"

    html = f"""
    <div style="font-family:'Segoe UI',sans-serif; max-width:560px; margin:0 auto; color:#374151;">
      <h2 style="color:#0891b2; margin-bottom:8px;">New Application Received</h2>
      <p>A new application has been submitted for <strong>{job_title}</strong>.</p>
      <table style="width:100%; border-collapse:collapse; margin:16px 0;">
        <tr><td style="padding:6px 0; color:#6b7280; width:140px;">Applicant</td>
            <td style="padding:6px 0; font-weight:600;">{name}</td></tr>
        <tr><td style="padding:6px 0; color:#6b7280;">Contact</td>
            <td style="padding:6px 0;">{contact}</td></tr>
        <tr><td style="padding:6px 0; color:#6b7280;">Job</td>
            <td style="padding:6px 0; font-weight:600;">{job_title}</td></tr>
        <tr><td style="padding:6px 0; color:#6b7280;">Company</td>
            <td style="padding:6px 0;">{company}</td></tr>
      </table>
      <p style="color:#6b7280; font-size:14px;">
         Review the application from the <em>Applications</em> section in the admin panel.</p>
      <p style="color:#9ca3af; font-size:12px; margin-top:24px;">— Talent Solutions (Internal)</p>
    </div>"""

    plain = (
        f"New application for {job_title}:\n\n"
        f"  Applicant : {name}\n"
        f"  Contact   : {contact}\n"
        f"  Company   : {company}\n\n"
        f"Review it in the admin panel.\n\n"
        f"— Talent Solutions (Internal)"
    )

    _send('recruitment', list(admins), subject, plain, html)


# ── 3. Application status update – to applicant (non-rejection) ───────────
# Sender: hr@

_STATUS_LABELS = {
    'pending':     ('Pending',     '#f59e0b'),
    'reviewed':    ('Under Review','#3b82f6'),
    'shortlisted': ('Shortlisted', '#8b5cf6'),
    'accepted':    ('Accepted',    '#22c55e'),
}

_STATUS_MESSAGES = {
    'reviewed':    'Your application is currently being reviewed by the hiring team.',
    'shortlisted': 'Congratulations! You have been shortlisted for the next round.',
    'accepted':    'Congratulations! Your application has been accepted. The team will reach out with next steps.',
}


def send_application_status_update(application):
    """Sent to the applicant whenever the admin changes status (except rejection)."""
    if not application.user or not application.user.email:
        return
    if application.status in ('pending', 'rejected'):
        return  # pending = default; rejected has its own dedicated email

    job_title  = application.job.title
    company    = application.job.company_name
    name       = application.full_name
    status     = application.status
    label, color = _STATUS_LABELS.get(status, (status.capitalize(), '#6b7280'))
    message    = _STATUS_MESSAGES.get(status, '')

    subject = f"Application Update – {job_title}"

    html = f"""
    <div style="font-family:'Segoe UI',sans-serif; max-width:560px; margin:0 auto; color:#374151;">
      <h2 style="color:#0891b2; margin-bottom:8px;">Application Status Update</h2>
      <p>Hi <strong>{name}</strong>,</p>
      <p>Your application for <strong>{job_title}</strong> at <strong>{company}</strong> has been updated.</p>
      <div style="text-align:center; margin:20px 0;">
        <span style="display:inline-block; padding:6px 20px; background:{color}15; color:{color};
                     border-radius:9999px; font-weight:700; font-size:15px; border:1px solid {color}40;">
          {label}
        </span>
      </div>
      <p style="text-align:center; color:#6b7280;">{message}</p>
      <p style="color:#9ca3af; font-size:12px; margin-top:24px; text-align:center;">— Talent Solutions</p>
    </div>"""

    plain = (
        f"Hi {name},\n\n"
        f"Your application for {job_title} at {company} has been updated.\n\n"
        f"New status: {label}\n\n"
        f"{message}\n\n"
        f"— Talent Solutions"
    )

    _send('hr', application.user.email, subject, plain, html)


# ── 4. Rejection email – dedicated branded template ───────────────────────
# Sender: welcome@ (no-reply@projekthub.com)

def send_rejection_email(application):
    """Full branded rejection email sent when admin rejects an application."""
    if not application.user or not application.user.email:
        return

    from django.conf import settings as _settings
    site_url = _settings.SITE_URL

    name    = application.full_name
    job_title = application.job.title
    company   = application.job.company_name
    country   = application.job.get_country_display_name()
    reason    = application.rejection_reason or ''

    subject = f"Your Application for {job_title} – Decision"

    # ── reason card (only rendered when admin left a reason) ──
    reason_rows = ''
    if reason:
        reason_rows = f"""
        <tr>
          <td style="padding:20px 28px 0;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                   style="border-radius:8px; overflow:hidden; border:1px solid #fecaca;">
              <tr>
                <td style="background:#fee2e2; padding:10px 16px;">
                  <p style="margin:0; font-size:12px; font-weight:700; color:#991b1b;
                            text-transform:uppercase; letter-spacing:0.8px;">Feedback from the hiring team</p>
                </td>
              </tr>
              <tr>
                <td style="background:#fff5f5; padding:14px 16px;">
                  <p style="margin:0; font-size:14px; color:#7f1d1d; line-height:1.6;">{reason}</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{subject}</title></head>
<body style="margin:0; padding:0; background:#f3f4f6;
             font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">

<!-- outer wrapper -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="padding:32px 16px;" align="center">

      <!-- card -->
      <table role="presentation" width="600" cellpadding="0" cellspacing="0"
             style="max-width:600px; background:#ffffff; border-radius:12px; overflow:hidden;
                    box-shadow:0 4px 16px rgba(0,0,0,0.08);">

        <!-- ── dark header ── -->
        <tr>
          <td style="background:#0f172a; padding:28px 28px 24px; text-align:center;">
            <p style="margin:0; font-size:24px; font-weight:700; color:#ffffff;
                      letter-spacing:-0.3px;">Talent Solutions</p>
            <p style="margin:6px 0 0; font-size:13px; color:#64748b;">Your Career, Our Priority</p>
          </td>
        </tr>

        <!-- ── red icon circle ── -->
        <tr>
          <td style="background:#f8fafc; padding:28px 28px 0;" align="center">
            <table role="presentation" cellpadding="0" cellspacing="0">
              <tr>
                <td width="64" height="64" style="background:#fee2e2; border-radius:50%;"
                    align="center" valign="middle">
                  <!-- simple ✕ mark -->
                  <span style="font-size:28px; color:#ef4444; font-weight:700;">✕</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ── title + subtitle ── -->
        <tr>
          <td style="background:#f8fafc; padding:16px 28px 0;" align="center">
            <p style="margin:0; font-size:20px; font-weight:700; color:#1f2937;">Application Decision</p>
            <p style="margin:8px 0 0; font-size:14px; color:#6b7280;">We have completed our review process</p>
          </td>
        </tr>

        <!-- ── greeting ── -->
        <tr>
          <td style="padding:24px 28px 0;">
            <p style="margin:0; font-size:15px; color:#374151; line-height:1.7;">
              Hi <strong style="color:#1f2937;">{name}</strong>,
            </p>
            <p style="margin:14px 0 0; font-size:15px; color:#374151; line-height:1.7;">
              Thank you for taking the time to apply for the position listed below.
              After a careful and thorough review of all applications received, we regret
              to inform you that your application has <strong style="color:#dc2626;">not been selected</strong> at this time.
            </p>
          </td>
        </tr>

        <!-- ── job details card ── -->
        <tr>
          <td style="padding:20px 28px 0;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                   style="border-radius:10px; overflow:hidden; border:1px solid #e5e7eb;">
              <!-- card header -->
              <tr>
                <td style="background:#eef2ff; padding:11px 18px;">
                  <p style="margin:0; font-size:12px; font-weight:700; color:#4338ca;
                            text-transform:uppercase; letter-spacing:0.8px;">Position Details</p>
                </td>
              </tr>
              <!-- rows -->
              <tr>
                <td style="padding:0 18px;">
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="padding:11px 0; border-bottom:1px solid #f3f4f6; width:90px;" valign="top">
                        <p style="margin:0; font-size:13px; color:#6b7280;">Position</p>
                      </td>
                      <td style="padding:11px 0; border-bottom:1px solid #f3f4f6;" valign="top">
                        <p style="margin:0; font-size:14px; font-weight:600; color:#1f2937;">{job_title}</p>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:11px 0; border-bottom:1px solid #f3f4f6;" valign="top">
                        <p style="margin:0; font-size:13px; color:#6b7280;">Company</p>
                      </td>
                      <td style="padding:11px 0; border-bottom:1px solid #f3f4f6;" valign="top">
                        <p style="margin:0; font-size:14px; font-weight:600; color:#1f2937;">{company}</p>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:11px 0;" valign="top">
                        <p style="margin:0; font-size:13px; color:#6b7280;">Location</p>
                      </td>
                      <td style="padding:11px 0;" valign="top">
                        <p style="margin:0; font-size:14px; font-weight:600; color:#1f2937;">{country}</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
              <!-- status badge row -->
              <tr>
                <td style="background:#fef2f2; padding:12px 18px; border-top:1px solid #fecaca;"
                    align="center">
                  <span style="display:inline-block; padding:5px 18px; background:#ef4444;
                               color:#ffffff; border-radius:20px; font-size:13px; font-weight:700;
                               letter-spacing:0.5px;">
                    Not Selected
                  </span>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ── rejection reason (conditional) ── -->
        {reason_rows}

        <!-- ── closing message ── -->
        <tr>
          <td style="padding:24px 28px 0;">
            <p style="margin:0; font-size:15px; color:#374151; line-height:1.7;">
              We truly value the interest you showed in joining our team. Please know that
              this decision was made after careful consideration and was not an easy one.
            </p>
            <p style="margin:14px 0 0; font-size:15px; color:#374151; line-height:1.7;">
              We encourage you to continue exploring opportunities that match your skills
              and experience. You are always welcome to apply again for any future positions
              that interest you.
            </p>
          </td>
        </tr>

        <!-- ── browse jobs button ── -->
        <tr>
          <td style="padding:28px 28px 0;" align="center">
            <a href="{site_url}/jobs/"
               style="display:inline-block; padding:11px 30px;
                      background:linear-gradient(135deg, #0891b2, #2563eb);
                      color:#ffffff; text-decoration:none; border-radius:8px;
                      font-size:14px; font-weight:600; letter-spacing:0.2px;">
              Browse More Jobs
            </a>
          </td>
        </tr>

        <!-- ── footer ── -->
        <tr>
          <td style="padding:32px 28px 28px; margin-top:8px; border-top:1px solid #f3f4f6;">
            <p style="margin:0; text-align:center; font-size:12px; color:#9ca3af; line-height:1.7;">
              This email was sent by <strong style="color:#6b7280;">Talent Solutions</strong>
              because you submitted an application on our platform.<br>
              If you have any questions, feel free to contact our support team.<br><br>
              &copy; 2026 Talent Solutions. All rights reserved.
            </p>
          </td>
        </tr>

      </table><!-- /card -->
    </td>
  </tr>
</table><!-- /outer -->

</body>
</html>"""

    plain = (
        f"Hi {name},\n\n"
        f"Thank you for taking the time to apply for {job_title} at {company}.\n\n"
        f"After a careful and thorough review, we regret to inform you that your\n"
        f"application has not been selected at this time.\n\n"
    )
    if reason:
        plain += f"Feedback from the hiring team:\n{reason}\n\n"
    plain += (
        f"We truly value the interest you showed in joining our team and encourage\n"
        f"you to continue exploring opportunities that match your skills.\n"
        f"You are always welcome to apply again for future positions.\n\n"
        f"Browse more jobs: {site_url}/jobs/\n\n"
        f"— Talent Solutions"
    )

    _send('welcome', application.user.email, subject, plain, html)
