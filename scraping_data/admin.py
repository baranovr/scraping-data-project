from django.contrib import admin
from scraping_data.models import JobListing, Technology, HistoricalData


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
        "views_popularity",
        "source"
    )
    search_fields = ("title", "company", "location", "technologies")
    list_filter = ("location", "technologies", "date_posted", "source")


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "vacancy_count")
    search_fields = ("name",)


@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ("technology", "date", "vacancy_count")
    list_filter = ("date",)
    search_fields = ("date",)
