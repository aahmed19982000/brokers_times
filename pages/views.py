from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from pages.models import HomepageSettings
from articles.models import Article
from brokers.models import Broker

class HomeView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings_obj, created = HomepageSettings.objects.get_or_create(id=1)
        
        featured_brokers = []
        if settings_obj.featured_broker_1:
            featured_brokers.append(settings_obj.featured_broker_1)
        if settings_obj.featured_broker_2:
            featured_brokers.append(settings_obj.featured_broker_2)
        if settings_obj.featured_broker_3:
            featured_brokers.append(settings_obj.featured_broker_3)

        featured_lists = []
        if settings_obj.featured_list_1:
            featured_lists.append(settings_obj.featured_list_1)
        if settings_obj.featured_list_2:
            featured_lists.append(settings_obj.featured_list_2)
        if settings_obj.featured_list_3:
            featured_lists.append(settings_obj.featured_list_3)
        if settings_obj.featured_list_4:
            featured_lists.append(settings_obj.featured_list_4)

        all_articles = Article.objects.filter(status='published').order_by('-created_at')
        featured_article = all_articles.first() if all_articles.exists() else None
        sidebar_articles = all_articles[1:4] if all_articles.count() > 1 else []
        
        from news.models import NewsArticle
        latest_news = NewsArticle.objects.filter(status='published').order_by('-created_at')[:4]

        context.update({
            'homepage_settings': settings_obj,
            'featured_brokers': featured_brokers,
            'featured_lists': featured_lists,
            'featured_article': featured_article,
            'sidebar_articles': sidebar_articles,
            'latest_news': latest_news,
        })
        return context

class BrokerReviewDetailView(DetailView):
    model = Broker
    template_name = 'pages/broker_review_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        broker = self.object
        
        # Split pros and cons by newline
        context['pros_list'] = [p.strip() for p in broker.pros.split('\n') if p.strip()] if broker.pros else []
        context['cons_list'] = [c.strip() for c in broker.cons.split('\n') if c.strip()] if broker.cons else []
        
        # Get related objects
        context['broker_regulators'] = broker.broker_regulators.all()
        context['account_types'] = broker.account_types.all()
        context['platform_tabs'] = broker.platform_tabs.all()
        context['faqs'] = broker.faqs.all()
        
        return context
    context_object_name = 'broker'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        broker = self.get_object()
        
        # Parse pros and cons from translated fields (uses the active language automatically)
        pros_text = broker.pros or ''
        cons_text = broker.cons or ''
        pros_list = [line.strip() for line in pros_text.split('\n') if line.strip()]
        cons_list = [line.strip() for line in cons_text.split('\n') if line.strip()]
        
        # Fetch other brokers for comparison (excluding current)
        compare_brokers = Broker.objects.exclude(id=broker.id)[:3]
        
        context.update({
            'pros_list': pros_list,
            'cons_list': cons_list,
            'compare_brokers': compare_brokers,
            'account_types': broker.account_types.all(),
            'broker_regulators': broker.broker_regulators.all(),
            'trading_platforms': broker.trading_platforms.all(),
        })
        return context

