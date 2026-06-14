from django.db import models
from ckeditor.fields import RichTextField

class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = RichTextField(blank=True)
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    featured_image_alt = models.CharField(max_length=255, blank=True)
    
    # SEO Settings
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ArticleFAQ(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.article.title} FAQ: {self.question[:50]}"
