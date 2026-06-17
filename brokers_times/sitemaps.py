from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from news.models import NewsArticle
from articles.models import Article
from brokers.models import Broker
from best_brokers.models import BestBrokersList


class StaticViewSitemap(Sitemap):
    """الصفحات الثابتة: الرئيسية، الأخبار، المقالات، الوسطاء..."""
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'news_list',
            'article_directory',
            'broker_directory',
            'compare_list',
            'about_us',
            'privacy_policy',
            'terms_of_service',
            'disclaimer',
            'cookie_policy',
        ]

    def location(self, item):
        return reverse(item)


class NewsSitemap(Sitemap):
    """أخبار الأسواق المالية"""
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return NewsArticle.objects.filter(status='published').order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('news_detail', kwargs={'slug': obj.slug})


class ArticleSitemap(Sitemap):
    """مقالات التداول التعليمية"""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Article.objects.filter(status='published').order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('article_detail', kwargs={'slug': obj.slug})


class BrokerSitemap(Sitemap):
    """مراجعات شركات التداول"""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Broker.objects.all().order_by('name')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('broker_review_detail', kwargs={'slug': obj.slug})


class BestBrokersSitemap(Sitemap):
    """قوائم أفضل وسيط"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return BestBrokersList.objects.filter(
            status='published', visibility='public'
        ).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('best_brokers_list_detail', kwargs={'slug': obj.slug})
