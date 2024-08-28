from django.db import models


class Vacancy(models.Model):
    title = models.CharField(max_length=255)  # Название вакансии
    company = models.CharField(max_length=255)  # Название компании
    location = models.CharField(max_length=255)  # Местоположение
    technology = models.CharField(max_length=255)  # Основные технологии, упомянутые в вакансии
    experience = models.CharField(max_length=50, null=True, blank=True)  # Требуемый опыт работы
    description = models.TextField()  # Полное описание вакансии
    salary = models.CharField(max_length=50, null=True, blank=True)
    date_posted = models.DateField()  # Дата публикации вакансии
    views_popularity = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=50)  # Источник (например, 'djinni.co')

    def __str__(self):
        return f"{self.title} at {self.company}"

    class Meta:
        verbose_name_plural = "Vacancies"


class Technology(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Название технологии (например, Python, Django)
    vacancy_count = models.IntegerField(default=0)  # Количество упоминаний в вакансиях

    def __str__(self):
        return self.name


class HistoricalData(models.Model):
    date = models.DateField(auto_now_add=True)  # Дата сохранения данных
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)  # Связь с технологией
    vacancy_count = models.IntegerField()  # Количество упоминаний на эту дату

    def __str__(self):
        return f"{self.technology.name} on {self.date}"

    class Meta:
        verbose_name_plural = "Historical Data"
