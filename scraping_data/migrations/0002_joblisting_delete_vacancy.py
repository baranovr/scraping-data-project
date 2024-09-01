# Generated by Django 4.0.4 on 2024-09-01 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('years_of_experience', models.CharField(blank=True, max_length=50, null=True)),
                ('salary', models.CharField(blank=True, max_length=50, null=True)),
                ('english_level', models.CharField(blank=True, max_length=50, null=True)),
                ('technologies', models.CharField(max_length=255)),
                ('views_popularity', models.IntegerField(blank=True, null=True)),
                ('date_posted', models.DateField(blank=True, null=True)),
                ('source', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name_plural': 'Vacancies',
            },
        ),
        migrations.DeleteModel(
            name='Vacancy',
        ),
    ]