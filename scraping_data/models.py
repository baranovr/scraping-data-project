from django.db import models


class Technology(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class JobListing(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    english_level = models.CharField(max_length=50, null=True, blank=True)
    technologies = models.ManyToManyField(Technology)
    seniority_level = models.CharField(max_length=55, null=True, blank=True)
    date_posted = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

    class Meta:
        verbose_name_plural = "Vacancies"
