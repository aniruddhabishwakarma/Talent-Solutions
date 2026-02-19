from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_contactmessage_company_google_maps_embed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='bio',
            field=models.TextField(help_text='Biography'),
        ),
    ]
