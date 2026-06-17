"""
URL configuration for brokers_times project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from django.http import HttpResponse
from .sitemaps import (
    StaticViewSitemap, NewsSitemap, ArticleSitemap,
    BrokerSitemap, BestBrokersSitemap,
)


def robots_txt(request):
    content = f"""User-agent: *
Allow: /

Disallow: /admin/
Disallow: /dashboard/
Disallow: /login/
Disallow: /register/
Disallow: /media/
Disallow: /static/

# ── Sitemap Index ──────────────────────────
Sitemap: {settings.SITE_URL}/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')


# ── Sitemap Index (sitemap.xml) ───────────────────────────────
# كل مفتاح هنا يصبح قسم مستقل بـ URL خاص به:
#   /sitemap-static.xml
#   /sitemap-news.xml
#   /sitemap-articles.xml
#   /sitemap-brokers.xml
#   /sitemap-best-brokers.xml

sitemaps = {
    'static':           StaticViewSitemap,
    'news':             NewsSitemap,
    'trading-articles': ArticleSitemap,
    'brokers-reviews':  BrokerSitemap,
    'best-broker':      BestBrokersSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls')),
    path('rosetta/', include('rosetta.urls')),
    path('i18n/', include('django.conf.urls.i18n')),

    # ── SEO ────────────────────────────────────────────────────
    path('robots.txt', robots_txt, name='robots_txt'),

    # Sitemap Index — ملف XML رئيسي يضم روابط الأقسام
    path('sitemap.xml',
         sitemap_index,
         {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemap_section'},
         name='sitemap_index'),

    # Sitemap لكل قسم على حدة  /sitemap-<section>.xml
    path('sitemap-<section>.xml',
         sitemap,
         {'sitemaps': sitemaps},
         name='sitemap_section'),

    path('', include('pages.urls')),
    path('', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
