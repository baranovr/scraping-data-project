from django.db import models


class JobListing(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    years_of_experience = models.CharField(max_length=50, null=True, blank=True)
    salary = models.CharField(max_length=50, null=True, blank=True)
    english_level = models.CharField(max_length=50, null=True, blank=True)
    technologies = models.CharField(max_length=255)
    views_popularity = models.CharField(max_length=555, null=True, blank=True)
    date_posted = models.CharField(max_length=150, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

    class Meta:
        verbose_name_plural = "Vacancies"


class Technology(models.Model):
    name = models.CharField(max_length=255, unique=True)
    vacancy_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class HistoricalData(models.Model):
    date = models.DateField(auto_now_add=True)
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)
    vacancy_count = models.IntegerField()

    def __str__(self):
        return f"{self.technology.name} on {self.date}"

    class Meta:
        verbose_name_plural = "Historical Data"
