from django.shortcuts import render
from django.http import HttpResponse
from .models import Vacancy, Technology, HistoricalData
import csv


def index(request):
    return render(request, "index.html")


def vacancy_list(request):
    vacancies = Vacancy.objects.all()
    return render(request, "vacancy_list.html", {"vacancies": vacancies})


def technology_stats(request):
    tech_stats = Technology.objects.all().order_by("-vacancy_count")
    return render(request, "technology_stats.html", {"tech_stats": tech_stats})


def download_csv(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="tech_stats.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["Title", "Company", "Location", "Technology", "Experience", "Salary", "Date Posted", "Views", "Source"]
    )

    for vacancy in Vacancy.objects.all():
        writer.writerow(
            [
                vacancy.title,
                vacancy.company,
                vacancy.location,
                vacancy.technology,
                vacancy.experience,
                vacancy.salary,
                vacancy.date_posted,
                vacancy.views_popularity,
                vacancy.source
            ]
        )

    return response


def historical_data(request):
    history = HistoricalData.objects.all().order_by("date", "technology__name")
    return render(request, "historical_data.html", {"history": history})