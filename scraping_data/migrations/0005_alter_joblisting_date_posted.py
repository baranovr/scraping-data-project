# Generated by Django 4.0.4 on 2024-09-01 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping_data', '0004_alter_joblisting_date_posted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joblisting',
            name='date_posted',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]