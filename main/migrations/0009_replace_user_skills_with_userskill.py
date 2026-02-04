from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_add_user_skills_profile_complete_and_user_document'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='skills',
        ),
        migrations.CreateModel(
            name='UserSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_skills', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_skills',
                'ordering': ['name'],
                'unique_together': {('user', 'name')},
            },
        ),
    ]
