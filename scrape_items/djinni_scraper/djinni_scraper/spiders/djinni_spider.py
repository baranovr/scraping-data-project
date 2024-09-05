import os
import re
import random
from typing import Any

import django
import scrapy
from scrapy.http.response import Response
from selenium import webdriver

from scraping_data_project.settings import USER_AGENT_LIST, TECHNOLOGIES, SENIORITY_LEVELS

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from scraping_data.models import JobListing


class DjinniSpider(scrapy.Spider):
    name = "djinni"
    allowed_domains = ["djinni.co"]
    start_urls = ["https://djinni.co/jobs/?primary_keyword=Python"]

    def __init__(self, *args, **kwargs) -> None:
        super(DjinniSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Edge()

    def closed(self, *args, **kwargs) -> None:
        self.driver.close()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers={"User-Agent": random.choice(USER_AGENT_LIST)}, callback=self.parse)

    def parse(self, response: Response) -> None:
        jobs = response.css('h3 a.job-item__title-link')

        for job in jobs:
            job_url = response.urljoin(job.css('::attr(href)').get())
            yield scrapy.Request(job_url, callback=self.get_all_data)

        next_page = response.css("a.page-link.page-link-next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def get_all_data(self, response: Response) -> dict:
        data = {
            "title": self.parse_title(response=response),
            "company": self.parse_company(response=response),
            "location": self.parse_location(response=response),
            "experience(years)": self.parse_experience(response=response),
            "salary": self.parse_salary(response=response),
            "date_posted": "None",
            "seniority_level": self.parse_seniority_level(response=response),
            "english_level": self.parse_eng_lvl(response=response),
            "technologies": self.parse_technologies(response=response),
            "source": "djinni.co"
        }
        job_listing = JobListing(
            title=data.get("title", ""),
            company=data.get("company", ""),
            location=data.get("location", ""),
            technologies=data.get("technologies", ""),
            years_of_experience=data.get("years_of_experience", ""),
            english_level=data.get("english_level", ""),
            seniority_level=data.get("seniority_level", ""),
            date_posted=data.get("date_posted", ""),
            source=data.get("source", "")
        )
        job_listing.save()
        yield data

    def parse_title(self, response: Response) -> str:
        title = response.css("h1::text").get()
        if title:
            return title.strip()
        return "None"

    def parse_company(self, response: Response) -> str:
        company = response.css("a.job-details--title::text").get()
        if company:
            return company.strip()
        return "None"

    def parse_location(self, response: Response) -> str:
        location = response.css("span.location-text::text").get()
        if location:
            return location.strip()
        return "None"

    def parse_experience(self, response: Response) -> None | str:
        experience_elements = response.css('ul.list-unstyled.list-mb-3 li strong.font-weight-600::text').getall()
        for element in experience_elements:
            element = element.strip().lower()
            if "years of experience" in element:
                match = re.search(r'from\s+(\d+)\s+years?\s+of\s+experience', element)
                if match:
                    return match.group(1)
            else:
                return "None"
        return None

    def parse_salary(self, response: Response) -> str:
        salary = response.css("div.text b#salary-suggestion::text").get()
        if salary:
            return salary.replace("$", "").split('-')[0].strip()
        return "None"

    def parse_seniority_level(self, response: Response) -> str:
        paragraphs = response.css('div.job-post-description p::text').getall()
        strong_texts = response.css('div.job-post-description strong::text').getall()
        all_text = ' '.join(paragraphs + strong_texts).lower()

        for level in SENIORITY_LEVELS:
            if level in all_text:
                return level.capitalize()

        return "None"

    def parse_eng_lvl(self, response: Response) -> str:
        eng_lvl = response.css('ul.list-unstyled.list-mb-3 li strong.font-weight-600::text').get()
        if "mediate" in eng_lvl or "vance" in eng_lvl:
            return eng_lvl.replace("Only\n      from\n      ", "").replace("from\n      ", "").strip()
        return "None"

    def parse_technologies(self, response: Response) -> list[str | Any]:
        paragraphs = response.css('div.job-post-description p::text').getall()
        strong_texts = response.css('div.job-post-description strong::text').getall()
        all_text = ' '.join(paragraphs + strong_texts)

        found_technologies = []

        if all_text:
            for tech in TECHNOLOGIES:
                if re.search(r'\b' + re.escape(tech.lower()) + r'\b', all_text.lower(), re.IGNORECASE):
                    found_technologies.append(tech)

        return found_technologies
