from django.urls import path
from scraping_data import views


urlpatterns = [
    path("", views.index, name="index"),
    path("scrape-djinni/", views.scrape_djinni, name="scrape_djinni"),
    path("scrape-work/", views.scrape_work, name="scrape_work"),
    path("download-csv/", views.download_csv, name="download_csv"),
    path("job-listings/", views.job_listings, name="job_listings"),
    path("historical-data/", views.historical_data, name="historical_data"),
]

app_name = "scraping_data"
