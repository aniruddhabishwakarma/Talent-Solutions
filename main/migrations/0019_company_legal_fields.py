from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_company_hero_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='registration_number',
            field=models.CharField(blank=True, help_text='Company Registration Number', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='license_number',
            field=models.CharField(blank=True, help_text='Foreign Employment License Number (DOFE)', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='pan_number',
            field=models.CharField(blank=True, help_text='PAN / Tax Identification Number', max_length=50, null=True),
        ),
    ]
