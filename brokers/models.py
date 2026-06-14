from django.db import models
from categories.models import Regulator, FinancialAsset, DepositLimit, IslamicAccount, Headquarters, TradingPlatform
from ckeditor.fields import RichTextField

class Broker(models.Model):
    # Metadata
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brokers/logos/', blank=True, null=True)
    logo_alt = models.CharField(max_length=255, blank=True)
    account_opening_link = models.URLField(max_length=500, blank=True)

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

    # Review specifications and rating
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    execution_speed = models.IntegerField(default=90)
    customer_support = models.IntegerField(default=90)
    asset_variety = models.IntegerField(default=90)
    
    pros = models.TextField(blank=True, help_text="One advantage per line / ميزة واحدة في كل سطر")
    cons = models.TextField(blank=True, help_text="One disadvantage per line / عيب واحد في كل سطر")
    
    custom_terminal_title = models.CharField(max_length=255, blank=True)
    custom_terminal_description = models.TextField(blank=True)
    custom_terminal_image = models.ImageField(upload_to='brokers/terminals/', blank=True, null=True)
    
    verdict_quote = models.TextField(blank=True)
    verdict_text = models.TextField(blank=True)
    verdict_sentiment = models.CharField(max_length=20, choices=[('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral')], default='neutral')
    local_offices = models.TextField(blank=True, help_text="One office per line / مكتب واحد في كل سطر")

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

class BrokerRegulator(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='broker_regulators')
    regulator = models.ForeignKey(Regulator, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default='AUTHORIZED')

    def __str__(self):
        return f"{self.broker.name} - {self.regulator.name} ({self.license_number})"

class BrokerAccountType(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='account_types')
    name = models.CharField(max_length=100)
    min_deposit = models.CharField(max_length=100)
    spread_from = models.CharField(max_length=100)
    commission = models.CharField(max_length=100)
    leverage = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.broker.name} - {self.name} Account"

class BrokerPlatformTab(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='platform_tabs')
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.broker.name} - {self.title}"

