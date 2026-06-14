from django.views.generic import ListView, DetailView
from .models import NewsArticle

class NewsListView(ListView):
    model = NewsArticle
    template_name = 'pages/news_list.html'
    context_object_name = 'news_articles'
    paginate_by = 12

    def get_queryset(self):
        return NewsArticle.objects.filter(status='published').order_by('-created_at')

class NewsDetailView(DetailView):
    model = NewsArticle
    template_name = 'pages/news_detail.html'
    context_object_name = 'news_article'

    def get_queryset(self):
        return NewsArticle.objects.filter(status='published')
