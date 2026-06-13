from django.db import models
from brokers.models import Broker
from ckeditor.fields import RichTextField

class BestBrokersList(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    
    # SEO Settings
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    
    featured_image = models.ImageField(upload_to='best_brokers/', blank=True, null=True)
    content = RichTextField(blank=True)
    
    # Metadata / Publishing Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class BestBrokersListItem(models.Model):
    best_brokers_list = models.ForeignKey(BestBrokersList, on_delete=models.CASCADE, related_name='items')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='best_broker_items')
    rank = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['rank']
        unique_together = ('best_brokers_list', 'broker')

    def __str__(self):
        return f"Rank {self.rank}: {self.broker.name} in {self.best_brokers_list.title}"

class BestBrokersListFAQ(models.Model):
    best_brokers_list = models.ForeignKey(BestBrokersList, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.best_brokers_list.title} FAQ: {self.question[:50]}"
