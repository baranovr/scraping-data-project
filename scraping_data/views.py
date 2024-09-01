import csv
import os
import django
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.core.wsgi import get_wsgi_application

from multiprocessing import Process, Queue

from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from scraping_data.models import JobListing, Technology, HistoricalData
from scrape_items.work.work.spiders.djinni_spider import DjinniSpider
from scrape_items.work.work.spiders.work_spider import WorkSpider


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scraping_data_project.settings")
django.setup()


def run_spider(spider_class, results_queue):
    def crawler_results(signal, sender, item, response, spider):
        results_queue.put(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    process = CrawlerProcess(get_project_settings())
    process.crawl(spider_class)
    process.start()


def scrape_djinni(request):
    results_queue = Queue()

    djinni_process = Process(target=run_spider, args=(DjinniSpider, results_queue))
    djinni_process.start()
    djinni_process.join()

    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    # for item in results:
    #     job_listing = JobListing(
    #         title=item['title'],
    #         company=item['company'],
    #         location=item['location'],
    #         years_of_experience=item['years_of_experience'],
    #         salary=item['salary'],
    #         date_posted=item['date_posted'],
    #         views_popularity=item['views_popularity'],
    #         english_level=item['english_level'],
    #         source=item['source']
    #     )
    #     job_listing.save()
    #
    #     for tech in item['technologies']:
    #         technology, created = Technology.objects.get_or_create(name=tech)
    #         job_listing.technologies.add(technology)

    return JsonResponse(results, safe=False)


def scrape_work(request):
    results_queue = Queue()

    work_process = Process(target=run_spider, args=(WorkSpider, results_queue))
    work_process.start()
    work_process.join()

    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    # for item in results:
    #     job_listing = JobListing(
    #         title=item['title'],
    #         company=item['company'],
    #         location=item['location'],
    #         years_of_experience=item['years_of_experience'],
    #         salary=item['salary'],
    #         date_posted=item['date_posted'],
    #         views_popularity=item['views_popularity'],
    #         english_level=item['english_level'],
    #         source=item['source']
    #     )
    #     job_listing.save()
    #
    #     for tech in item['technologies']:
    #         technology, created = Technology.objects.get_or_create(name=tech)
    #         job_listing.technologies.add(technology)

    return JsonResponse(results, safe=False)


def download_csv(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="tech_stats.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ["Title", "Company", "Location", "Technology", "Experience", "Salary", "Date Posted", "Views", "Source"]
    )
    for vacancy in JobListing.objects.all():
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


def job_listings(request):
    listings = JobListing.objects.all()
    return render(request, 'job_listings.html', {'listings': listings})


def historical_data(request):
    data = HistoricalData.objects.all().order_by('date')
    return render(request, 'historical_data.html', {'data': data})


def index(request):
    return render(request, "index.html")
