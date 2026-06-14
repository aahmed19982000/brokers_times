import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brokers_times.settings')
django.setup()

from news.models import NewsArticle
print(f"Total News: {NewsArticle.objects.count()}")
print(f"Published News: {NewsArticle.objects.filter(status='published').count()}")
