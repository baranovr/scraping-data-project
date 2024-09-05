import os
import random
import re
from typing import Any
from decimal import Decimal
from datetime import datetime

import django
import scrapy
from scrapy.http.response import Response
from selenium import webdriver

from scraping_data_project.settings import TECHNOLOGIES, USER_AGENT_LIST, SENIORITY_LEVELS

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scraping_data_project.settings")
django.setup()

from scraping_data.models import JobListing


class WorkSpider(scrapy.Spider):
    name = "work"
    allowed_domains = ["www.work.ua"]
    start_urls = ["https://www.work.ua/jobs-python/"]

    def __init__(self, *args, **kwargs) -> None:
        super(WorkSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Edge()

    def closed(self, *args, **kwargs) -> None:
        self.driver.close()
        self.driver.quit()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers={"User-Agent": random.choice(USER_AGENT_LIST)}, callback=self.parse)

    def parse(self, response: Response) -> None:
        jobs = response.css("h2.my-0")

        for job in jobs:
            job_url = response.urljoin(job.css("a::attr(href)").get())
            if job_url:
                yield scrapy.Request(job_url, callback=self.get_all_data)

        next_page = response.css('ul.pagination li.add-left-default a.link-icon::attr(href)').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def get_all_data(self, response: Response) -> dict:
        data = {
            "title": self.parse_title(response=response),
            "company": self.parse_company(response=response),
            "location": self.parse_location(response=response),
            "years_of_experience": self.parse_experience(response=response),
            "salary": self.parse_salary(response=response),
            "date_posted": self.parse_date_posted(response=response),
            "seniority_level": self.parse_seniority_level(response=response),
            "english_level": self.parse_eng_lvl(response=response),
            "technologies": self.parse_technologies(response=response),
            "source": response.url
        }

        job_listing = JobListing(
            title=data["title"],
            company=data["company"],
            location=data["location"],
            years_of_experience=data["years_of_experience"],
            salary=data["salary"],
            english_level=data["english_level"],
            technologies=", ".join(data["technologies"]),
            seniority_level=data["seniority_level"],
            date_posted=data["date_posted"],
            source=data["source"]
        )
        job_listing.save()
        yield data

    def parse_title(self, response: Response) -> str:
        text = response.css("h1#h1-name::text").getall()
        title = " ".join([t.strip() for t in text])
        return title.strip() if title else ""

    def parse_company(self, response: Response) -> str:
        company_li = response.css("li")

        for li in company_li:
            if li.css("span.glyphicon-company"):
                company = li.css("span.strong-500::text").get()
                return company.strip() if company and "грн" not in company else ""

        return ""

    def parse_location(self, response: Response) -> str:
        location_not_remote = response.css("li:has(span.glyphicon-map-marker)")

        if location_not_remote:
            location = location_not_remote.css("::text").getall()
            location = "".join(location).strip().split(",")[0]
            return location if location else ""
        else:
            return "Remote"

    def parse_experience(self, response: Response) -> int | None:
        experience = response.css("li:has(span.glyphicon-tick)")
        if experience:
            experience = experience.css("::text").getall()
            for exp in experience:
                if "рок" in exp:
                    match = re.search(r'\d+', exp)
                    if match:
                        return int(match.group(0))

        return None

    def parse_salary(self, response: Response) -> Decimal | None:
        salary_li = response.css("li")
        for li in salary_li:
            if li.css("span.glyphicon-hryvnia"):
                salary = response.css("span.strong-500::text").get().replace("&thinsp;", " ")
                match = re.search(r'\d+', salary)
                if match:
                    return Decimal(match.group(0))

        return None

    def parse_date_posted(self, response: Response) -> datetime | None:
        date_posted = response.css("time::attr(datetime)").get()
        if date_posted:
            return datetime.strptime(date_posted.strip(), "%Y-%m-%d")
        return None

    def parse_seniority_level(self, response: Response) -> str:
        job_description = response.css("#job-description *::text").getall()
        text = " ".join(job_description).strip().lower()

        for level in SENIORITY_LEVELS:
            if level in text:
                return level.capitalize()

        return "Not specified"

    def parse_eng_lvl(self, response: Response) -> str:
        ENGLISH_LEVELS = {
            "b1": "intermediate",
            "b2": "upper-Intermediate",
            "c1": "advanced"
        }

        lang_li = response.css("li")
        for li in lang_li:
            if li.css("span.glyphicon-language"):
                lang = li.css("span.glyphicon-language::text").get()
                if "cеред" in lang:
                    return "Intermediate"
            else:
                job_description = response.css("#job-description *::text").getall()
                text = " ".join(job_description).strip()

                for level_v in ENGLISH_LEVELS.values():
                    if level_v.lower() in text.lower():
                        return level_v.capitalize()

                for level_k in ENGLISH_LEVELS.keys():
                    if level_k.lower() in text.lower():
                        return ENGLISH_LEVELS[level_k.lower()].capitalize()

        return ""

    def parse_technologies(self, response: Response) -> list[str]:
        job_description = response.css("#job-description *::text").getall()
        text = " ".join(job_description).strip()

        technologies = []

        for tech in TECHNOLOGIES:
            if tech.lower() in text.lower():
                technologies.append(tech)

        return technologies
