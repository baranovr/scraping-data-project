import os
import csv

import django
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from multiprocessing import Process, Queue

from scrape_items.djinni_scraper.djinni_scraper.spiders.djinni_spider import DjinniSpider
from scrape_items.linkedin_scraper.linkedin_scraper.spiders.linkedin_spider import LinkedInSpider
from scrape_items.work_scraper.work_scraper.spiders.work_spider import WorkSpider

from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scraping_data_project.settings")
django.setup()

from scraping_data.models import JobListing


def run_spider(spider_class, queue):
    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    process = CrawlerProcess({
        'DOWNLOAD_DELAY': 5,
        'RETRY_TIMES': 25,
        'RETRY_HTTP_CODES': [429]
    })
    process.crawl(spider_class)
    process.start()

    queue.put(results)


def scrape_djinni(request):
    queue = Queue()
    process = Process(target=run_spider, args=(DjinniSpider, queue))
    process.start()
    process.join()

    results = queue.get()
    return JsonResponse(results, safe=False)


def scrape_work(request):
    queue = Queue()
    process = Process(target=run_spider, args=(WorkSpider, queue))
    process.start()
    process.join()

    results = queue.get()
    return JsonResponse(results, safe=False)


def scrape_linkedin(request):
    queue = Queue()
    process = Process(target=run_spider, args=(LinkedInSpider, queue))
    process.start()
    process.join()

    results = queue.get()
    return JsonResponse(results, safe=False)


def download_csv(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="tech_stats.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "Title",
            "Company",
            "Location",
            "Years_of_experience",
            "Salary",
            "Seniority_level",
            "English_level",
            "Technologies",
            "Date_Posted",
            "Source"
        ]
    )

    for vacancy in JobListing.objects.all():
        writer.writerow(
            [
                vacancy.title,
                vacancy.company,
                vacancy.location,
                vacancy.years_of_experience,
                vacancy.salary,
                vacancy.seniority_level,
                vacancy.english_level,
                vacancy.technologies,
                vacancy.date_posted,
                vacancy.source
            ]
        )
    return response


def index(request):
    return render(request, "index.html")
