from django.db import models


class JobListing(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    years_of_experience = models.CharField(max_length=50, null=True, blank=True)
    salary = models.CharField(max_length=50, null=True, blank=True)
    english_level = models.CharField(max_length=50, null=True, blank=True)
    technologies = models.CharField(max_length=555)
    seniority_level = models.CharField(max_length=55, null=True, blank=True)
    date_posted = models.CharField(max_length=150, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

    class Meta:
        verbose_name_plural = "Vacancies"
