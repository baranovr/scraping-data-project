from django.urls import path
from scraping_data import views


urlpatterns = [
    path("", views.index, name="index"),
    path("scrape_djinni/", views.scrape_djinni, name="scrape_djinni"),
    path("scrape_work/", views.scrape_work, name="scrape_work"),
    path("download-csv/", views.download_csv, name="download_csv"),
]

app_name = "scraping_data"
