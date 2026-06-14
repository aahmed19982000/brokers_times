from django.db import models
from ckeditor.fields import RichTextField
from brokers.models import Broker

class NewsArticle(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = RichTextField(blank=True)
    
    featured_image = models.ImageField(upload_to='news/', blank=True, null=True)
    featured_image_alt = models.CharField(max_length=255, blank=True)
    
    # SEO Settings
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
