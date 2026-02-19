from django.db import migrations, models
import main.models.hero_photo_model


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_company_legal_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Photo for the hero gallery (recommended: 800x600px or similar landscape)', upload_to=main.models.hero_photo_model.upload_hero_photo)),
                ('caption', models.CharField(blank=True, help_text="Optional short caption shown on hover (e.g., 'MoU Signing Ceremony')", max_length=200, null=True)),
                ('display_order', models.IntegerField(default=0, help_text='Lower numbers appear first')),
                ('is_active', models.BooleanField(default=True, help_text='Only active photos are shown on the website')),
                ('created_at', models.BigIntegerField(editable=False)),
            ],
            options={
                'verbose_name': 'Hero Photo',
                'verbose_name_plural': 'Hero Photos',
                'db_table': 'hero_photos',
                'ordering': ['display_order', 'id'],
            },
        ),
    ]
