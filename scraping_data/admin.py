from django.contrib import admin
from scraping_data.models import Vacancy, Technology, HistoricalData


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = (
        "title", "company", "location", "technology", "experience", "date_posted", "views_popularity", "source"
    )
    search_fields = ("title", "company", "location", "technology")
    list_filter = ("location", "technology", "date_posted", "source")


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "vacancy_count")
    search_fields = ("name",)


@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ("technology", "date", "vacancy_count")
    list_filter = ("date",)
    search_fields = ("technology__name",)
