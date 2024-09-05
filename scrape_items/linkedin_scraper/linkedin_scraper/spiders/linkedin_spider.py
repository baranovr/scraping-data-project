import os
from typing import Any
from decimal import Decimal
from datetime import datetime

import django
import scrapy
import re

from scrapy.http.response import Response

from scraping_data_project.settings import TECHNOLOGIES

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scraping_data_project.settings")
django.setup()

from scraping_data.models import JobListing

JOB_DESCRIPTION = (
    ".show-more-less-html__markup.show-more-less-html__markup--clamp-after-5 p::text, "
    ".show-more-less-html__markup.show-more-less-html__markup--clamp-after-5 p br::text, "
    ".show-more-less-html__markup.show-more-less-html__markup--clamp-after-5 p strong::text, "
    ".show-more-less-html__markup.show-more-less-html__markup--clamp-after-5 ul li::text"
)

class LinkedInSpider(scrapy.Spider):
    name = "linkedin"
    api_url = "https://www.linkedin.com/jobs/search?keywords=Junior%2BPython%2BDeveloper&location=Ukraine&geoId=&trk=public_jobs_jobs-search-bar_search-submit"

    max_requests = 150
    request_count = 0

    def start_requests(self) -> None:
        first_job_on_page = 0
        first_url = self.api_url + str(first_job_on_page)
        yield scrapy.Request(
            url=first_url,
            callback=self.parse_job,
            meta={"first_job_on_page": first_job_on_page},
        )

    def parse_job(self, response: Response) -> None:
        first_job_on_page = response.meta["first_job_on_page"]
        jobs = response.css("li")

        num_jobs_returned = len(jobs)

        for job in jobs:
            if self.request_count >= self.max_requests:
                self.crawler.engine.close_spider(self)
                return

            job_item = {
                "title": job.css("h3.base-search-card__title::text").get(default="").strip(),
                "company": job.css("h4.base-search-card__subtitle a::text").get(default="").strip(),
                "location": job.css("span.job-search-card__location::text").get(default="").strip().split(",")[0],
                "date_posted": self.parse_date(job.css("time.job-search-card__listdate::attr(datetime)").get(default="")),
                "source": response.url
            }

            job_url = job.css("a.base-card__full-link::attr(href)").get()
            if job_url:
                detail_url = response.urljoin(job_url)
                yield scrapy.Request(
                    detail_url,
                    callback=self.parse_detail,
                    meta={"job_item": job_item},
                )
                self.request_count += 1

        if num_jobs_returned > 0 and self.request_count < self.max_requests:
            first_job_on_page += 25
            next_url = self.api_url + str(first_job_on_page)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_job,
                meta={"first_job_on_page": first_job_on_page},
            )

    def parse_technologies(self, response: Response) -> str:
        job_description = response.css(JOB_DESCRIPTION).getall()

        text = " ".join(job_description).strip()
        technologies = [tech for tech in TECHNOLOGIES if tech.lower() in text.lower()]

        return ", ".join(technologies)

    def parse_years_of_experience(self, response: Response) -> int | None:
        job_description = response.css(JOB_DESCRIPTION).getall()
        text = " ".join(job_description).strip()

        match = re.search(r"(\d+)\+?\s+years of experience", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def parse_eng_lvl(self, response: Response) -> str:
        job_description = response.css(JOB_DESCRIPTION).getall()
        text = " ".join(job_description).strip()

        ENGLISH_LVLS = {
            "b1": "intermediate",
            "b2": "upper-Intermediate",
            "c1": "advanced"
        }

        for level_v in ENGLISH_LVLS.values():
            if level_v.lower() in text.lower():
                return level_v.capitalize()

        for level_k in ENGLISH_LVLS.keys():
            if level_k.lower() in text.lower():
                return ENGLISH_LVLS[level_k.lower()].capitalize()

        return ""

    def parse_salary(self, response: Response) -> Decimal | None:
        # LinkedIn typically doesn't provide salary information, so we'll return None
        return None

    def parse_seniority_level(self, response: Response) -> str:
        seniority_level = response.css(
            "span.description__job-criteria-text::text"
        ).get(default="").replace("level", "").strip()
        return seniority_level if seniority_level else "Not specified"

    def parse_date(self, date_string: str) -> datetime | None:
        if date_string:
            try:
                return datetime.strptime(date_string.strip(), "%Y-%m-%d")
            except ValueError:
                pass
        return None

    def parse_detail(self, response: Response) -> None:
        job_item = response.meta["job_item"]

        job_item["technologies"] = self.parse_technologies(response)
        job_item["years_of_experience"] = self.parse_years_of_experience(response)
        job_item["english_level"] = self.parse_eng_lvl(response)
        job_item["seniority_level"] = self.parse_seniority_level(response)
        job_item["salary"] = self.parse_salary(response)

        job_listing = JobListing(
            title=job_item["title"],
            company=job_item["company"],
            location=job_item["location"],
            years_of_experience=job_item["years_of_experience"],
            salary=job_item["salary"],
            english_level=job_item["english_level"],
            technologies=job_item["technologies"],
            seniority_level=job_item["seniority_level"],
            date_posted=job_item["date_posted"],
            source=job_item["source"]
        )
        job_listing.save()

        yield job_item