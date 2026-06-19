from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Regulator(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.FileField(upload_to='category_icons/', blank=True, null=True)

    def __str__(self):
        return self.name

class FinancialAsset(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.FileField(upload_to='category_icons/', blank=True, null=True)

    def __str__(self):
        return self.name

class DepositLimit(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name

class IslamicAccount(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name

class Headquarters(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    country_code = models.CharField(max_length=2, blank=True, help_text="ISO 2-letter country code (e.g. gb, us, cy)")

    class Meta:
        verbose_name_plural = "Headquarters"

    def __str__(self):
        return self.name

class TradingPlatform(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.FileField(upload_to='category_icons/', blank=True, null=True)

    def __str__(self):
        return self.name
