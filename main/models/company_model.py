from django.db import models


class Company(models.Model):
    """
    Company profile model - stores the main company information.
    This is a singleton model (only one company profile).
    """

    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    ]

    COMPANY_TYPE_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
        ('startup', 'Startup'),
        ('ngo', 'NGO'),
        ('government', 'Government'),
    ]

    # Basic Information
    company_name = models.CharField(max_length=255, help_text='Official company name')
    logo = models.ImageField(upload_to='company/', blank=True, null=True, help_text='Company logo')
    tagline = models.CharField(max_length=255, blank=True, null=True, help_text='Short slogan or motto')
    website = models.URLField(blank=True, null=True, help_text='Company website URL')
    industry = models.CharField(max_length=100, blank=True, null=True, help_text='Industry type')

    # Contact Details
    email = models.EmailField(help_text='Primary contact email')
    phone = models.CharField(max_length=20, help_text='Contact phone number')
    alternate_phone = models.CharField(max_length=20, blank=True, null=True, help_text='Secondary phone')
    address = models.TextField(help_text='Street address')
    city = models.CharField(max_length=100, help_text='City')
    state = models.CharField(max_length=100, help_text='State/Province')
    country = models.CharField(max_length=100, help_text='Country')
    postal_code = models.CharField(max_length=20, help_text='ZIP/Postal code')

    # Company Details
    about = models.TextField(blank=True, null=True, help_text='About us description')
    founded_year = models.PositiveIntegerField(blank=True, null=True, help_text='Year company was founded')
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True, null=True, help_text='Employee count range')
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPE_CHOICES, blank=True, null=True, help_text='Type of company')

    # Social Media
    facebook = models.URLField(blank=True, null=True, help_text='Facebook page URL')
    twitter = models.URLField(blank=True, null=True, help_text='Twitter/X profile URL')
    instagram = models.URLField(blank=True, null=True, help_text='Instagram profile URL')
    tiktok = models.URLField(blank=True, null=True, help_text='TikTok profile URL')
    youtube = models.URLField(blank=True, null=True, help_text='YouTube channel URL')
    whatsapp = models.URLField(blank=True, null=True, help_text='WhatsApp business URL')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company'
        verbose_name = 'Company'
        verbose_name_plural = 'Company'

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        """Ensure only one company profile exists (singleton pattern)."""
        if not self.pk and Company.objects.exists():
            # Update existing instead of creating new
            existing = Company.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_company(cls):
        """Get or create the company profile."""
        company, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'company_name': 'Talent Solutions',
                'email': 'info@talentsolutions.com',
                'phone': '+1234567890',
                'address': '123 Business Street',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'postal_code': '10001',
            }
        )
        return company
