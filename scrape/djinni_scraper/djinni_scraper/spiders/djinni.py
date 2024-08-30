import re
from typing import Any

import scrapy
from scrapy.http.response import Response
from selenium import webdriver


TECHNOLOGIES = [
        "Django", "Flask", "FastAPI", "RESTful APIs", "Pyramid", "Tornado", "Bottle", "CherryPy",
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra", "Oracle DB",
        "Elasticsearch", "DynamoDB",
        "AWS", "EC2", "S3", "RDS", "Lambda", "Google Cloud Platform", "Microsoft Azure", "Heroku",
        "DigitalOcean",
        "Docker", "Kubernetes", "OpenShift", "Docker Compose", "Helm",
        "Jenkins", "GitLab CI", "Travis CI", "CircleCI", "GitHub Actions", "Bamboo",
        "Git", "Mercurial", "SVN",
        "REST", "GraphQL", "SOAP", "gRPC", "WebSockets",
        "PyTest", "Unittest", "Nose", "Selenium", "Hypothesis", "Robot Framework",
        "Ansible", "Terraform", "Puppet", "Chef",
        "asyncio", "Twisted", "Celery", "aiohttp", "gevent",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "Matplotlib",
        "SciPy", "XGBoost", "LightGBM", "OpenCV",
        "Apache Hadoop", "Apache Spark", "Apache Kafka", "Dask", "Airflow", "Luigi",
        "Matplotlib", "Seaborn", "Plotly", "Bokeh", "Dash",
        "JavaScript", "TypeScript", "React", "Angular", "Vue.js", "HTML", "CSS", "Bootstrap",
        "jQuery",
        "Requests", "urllib", "Scrapy", "Beautiful Soup", "Twisted", "Paramiko",
        "Tkinter", "PyQt", "Kivy", "wxPython", "PyGTK",
        "Make", "CMake", "SCons", "pip", "virtualenv", "Poetry", "Conda",
        "ELK Stack (Elasticsearch, Logstash, Kibana)", "Prometheus", "Grafana", "Sentry",
        "Vagrant", "VirtualBox", "Packer", "AWS CloudFormation",
        "SSL/TLS", "OAuth", "JWT", "bcrypt", "cryptography",
        "Pygame", "Panda3D", "PyOpenGL", "Cocos2d"
    ]


class DjinniSpider(scrapy.Spider):
    name = "djinni"
    allowed_domains = ["djinni.co"]
    start_urls = ["https://djinni.co/jobs/?primary_keyword=Python"]

    def __init__(self, *args, **kwargs) -> None:
        super(DjinniSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Edge()

    def closed(self, *args, **kwargs) -> None:
        self.driver.close()

    def parse(self, response: Response) -> None:
        jobs = response.css('h3 a.job-item__title-link')

        for job in jobs:
            job_url = response.urljoin(job.css('::attr(href)').get())
            yield scrapy.Request(job_url, callback=self.get_all_data)

        next_page = response.css("a.page-link.page-link-next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def get_all_data(self, response: Response) -> dict:
        yield {
            "title": self.parse_title(response=response),
            "company": self.parse_company(response=response),
            "location": self.parse_location(response=response),
            "experience(years)": self.parse_experience(response=response),
            "salary": self.parse_salary(response=response),
            "date_posted": "None",
            "views_popularity": "None",
            "english_level": self.parse_eng_lvl(response=response),
            "technologies": self.parse_technologies(response=response),
            "source": "djinni.co"
        }

    def parse_title(self, response: Response) -> None | str:
        title = response.css("h1::text").get()
        if title:
            return title.strip()
        return "None"

    def parse_company(self, response: Response) -> None | str:
        company = response.css("a.job-details--title::text").get()
        if company:
            return company.strip()
        return "None"

    def parse_location(self, response: Response) -> None | str:
        location = response.css("span.location-text::text").get()
        if location:
            return location.strip()
        return "None"

    def parse_experience(self, response: Response) -> None | int | str:
        experience_elements = response.css('ul.list-unstyled.list-mb-3 li strong.font-weight-600::text').getall()
        for element in experience_elements:
            element = element.strip().lower()
            if "years of experience" in element:
                match = re.search(r'from\s+(\d+)\s+years?\s+of\s+experience', element)
                if match:
                    return int(match.group(1))
            else:
                return "None"
        return None

    def parse_salary(self, response: Response) -> None | int | str:
        salary = response.css("div.text b#salary-suggestion::text").get()
        if salary:
            return salary.replace("$", "").split('-')[0].strip()
        return "None"

    def parse_eng_lvl(self, response: Response) -> None | str:
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
