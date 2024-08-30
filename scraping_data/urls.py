from django.urls import path
from scraping_data import views


urlpatterns = [
    path("", views.index, name="index"),
    path("vacancies/", views.vacancy_list, name="vacancy_list"),
    path("technology-stats/", views.technology_stats, name="technology_stats"),
    path("historical-data/", views.historical_data, name="historical_data"),
    path("download-csv/", views.download_csv, name="download_csv"),
    path("scrape_djinni/", views.scrape_djinni, name="scrape_djinni"),
]

app_name = "scraping_data"
