from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from main.models import ContactMessage


def submit_contact(request):
    """
    Handle contact form submission
    """
    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Validate required fields
        if not all([full_name, email, subject, message_text]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('home')

        try:
            # Save to database
            contact_message = ContactMessage.objects.create(
                full_name=full_name,
                email=email,
                phone=phone if phone else None,
                subject=subject,
                message=message_text
            )

            # Send confirmation email to user
            send_confirmation_email(full_name, email, subject)

            # Send notification to admin
            send_admin_notification(full_name, email, phone, subject, message_text)

            messages.success(request, f'Thank you {full_name}! Your message has been sent. We\'ll get back to you soon.')
            return redirect('home')

        except Exception as e:
            print(f"Error saving contact message: {e}")
            messages.error(request, 'Sorry, something went wrong. Please try again later.')
            return redirect('home')

    # If not POST, redirect to home
    return redirect('home')


def send_confirmation_email(full_name, user_email, subject):
    """
    Send confirmation email to user
    """
    try:
        email_subject = "We received your message - Talent Solutions"
        email_message = f"""
Hello {full_name},

Thank you for contacting Talent Solutions!

We have received your message regarding "{subject}" and will get back to you as soon as possible.

Our team typically responds within 24-48 hours during business hours (Sunday-Friday, 10 AM - 5 PM).

If your inquiry is urgent, please feel free to call us at:
{settings.EMAIL_SENDERS.get('support', 'no-reply@talentsolutions.com.np')}

Best regards,
The Talent Solutions Team

---
This is an automated confirmation email. Please do not reply to this email.
"""

        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.EMAIL_SENDERS.get('support', 'no-reply@talentsolutions.com.np'),
            recipient_list=[user_email],
            fail_silently=False,
        )
        print(f"Confirmation email sent to {user_email}")
    except Exception as e:
        print(f"Error sending confirmation email: {e}")


def send_admin_notification(full_name, user_email, phone, subject, message_text):
    """
    Send notification email to admin/recruitment team
    """
    try:
        from main.models import Company

        # Get company email or fallback to default
        try:
            company = Company.objects.first()
            admin_email = company.email if company else 'info@talentsolutions.com.np'
        except:
            admin_email = 'info@talentsolutions.com.np'

        email_subject = f"New Contact Form Submission: {subject}"
        email_message = f"""
New contact form submission received:

From: {full_name}
Email: {user_email}
Phone: {phone if phone else 'Not provided'}

Subject: {subject}

Message:
{message_text}

---
Submitted via Talent Solutions website contact form
Reply to this inquiry: {user_email}
"""

        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.EMAIL_SENDERS.get('support', 'no-reply@talentsolutions.com.np'),
            recipient_list=[admin_email],
            fail_silently=False,
        )
        print(f"Admin notification sent to {admin_email}")
    except Exception as e:
        print(f"Error sending admin notification: {e}")
