from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_alter_teammember_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='hero_slogan',
            field=models.CharField(blank=True, help_text='Hero section heading (e.g. "Find the right talent, without the hassle.")', max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='hero_description',
            field=models.TextField(blank=True, help_text='Hero section subtext paragraph', null=True),
        ),
    ]
