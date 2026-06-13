from django.db import models
from categories.models import Regulator, FinancialAsset, DepositLimit, IslamicAccount, Headquarters, TradingPlatform
from ckeditor.fields import RichTextField

class Broker(models.Model):
    # Metadata
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)

    # Review Content
    review_content = RichTextField(blank=True)

    # Specifications / Taxonomy Relations
    regulators = models.ManyToManyField(Regulator, related_name='brokers', blank=True)
    financial_assets = models.ManyToManyField(FinancialAsset, related_name='brokers', blank=True)
    deposit_limit = models.ForeignKey(DepositLimit, on_delete=models.SET_NULL, null=True, blank=True, related_name='brokers')
    islamic_account = models.ForeignKey(IslamicAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='brokers')
    headquarters = models.ForeignKey(Headquarters, on_delete=models.SET_NULL, null=True, blank=True, related_name='brokers')
    trading_platforms = models.ManyToManyField(TradingPlatform, related_name='brokers', blank=True)
    
    min_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    withdrawal_time = models.CharField(max_length=100, blank=True)
    base_currencies = models.CharField(max_length=100, blank=True, help_text="e.g. USD, EUR, GBP")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class BrokerFAQ(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.broker.name} FAQ: {self.question[:50]}"
