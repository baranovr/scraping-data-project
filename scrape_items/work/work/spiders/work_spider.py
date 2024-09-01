import random
import re
from typing import Any

import scrapy
from scrapy.http.response import Response
from scrapy.crawler import CrawlerProcess
from selenium import webdriver

from scraping_data_project.settings import TECHNOLOGIES, USER_AGENT_LIST
from scraping_data.models import JobListing

from multiprocessing import Process


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
        yield {
            "title": self.parse_title(response=response),
            "company": self.parse_company(response=response),
            "location": self.parse_location(response=response),
            "years_of_experience": self.parse_experience(response=response),
            "salary": self.parse_salary(response=response),
            "date_posted": "None",
            "views_popularity": "None",
            "english_level": self.parse_eng_lvl(response=response),
            "technologies": self.parse_technologies(response=response),
            "source": "djinni.co"
        }

    def parse_title(self, response: Response) -> str:
        text = response.css("h1#h1-name::text").getall()
        title = " ".join([t.strip() for t in text])
        return title.strip() if title else "None"

    def parse_company(self, response: Response) -> str:
        company_li = response.css("li")

        for li in company_li:
            if li.css("span.glyphicon-company"):
                company = li.css("span.strong-500::text").get()
                return company.strip() if company and "грн" not in company else "None"

        return "None"

    def parse_location(self, response: Response) -> str:
        location_not_remote = response.css("li:has(span.glyphicon-map-marker)")

        if location_not_remote:
            location = location_not_remote.css("::text").getall()
            location = "".join(location).strip().split(",")[0]
            return location if location else "None"
        else:
            return "Remote"

    def parse_experience(self, response: Response) -> str:
        experience = response.css("li:has(span.glyphicon-tick)")
        if experience:
            experience = experience.css("::text").getall()
            for experience in experience:
                if "рок" in experience:
                    match = re.search(r'\d+', experience)
                    return match.group(0) if match else "None"

        return "None"

    def parse_salary(self, response: Response) -> str:
        salary_li = response.css("li")
        for li in salary_li:
            if li.css("span.glyphicon-hryvnia"):
                salary = response.css("span.strong-500::text").get().replace("&thinsp;", " ")
                match = re.search(r'\d+', salary)
                if match:
                    return match.group(0)
                else:
                    "None"

        return "None"

    def parse_data_posted(self, response: Response) -> str:
        date = response.css("time::attr(datetime)").get()
        if date:
            return date.strip()
        return "None"

    def parse_eng_lvl(self, response: Response) -> str:
        ENGLISH_LVLS = {
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

                for level_v in ENGLISH_LVLS.values():
                    if level_v.lower() in text.lower():
                        return level_v.capitalize()

                for level_k in ENGLISH_LVLS.keys():
                    if level_k.lower() in ENGLISH_LVLS.keys():
                        return ENGLISH_LVLS[level_k.lower()].capitalize()

                return "None"

    def parse_technologies(self, response: Response) -> list[Any]:
        job_description = response.css("#job-description *::text").getall()
        text = " ".join(job_description).strip()

        technologies = []

        for tech in TECHNOLOGIES:
            if tech.lower() in text.lower():
                technologies.append(tech)

        return technologies


def run_spider(spider_class):
    process = CrawlerProcess()
    process.crawl(spider_class)
    process.start()


if __name__ == '__main__':
    p2 = Process(target=run_spider, args=(WorkSpider,))

    p2.start()
    p2.join()
    if p2.is_alive():
        p2.terminate()
        p2.join()
