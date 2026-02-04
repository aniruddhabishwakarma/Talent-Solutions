from django.db import models
from django.utils.text import slugify
from django.conf import settings
import time


# Countries grouped by first letter for dropdown
COUNTRIES_BY_LETTER = {
    'A': [
        ('AF', 'Afghanistan'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AD', 'Andorra'),
        ('AO', 'Angola'), ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'),
        ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'),
    ],
    'B': [
        ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'),
        ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'),
        ('BT', 'Bhutan'), ('BO', 'Bolivia'), ('BA', 'Bosnia and Herzegovina'),
        ('BW', 'Botswana'), ('BR', 'Brazil'), ('BN', 'Brunei'), ('BG', 'Bulgaria'),
        ('BF', 'Burkina Faso'), ('BI', 'Burundi'),
    ],
    'C': [
        ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('CV', 'Cape Verde'),
        ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'),
        ('CO', 'Colombia'), ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo (DRC)'),
        ('CR', 'Costa Rica'), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
    ],
    'D': [
        ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'),
    ],
    'E': [
        ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'),
        ('ER', 'Eritrea'), ('EE', 'Estonia'), ('SZ', 'Eswatini'), ('ET', 'Ethiopia'),
    ],
    'F': [
        ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'),
    ],
    'G': [
        ('GA', 'Gabon'), ('GM', 'Gambia'), ('GE', 'Georgia'), ('DE', 'Germany'),
        ('GH', 'Ghana'), ('GR', 'Greece'), ('GD', 'Grenada'), ('GT', 'Guatemala'),
        ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'),
    ],
    'H': [
        ('HT', 'Haiti'), ('HN', 'Honduras'), ('HU', 'Hungary'),
    ],
    'I': [
        ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran'),
        ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IL', 'Israel'), ('IT', 'Italy'),
        ('CI', 'Ivory Coast'),
    ],
    'J': [
        ('JM', 'Jamaica'), ('JP', 'Japan'), ('JO', 'Jordan'),
    ],
    'K': [
        ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KP', 'North Korea'),
        ('KR', 'South Korea'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'),
    ],
    'L': [
        ('LA', 'Laos'), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'),
        ('LR', 'Liberia'), ('LY', 'Libya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
    ],
    'M': [
        ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'),
        ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MR', 'Mauritania'),
        ('MU', 'Mauritius'), ('MX', 'Mexico'), ('FM', 'Micronesia'), ('MD', 'Moldova'),
        ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MA', 'Morocco'),
        ('MZ', 'Mozambique'), ('MM', 'Myanmar'),
    ],
    'N': [
        ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'),
        ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'),
        ('MK', 'North Macedonia'), ('NO', 'Norway'),
    ],
    'O': [
        ('OM', 'Oman'),
    ],
    'P': [
        ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestine'), ('PA', 'Panama'),
        ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'),
        ('PL', 'Poland'), ('PT', 'Portugal'),
    ],
    'Q': [
        ('QA', 'Qatar'),
    ],
    'R': [
        ('RO', 'Romania'), ('RU', 'Russia'), ('RW', 'Rwanda'),
    ],
    'S': [
        ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'),
        ('VC', 'Saint Vincent and the Grenadines'), ('WS', 'Samoa'),
        ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'), ('SA', 'Saudi Arabia'),
        ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'),
        ('SG', 'Singapore'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'),
        ('SO', 'Somalia'), ('ZA', 'South Africa'), ('SS', 'South Sudan'), ('ES', 'Spain'),
        ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SE', 'Sweden'),
        ('CH', 'Switzerland'), ('SY', 'Syria'),
    ],
    'T': [
        ('TW', 'Taiwan'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania'), ('TH', 'Thailand'),
        ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'),
        ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TV', 'Tuvalu'),
    ],
    'U': [
        ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'),
        ('GB', 'United Kingdom'), ('US', 'United States'), ('UY', 'Uruguay'),
        ('UZ', 'Uzbekistan'),
    ],
    'V': [
        ('VU', 'Vanuatu'), ('VA', 'Vatican City'), ('VE', 'Venezuela'), ('VN', 'Vietnam'),
    ],
    'Y': [
        ('YE', 'Yemen'),
    ],
    'Z': [
        ('ZM', 'Zambia'), ('ZW', 'Zimbabwe'),
    ],
}

# Flatten for model choices
COUNTRY_CHOICES = []
for letter in sorted(COUNTRIES_BY_LETTER.keys()):
    COUNTRY_CHOICES.extend(COUNTRIES_BY_LETTER[letter])


CURRENCY_CHOICES = [
    ('USD', 'USD - US Dollar'),
    ('AED', 'AED - UAE Dirham'),
    ('SAR', 'SAR - Saudi Riyal'),
    ('QAR', 'QAR - Qatari Riyal'),
    ('KWD', 'KWD - Kuwaiti Dinar'),
    ('BHD', 'BHD - Bahraini Dinar'),
    ('OMR', 'OMR - Omani Rial'),
    ('MYR', 'MYR - Malaysian Ringgit'),
    ('SGD', 'SGD - Singapore Dollar'),
    ('EUR', 'EUR - Euro'),
    ('GBP', 'GBP - British Pound'),
    ('AUD', 'AUD - Australian Dollar'),
    ('CAD', 'CAD - Canadian Dollar'),
    ('JPY', 'JPY - Japanese Yen'),
    ('CNY', 'CNY - Chinese Yuan'),
    ('INR', 'INR - Indian Rupee'),
    ('NPR', 'NPR - Nepalese Rupee'),
]

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('any', 'Any'),
]

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('closed', 'Closed'),
]


class Job(models.Model):
    """Model for job postings."""

    # Basic Info
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    company_name = models.CharField(max_length=200, default='', help_text="Employer company name")
    description = models.TextField(help_text="Full job description including benefits")

    # Location
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    city = models.CharField(max_length=100, blank=True, null=True)

    # Contract
    contract_duration = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Contract duration in months"
    )

    # Benefits
    fooding = models.BooleanField(default=False, help_text="Is food provided?")
    lodging = models.BooleanField(default=False, help_text="Is lodging/accommodation provided?")
    overtime_available = models.BooleanField(default=False, help_text="Is overtime available?")

    # Salary
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    salary_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')

    # Requirements
    skills = models.ManyToManyField('Skill', related_name='jobs', blank=True)
    education = models.CharField(max_length=200, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0, help_text="Minimum years of experience")
    age_min = models.PositiveIntegerField(blank=True, null=True)
    age_max = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='any')

    # Vacancies
    vacancies = models.PositiveIntegerField(default=1)

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    deadline = models.DateField(help_text="Application deadline")
    is_urgent = models.BooleanField(default=False)

    # Timestamps (epoch milliseconds)
    created_at = models.BigIntegerField(editable=False)
    updated_at = models.BigIntegerField(editable=False)

    # Relations
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )

    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_country_display()}"

    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Set created_at on first save (epoch milliseconds)
        if not self.created_at:
            self.created_at = int(time.time() * 1000)

        # Always update updated_at (epoch milliseconds)
        self.updated_at = int(time.time() * 1000)

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if the job deadline has passed."""
        from django.utils import timezone
        return self.deadline < timezone.now().date()

    def get_auto_status(self):
        """Get the automatic status based on deadline."""
        if self.status == 'draft':
            return 'draft'
        if self.is_expired:
            return 'closed'
        return 'active'

    def get_country_display_name(self):
        """Get full country name."""
        return dict(COUNTRY_CHOICES).get(self.country, self.country)

    def get_salary_display(self):
        """Get formatted salary with currency."""
        return f"{self.salary_currency} {self.salary:,.2f}"

    @property
    def created_at_datetime(self):
        """Convert epoch milliseconds to datetime."""
        from datetime import datetime
        return datetime.fromtimestamp(self.created_at / 1000)

    @property
    def updated_at_datetime(self):
        """Convert epoch milliseconds to datetime."""
        from datetime import datetime
        return datetime.fromtimestamp(self.updated_at / 1000)
