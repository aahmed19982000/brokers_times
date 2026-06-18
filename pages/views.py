from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView
from django.db.models import Q
from pages.models import HomepageSettings
from articles.models import Article, ArticleFAQ
from brokers.models import Broker
from best_brokers.models import BestBrokersList

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
        latest_news = NewsArticle.objects.filter(status='published').order_by('-created_at')[:5]

        from best_brokers.models import BestBrokersList
        global_list = BestBrokersList.objects.filter(is_global=True).first()
        global_ranked_brokers = []
        if global_list:
            global_ranked_brokers = [item.broker for item in global_list.items.all().order_by('rank')[:5]]

        from categories.models import Regulator, FinancialAsset, TradingPlatform

        # استخدام القوائم المحددة من لوحة التحكم، أو عرض الكل إن لم يُحدد شيء
        if settings_obj.homepage_regulators.exists():
            regulators = settings_obj.homepage_regulators.all()
        else:
            regulators = Regulator.objects.all()

        if settings_obj.homepage_assets.exists():
            assets = settings_obj.homepage_assets.all()
        else:
            assets = FinancialAsset.objects.all()

        if settings_obj.homepage_platforms.exists():
            platforms = settings_obj.homepage_platforms.all()
        else:
            platforms = TradingPlatform.objects.all()

        context.update({
            'homepage_settings': settings_obj,
            'featured_brokers': featured_brokers,
            'featured_lists': featured_lists,
            'featured_article': featured_article,
            'sidebar_articles': sidebar_articles,
            'latest_news': latest_news,
            'global_ranked_brokers': global_ranked_brokers,
            'regulators': regulators,
            'assets': assets,
            'platforms': platforms,
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
        
        # Parse pros, cons, and local offices
        pros_text = broker.pros or ''
        cons_text = broker.cons or ''
        local_offices_text = broker.local_offices or ''
        
        pros_list = [line.strip() for line in pros_text.split('\n') if line.strip()]
        cons_list = [line.strip() for line in cons_text.split('\n') if line.strip()]
        local_offices_list = [line.strip() for line in local_offices_text.split('\n') if line.strip()]
        
        # Fetch other brokers for comparison (excluding current)
        compare_brokers = Broker.objects.exclude(id=broker.id)[:3]
        
        context.update({
            'pros_list': pros_list,
            'cons_list': cons_list,
            'local_offices_list': local_offices_list,
            'compare_brokers': compare_brokers,
            'account_types': broker.account_types.all(),
            'broker_regulators': broker.broker_regulators.all(),
            'trading_platforms': broker.trading_platforms.all(),
        })
        return context


class BrokerDirectoryView(ListView):
    model = Broker
    template_name = 'pages/broker_directory.html'
    context_object_name = 'brokers'
    paginate_by = 12

    def get_queryset(self):
        queryset = Broker.objects.all().order_by('-rating')
        
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(seo_description__icontains=q))

        regulation = self.request.GET.get('regulation', '').strip()
        if regulation:
            queryset = queryset.filter(regulators__slug=regulation)

        instrument = self.request.GET.get('instrument', '').strip()
        if instrument:
            queryset = queryset.filter(financial_assets__slug=instrument)

        min_deposit = self.request.GET.get('min_deposit', '').strip()
        if min_deposit:
            try:
                queryset = queryset.filter(min_deposit__lte=float(min_deposit))
            except ValueError:
                pass

        platform = self.request.GET.get('platform', '').strip()
        if platform:
            queryset = queryset.filter(trading_platforms__slug=platform)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from categories.models import Regulator, FinancialAsset, TradingPlatform
        context['regulators'] = Regulator.objects.all()
        context['instruments'] = FinancialAsset.objects.all()
        context['platforms'] = TradingPlatform.objects.all()
        
        context['q_val'] = self.request.GET.get('q', '').strip()
        context['regulation_val'] = self.request.GET.get('regulation', '').strip()
        context['instrument_val'] = self.request.GET.get('instrument', '').strip()
        context['min_deposit_val'] = self.request.GET.get('min_deposit', '').strip()
        context['platform_val'] = self.request.GET.get('platform', '').strip()
        return context


class ArticleDirectoryView(ListView):
    model = Article
    template_name = 'pages/article_directory.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        # Only show published articles, ordered by created_at descending
        queryset = list(Article.objects.filter(status='published').order_by('-created_at'))
        
        # Attach dynamic fields (category, author, read time) to each article in python
        for art in queryset:
            # 1. Category mapping
            if 'quantitative' in art.slug:
                art.category_slug = 'strategies'
                art.category_name = 'Advanced Strategies'
            elif 'broker' in art.slug:
                art.category_slug = 'basics'
                art.category_name = 'Trading Basics'
            elif 'regulator' in art.slug:
                art.category_slug = 'regulations'
                art.category_name = 'Regulations'
            else:
                art.category_slug = 'analysis'
                art.category_name = 'Market Analysis'
                
            # 2. Author mapping
            if art.category_slug == 'strategies':
                art.author_name = 'David Kross'
                art.author_initials = 'DK'
                art.author_role = 'QUANT SPECIALIST'
            elif art.category_slug == 'basics':
                art.author_name = 'Elena Moretti'
                art.author_initials = 'EM'
                art.author_role = 'SENIOR BEHAVIORAL ANALYST'
            elif art.category_slug == 'regulations':
                art.author_name = 'Sarah Whitmore'
                art.author_initials = 'SW'
                art.author_role = 'LEGAL COMPLIANCE HEAD'
            else:
                art.author_name = 'Julian Sterling'
                art.author_initials = 'JS'
                art.author_role = 'CHIEF MARKET ANALYST'
                
            # 3. Read time mapping
            if art.category_slug == 'strategies':
                art.read_time = '12 min read'
            elif art.category_slug == 'basics':
                art.read_time = '8 min read'
            elif art.category_slug == 'regulations':
                art.read_time = '15 min read'
            else:
                art.read_time = '10 min read'

        # Filter by category if query parameter 'category' is passed
        category_filter = self.request.GET.get('category', '').strip().lower()
        if category_filter and category_filter != 'all':
            queryset = [art for art in queryset if art.category_slug == category_filter]

        # Search filter
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = [art for art in queryset if q.lower() in art.title.lower() or q.lower() in art.content.lower()]
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Trending Articles mockup (from screenshot)
        context['trending_articles'] = [
            {'num': '01', 'category': 'CRYPTO', 'title': "Bitcoin's Halving Aftermath: 6 Months Later"},
            {'num': '02', 'category': 'FOREX', 'title': "Why the Japanese Yen Carry Trade Still Matters"},
            {'num': '03', 'category': 'COMMODITIES', 'title': "Gold vs. Silver: The Diversification Dilemma"}
        ]
        
        # 2. Get featured article
        # The first item in the queryset is treated as the featured article (if any exist)
        object_list = self.get_queryset()
        if object_list:
            context['featured_article'] = object_list[0]
            # Grid articles are the remaining ones
            context['grid_articles'] = object_list[1:]
        else:
            context['featured_article'] = None
            context['grid_articles'] = []
            
        # 3. Current filter values
        context['category_val'] = self.request.GET.get('category', '').strip().lower()
        context['q_val'] = self.request.GET.get('q', '').strip()
        
        return context


class CompareListView(TemplateView):
    template_name = 'pages/compare_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from best_brokers.models import BestBrokersList
        context['compare_lists'] = BestBrokersList.objects.filter(status='published').order_by('-created_at')
        return context


class BestBrokersListDetailView(DetailView):
    model = BestBrokersList
    template_name = 'pages/best_brokers_detail.html'
    context_object_name = 'best_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.object
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'pages/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Article.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faqs'] = self.object.faqs.all()
        context['related_articles'] = Article.objects.filter(status='published').exclude(pk=self.object.pk).order_by('-created_at')[:4]
        return context


class AboutUsView(TemplateView):
    template_name = 'pages/about_us.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'pages/privacy_policy.html'


class TermsOfServiceView(TemplateView):
    template_name = 'pages/terms_of_service.html'


class DisclaimerView(TemplateView):
    template_name = 'pages/disclaimer.html'


class CookiePolicyView(TemplateView):
    template_name = 'pages/cookie_policy.html'




