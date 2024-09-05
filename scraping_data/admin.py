from django.contrib import admin
from scraping_data.models import JobListing


@admin.register(JobListing)
class VacancyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "location",
        "years_of_experience",
        "salary",
        "english_level",
        "technologies",
        "date_posted",
        "seniority_level",
        "source"
    )
    search_fields = ("title", "company", "location", "technologies")
    list_filter = ("location", "technologies", "date_posted", "source")
