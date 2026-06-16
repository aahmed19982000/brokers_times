from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomUserProfileForm, DashboardUserCreateForm, DashboardUserUpdateForm
from .models import CustomUser
from brokers.models import Broker, BrokerFAQ, BrokerAccountType, BrokerPlatformTab
from articles.models import Article, ArticleFAQ
from best_brokers.models import BestBrokersList, BestBrokersListItem, BestBrokersListFAQ
from categories.models import Regulator, FinancialAsset, Headquarters, IslamicAccount, DepositLimit, TradingPlatform
from pages.models import HomepageSettings, SiteSettings, HeaderLink, FooterLink, FooterRegulatoryBadge
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views import View
import os
import uuid
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from django.conf import settings
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
def custom_logout_view(request):
    logout(request)
    return redirect('login')
class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')
    def get_object(self, queryset=None):
        return self.request.user
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Collect permissions to display on dashboard
        context['can_publish'] = user.has_perm('users.can_publish') or user.is_superuser
        context['can_edit'] = user.has_perm('users.can_edit') or user.is_superuser
        context['can_manage_brokers'] = user.has_perm('users.can_manage_brokers') or user.is_superuser
        # Add models counts for stats
        context['brokers_count'] = Broker.objects.count()
        context['articles_count'] = Article.objects.count()
        context['best_brokers_count'] = BestBrokersList.objects.count()
        return context
class DashboardBrokersView(LoginRequiredMixin, ListView):
    model = Broker
    template_name = 'dashboard/brokers.html'
    context_object_name = 'brokers'
    ordering = ['-created_at']

    def get_queryset(self):
        from django.db.models import Q
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(slug__icontains=q))
        return queryset
class DashboardArticlesView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'dashboard/articles.html'
    context_object_name = 'articles'
    ordering = ['-created_at']
class DashboardBestBrokersView(LoginRequiredMixin, ListView):
    model = BestBrokersList
    template_name = 'dashboard/best_brokers.html'
    context_object_name = 'lists'
class DashboardBrokerCreateView(LoginRequiredMixin, View):
    def get(self, request):
        regulators = Regulator.objects.all()
        financial_assets = FinancialAsset.objects.all()
        headquarters = Headquarters.objects.all()
        islamic_accounts = IslamicAccount.objects.all()
        trading_platforms = TradingPlatform.objects.all()
        context = {
            'regulators': regulators,
            'financial_assets': financial_assets,
            'headquarters': headquarters,
            'islamic_accounts': islamic_accounts,
            'trading_platforms': trading_platforms,
            'selected_trading_platforms': [],
            'is_edit': False,
            'best_brokers_lists': BestBrokersList.objects.all().order_by('title'),
        }
        return render(request, 'dashboard/broker_form.html', context)
    def post(self, request):
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        account_opening_link = request.POST.get('account_opening_link', '')
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        review_content = request.POST.get('review_content', '')
        min_deposit = request.POST.get('min_deposit') or 0.00
        withdrawal_time = request.POST.get('withdrawal_time', '')
        base_currencies = request.POST.get('base_currencies', '')
        logo_alt = request.POST.get('logo_alt', '')
        hq_id = request.POST.get('headquarters')
        islamic_id = request.POST.get('islamic_account')
        # New detailed review fields
        rating = request.POST.get('rating') or 4.5
        execution_speed = request.POST.get('execution_speed') or 90
        customer_support = request.POST.get('customer_support') or 90
        asset_variety = request.POST.get('asset_variety') or 90
        pros = request.POST.get('pros', '')
        cons = request.POST.get('cons', '')
        custom_terminal_title = request.POST.get('custom_terminal_title', '')
        custom_terminal_description = request.POST.get('custom_terminal_description', '')
        verdict_quote = request.POST.get('verdict_quote', '')
        verdict_text = request.POST.get('verdict_text', '')
        local_offices = request.POST.get('local_offices', '')
        try:
            rating_val = float(rating)
        except (ValueError, TypeError):
            rating_val = 4.5
        if rating_val >= 4.0:
            verdict_sentiment = 'positive'
        elif rating_val >= 3.0:
            verdict_sentiment = 'neutral'
        else:
            verdict_sentiment = 'negative'
        # Auto calculate deposit limit
        try:
            min_dep_val = float(min_deposit)
        except (ValueError, TypeError):
            min_dep_val = 0.0
        if min_dep_val < 100.0:
            limit_slug = 'under-100'
        elif min_dep_val <= 500.0:
            limit_slug = '100-500'
        else:
            limit_slug = 'above-500'
        dep_limit = DepositLimit.objects.filter(slug=limit_slug).first()
        with transaction.atomic():
            broker = Broker.objects.create(
                name = name,
                slug=slug,
                seo_title = seo_title,
                seo_description = seo_description,
                account_opening_link = account_opening_link,
                review_content = review_content,
                min_deposit=min_deposit,
                withdrawal_time = withdrawal_time,
                base_currencies=base_currencies,
                headquarters_id=hq_id if hq_id else None,
                islamic_account_id=islamic_id if islamic_id else None,
                deposit_limit=dep_limit,
                logo=request.FILES.get('logo'),
                logo_alt = logo_alt,
                # New fields mapping
                rating=rating,
                execution_speed=execution_speed,
                customer_support=customer_support,
                asset_variety=asset_variety,
                pros = pros,
                cons = cons,
                custom_terminal_title = custom_terminal_title,
                custom_terminal_description = custom_terminal_description,
                custom_terminal_image=request.FILES.get('custom_terminal_image'),
                verdict_quote = verdict_quote,
                verdict_text = verdict_text,
                verdict_sentiment = verdict_sentiment,
                local_offices = local_offices,
            )
            regulator_ids = request.POST.getlist('regulators')
            if regulator_ids:
                broker.regulators.set(Regulator.objects.filter(id__in=regulator_ids))
            asset_ids = request.POST.getlist('financial_assets')
            if asset_ids:
                broker.financial_assets.set(FinancialAsset.objects.filter(id__in=asset_ids))
            trading_platform_ids = request.POST.getlist('trading_platforms')
            broker.trading_platforms.set(TradingPlatform.objects.filter(id__in=trading_platform_ids))
            # Create FAQs
            faq_questions = request.POST.getlist('faq_question')
            faq_answers = request.POST.getlist('faq_answer')
            for i in range(max(len(faq_questions), len(faq_questions))):
                q = faq_questions[i].strip() if i < len(faq_questions) else ""
                a = faq_answers[i].strip() if i < len(faq_answers) else ""
                if q or q or a or a:
                    BrokerFAQ.objects.create(
                        broker=broker,
                        question = q,
                        answer = a,
                        order=i
                    )

            # Create Platform Tabs
            platform_titles = request.POST.getlist('platform_title')
            platform_subtitles = request.POST.getlist('platform_subtitle')
            for i in range(max(len(platform_titles), len(platform_titles))):
                plat_title = platform_titles[i].strip() if i < len(platform_titles) else ""
                plat_sub = platform_subtitles[i].strip() if i < len(platform_subtitles) else ""
                if plat_title or plat_title:
                    BrokerPlatformTab.objects.create(
                        broker=broker,
                        title = plat_title,
                        subtitle = plat_sub,
                        order=i
                    )
        return redirect('dashboard_brokers')
class DashboardBrokerUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        broker = get_object_or_404(Broker, pk=pk)
        regulators = Regulator.objects.all()
        financial_assets = FinancialAsset.objects.all()
        headquarters = Headquarters.objects.all()
        islamic_accounts = IslamicAccount.objects.all()
        trading_platforms = TradingPlatform.objects.all()
        selected_regulators = list(broker.regulators.values_list('id', flat=True))
        selected_assets = list(broker.financial_assets.values_list('id', flat=True))
        selected_trading_platforms = list(broker.trading_platforms.values_list('id', flat=True))
        context = {
            'broker': broker,
            'regulators': regulators,
            'financial_assets': financial_assets,
            'headquarters': headquarters,
            'islamic_accounts': islamic_accounts,
            'trading_platforms': trading_platforms,
            'selected_regulators': selected_regulators,
            'selected_assets': selected_assets,
            'selected_trading_platforms': selected_trading_platforms,
            'faqs': broker.faqs.all(),
            'account_types': broker.account_types.all(),
            'platform_tabs': broker.platform_tabs.all(),
            'is_edit': True,
            'best_brokers_lists': BestBrokersList.objects.all().order_by('title'),
        }
        return render(request, 'dashboard/broker_form.html', context)
    def post(self, request, pk):
        broker = get_object_or_404(Broker, pk=pk)
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        account_opening_link = request.POST.get('account_opening_link', '')
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        review_content = request.POST.get('review_content', '')
        min_deposit = request.POST.get('min_deposit') or 0.00
        withdrawal_time = request.POST.get('withdrawal_time', '')
        base_currencies = request.POST.get('base_currencies', '')
        logo_alt = request.POST.get('logo_alt', '')
        hq_id = request.POST.get('headquarters')
        islamic_id = request.POST.get('islamic_account')
        # New detailed review fields
        rating = request.POST.get('rating') or 4.5
        execution_speed = request.POST.get('execution_speed') or 90
        customer_support = request.POST.get('customer_support') or 90
        asset_variety = request.POST.get('asset_variety') or 90
        pros = request.POST.get('pros', '')
        cons = request.POST.get('cons', '')
        custom_terminal_title = request.POST.get('custom_terminal_title', '')
        custom_terminal_description = request.POST.get('custom_terminal_description', '')
        verdict_quote = request.POST.get('verdict_quote', '')
        verdict_text = request.POST.get('verdict_text', '')
        local_offices = request.POST.get('local_offices', '')
        try:
            rating_val = float(rating)
        except (ValueError, TypeError):
            rating_val = 4.5
        if rating_val >= 4.0:
            verdict_sentiment = 'positive'
        elif rating_val >= 3.0:
            verdict_sentiment = 'neutral'
        else:
            verdict_sentiment = 'negative'
        # Auto calculate deposit limit
        try:
            min_dep_val = float(min_deposit)
        except (ValueError, TypeError):
            min_dep_val = 0.0
        if min_dep_val < 100.0:
            limit_slug = 'under-100'
        elif min_dep_val <= 500.0:
            limit_slug = '100-500'
        else:
            limit_slug = 'above-500'
        dep_limit = DepositLimit.objects.filter(slug=limit_slug).first()
        with transaction.atomic():
            broker.name = name
            broker.slug = slug
            broker.account_opening_link = account_opening_link
            broker.seo_title = seo_title
            broker.seo_description = seo_description
            broker.review_content = review_content
            broker.min_deposit = min_deposit
            broker.withdrawal_time = withdrawal_time
            broker.base_currencies = base_currencies
            broker.headquarters_id = hq_id if hq_id else None
            broker.islamic_account_id = islamic_id if islamic_id else None
            broker.deposit_limit = dep_limit
            broker.logo_alt = logo_alt
            # Update review detail fields
            broker.rating = rating
            broker.execution_speed = execution_speed
            broker.customer_support = customer_support
            broker.asset_variety = asset_variety
            broker.pros = pros
            broker.cons = cons
            broker.custom_terminal_title = custom_terminal_title
            broker.custom_terminal_description = custom_terminal_description
            broker.verdict_quote = verdict_quote
            broker.verdict_text = verdict_text
            broker.verdict_sentiment = verdict_sentiment
            broker.local_offices = local_offices
            if request.FILES.get('logo'):
                broker.logo = request.FILES.get('logo')
            elif request.POST.get('logo-clear') == 'on':
                broker.logo = None
            if request.FILES.get('custom_terminal_image'):
                broker.custom_terminal_image = request.FILES.get('custom_terminal_image')
            broker.save()
            regulator_ids = request.POST.getlist('regulators')
            broker.regulators.set(Regulator.objects.filter(id__in=regulator_ids))
            asset_ids = request.POST.getlist('financial_assets')
            broker.financial_assets.set(FinancialAsset.objects.filter(id__in=asset_ids))
            trading_platform_ids = request.POST.getlist('trading_platforms')
            broker.trading_platforms.set(TradingPlatform.objects.filter(id__in=trading_platform_ids))
            # Recreate FAQs
            broker.faqs.all().delete()
            faq_questions = request.POST.getlist('faq_question')
            faq_answers = request.POST.getlist('faq_answer')
            for i in range(max(len(faq_questions), len(faq_questions))):
                q = faq_questions[i].strip() if i < len(faq_questions) else ""
                a = faq_answers[i].strip() if i < len(faq_answers) else ""
                if q or q or a or a:
                    BrokerFAQ.objects.create(
                        broker=broker,
                        question = q,
                        answer = a,
                        order=i
                    )

            # Recreate Platform Tabs
            broker.platform_tabs.all().delete()
            platform_titles = request.POST.getlist('platform_title')
            platform_subtitles = request.POST.getlist('platform_subtitle')
            for i in range(max(len(platform_titles), len(platform_titles), 1) if (platform_titles or platform_titles) else 0):
                plat_title = platform_titles[i].strip() if i < len(platform_titles) else ""
                plat_sub = platform_subtitles[i].strip() if i < len(platform_subtitles) else ""
                if plat_title or plat_title:
                    BrokerPlatformTab.objects.create(
                        broker=broker,
                        title = plat_title,
                        subtitle = plat_sub,
                        order=i
                    )
        return redirect('dashboard_brokers')
@method_decorator(csrf_exempt, name='dispatch')
class DashboardImageUploadView(LoginRequiredMixin, View):
    def post(self, request):
        file = request.FILES.get('image')
        if not file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        try:
            filename = f"{uuid.uuid4().hex}.webp"
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            img = Image.open(file)
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img.save(save_path, 'WEBP', quality=85)
            else:
                img = img.convert('RGB')
                img.save(save_path, 'WEBP', quality=85)
            url = settings.MEDIA_URL + 'uploads/' + filename
            return JsonResponse({'url': url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
class DashboardTaxonomyCreateAjaxView(LoginRequiredMixin, View):
    def post(self, request):
        from django.utils.text import slugify
        from django.db.models import Q
        import uuid
        from categories.models import Regulator, Headquarters, IslamicAccount, DepositLimit, TradingPlatform, FinancialAsset
        model_type = request.POST.get('type', '').strip()
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'error': 'Name is required / الاسم مطلوب'}, status=400)
        model_map = {
            'regulator': Regulator,
            'headquarters': Headquarters,
            'islamic_account': IslamicAccount,
            'deposit_limit': DepositLimit,
            'trading_platform': TradingPlatform,
            'financial_asset': FinancialAsset,
        }
        model_class = model_map.get(model_type)
        if not model_class:
            return JsonResponse({'error': 'Invalid taxonomy type'}, status=400)
        # Check if already exists in database (case insensitive)
        instance = model_class.objects.filter(name__iexact=name).first()
        created = False
        if not instance:
            slug = slugify(name)
            if not slug:
                slug = f"{model_type[:3]}-{uuid.uuid4().hex[:8]}"
            base_slug = slug
            counter = 1
            while model_class.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            instance = model_class.objects.create(
                name = name,
                slug=slug
            )
            created = True
        return JsonResponse({
            'id': instance.id,
            'name': instance.name,
            'created': created
        })
class DashboardArticleCreateView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'is_edit': False,
            'best_brokers_lists': BestBrokersList.objects.all().order_by('title'),
        }
        return render(request, 'dashboard/article_form.html', context)
    def post(self, request):
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        content = request.POST.get('content', '')
        featured_image_alt = request.POST.get('featured_image_alt', '')
        with transaction.atomic():
            article = Article.objects.create(
                title = title,
                slug=slug,
                status=status,
                seo_title = seo_title,
                seo_description = seo_description,
                content = content,
                featured_image_alt = featured_image_alt,
            )
            if request.FILES.get('featured_image'):
                article.featured_image = request.FILES.get('featured_image')
                article.save()
            faq_questions = request.POST.getlist('faq_question')
            faq_answers = request.POST.getlist('faq_answer')
            for i in range(max(len(faq_questions), len(faq_questions))):
                q = faq_questions[i].strip() if i < len(faq_questions) else ""
                a = faq_answers[i].strip() if i < len(faq_answers) else ""
                if q or q or a or a:
                    ArticleFAQ.objects.create(
                        article=article,
                        question = q,
                        answer = a,
                        order=i
                    )
        return redirect('dashboard_articles')
class DashboardArticleUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        context = {
            'article': article,
            'faqs': article.faqs.all(),
            'is_edit': True,
            'best_brokers_lists': BestBrokersList.objects.all().order_by('title'),
        }
        return render(request, 'dashboard/article_form.html', context)
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        content = request.POST.get('content', '')
        featured_image_alt = request.POST.get('featured_image_alt', '')
        with transaction.atomic():
            article.title = title
            article.slug = slug
            article.status = status
            article.seo_title = seo_title
            article.seo_description = seo_description
            article.content = content
            article.featured_image_alt = featured_image_alt
            if request.FILES.get('featured_image'):
                article.featured_image = request.FILES.get('featured_image')
            elif request.POST.get('featured_image-clear') == 'on':
                article.featured_image = None
            article.save()
            article.faqs.all().delete()
            faq_questions = request.POST.getlist('faq_question')
            faq_answers = request.POST.getlist('faq_answer')
            for i in range(max(len(faq_questions), len(faq_questions))):
                q = faq_questions[i].strip() if i < len(faq_questions) else ""
                a = faq_answers[i].strip() if i < len(faq_answers) else ""
                if q or q or a or a:
                    ArticleFAQ.objects.create(
                        article=article,
                        question = q,
                        answer = a,
                        order=i
                    )
        return redirect('dashboard_articles')
class DashboardBestBrokersCreateView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'is_edit': False,
            'brokers': Broker.objects.all().order_by('name'),
            'best_brokers_lists': BestBrokersList.objects.all().order_by('title'),
        }
        return render(request, 'dashboard/best_brokers_form.html', context)
    def post(self, request):
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        visibility = request.POST.get('visibility', 'private')
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        content = request.POST.get('content', '')
        featured_image_alt = request.POST.get('featured_image_alt', '')
        country_flag = request.POST.get('country_flag', '')
        with transaction.atomic():
            best_list = BestBrokersList.objects.create(
                title = title,
                slug=slug,
                status=status,
                visibility=visibility,
                seo_title = seo_title,
                seo_description = seo_description,
                content = content,
                featured_image_alt = featured_image_alt,
                country_flag = country_flag,
            )
            if request.FILES.get('featured_image'):
                best_list.featured_image = request.FILES.get('featured_image')
                best_list.save()
            # Save FAQs
            faq_questions = request.POST.getlist('faq_question')
            faq_answers = request.POST.getlist('faq_answer')
            for i in range(max(len(faq_questions), len(faq_questions))):
                q = faq_questions[i].strip() if i < len(faq_questions) else ""
                a = faq_answers[i].strip() if i < len(faq_answers) else ""
                if q or q or a or a:
                    BestBrokersListFAQ.objects.create(
                        best_brokers_list=best_list,
                        question = q,
                        answer = a,
                        order=i
                    )
        return redirect('dashboard_best_brokers')
class DashboardBestBrokersUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        best_list = get_object_or_404(BestBrokersList, pk=pk)
        context = {
            'best_list': best_list,
            'items': best_list.items.all(),
            'faqs': best_list.faqs.all(),
            'is_edit': True,
            'brokers': Broker.objects.all().order_by('name'),
            'best_brokers_lists': BestBrokersList.objects.all().order_by('title'),
        }
        return render(request, 'dashboard/best_brokers_form.html', context)
    def post(self, request, pk):
        best_list = get_object_or_404(BestBrokersList, pk=pk)
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        visibility = request.POST.get('visibility', 'private')
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        content = request.POST.get('content', '')
        featured_image_alt = request.POST.get('featured_image_alt', '')
        country_flag = request.POST.get('country_flag', '')
        with transaction.atomic():
            best_list.title = title
            best_list.slug = slug
            best_list.status = status
            best_list.visibility = visibility
            best_list.seo_title = seo_title
            best_list.seo_description = seo_description
            best_list.content = content
            best_list.featured_image_alt = featured_image_alt
            best_list.country_flag = country_flag
            if request.FILES.get('featured_image'):
                best_list.featured_image = request.FILES.get('featured_image')
            elif request.POST.get('featured_image-clear') == 'on':
                best_list.featured_image = None
            best_list.save()
            # Update FAQs
            best_list.faqs.all().delete()
            faq_questions = request.POST.getlist('faq_question')
            faq_answers = request.POST.getlist('faq_answer')
            for i in range(max(len(faq_questions), len(faq_questions))):
                q = faq_questions[i].strip() if i < len(faq_questions) else ""
                a = faq_answers[i].strip() if i < len(faq_answers) else ""
                if q or q or a or a:
                    BestBrokersListFAQ.objects.create(
                        best_brokers_list=best_list,
                        question = q,
                        answer = a,
                        order=i
                    )
        return redirect('dashboard_best_brokers')
class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if not (request.user.role == 'admin' or request.user.is_superuser):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to access user management.")
        return super().dispatch(request, *args, **kwargs)
class DashboardUsersView(AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'dashboard/users.html'
    context_object_name = 'users'
    def get_queryset(self):
        return CustomUser.objects.all().order_by('username')
class DashboardUserCreateView(AdminRequiredMixin, CreateView):
    model = CustomUser
    form_class = DashboardUserCreateForm
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('dashboard_users')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context
class DashboardUserUpdateView(AdminRequiredMixin, UpdateView):
    model = CustomUser
    form_class = DashboardUserUpdateForm
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('dashboard_users')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context
class DashboardHomepageSettingsView(AdminRequiredMixin, View):
    def get(self, request):
        settings_obj, created = HomepageSettings.objects.get_or_create(id=1)
        brokers = Broker.objects.all().order_by('name')
        lists = BestBrokersList.objects.filter(status='published').order_by('title')
        if not lists.exists():
            lists = BestBrokersList.objects.all().order_by('title')
        context = {
            'settings': settings_obj,
            'brokers': brokers,
            'lists': lists,
        }
        return render(request, 'dashboard/homepage_settings.html', context)
    def post(self, request):
        settings_obj, created = HomepageSettings.objects.get_or_create(id=1)
        hero_id = request.POST.get('hero_featured_broker')
        b1_id = request.POST.get('featured_broker_1')
        b2_id = request.POST.get('featured_broker_2')
        b3_id = request.POST.get('featured_broker_3')
        l1_id = request.POST.get('featured_list_1')
        l2_id = request.POST.get('featured_list_2')
        l3_id = request.POST.get('featured_list_3')
        l4_id = request.POST.get('featured_list_4')
        def get_or_none(model, pk):
            if pk:
                try:
                    return model.objects.get(pk=pk)
                except model.DoesNotExist:
                    pass
            return None
        settings_obj.hero_featured_broker = get_or_none(Broker, hero_id)
        settings_obj.featured_broker_1 = get_or_none(Broker, b1_id)
        settings_obj.featured_broker_2 = get_or_none(Broker, b2_id)
        settings_obj.featured_broker_3 = get_or_none(Broker, b3_id)
        settings_obj.featured_list_1 = get_or_none(BestBrokersList, l1_id)
        settings_obj.featured_list_2 = get_or_none(BestBrokersList, l2_id)
        settings_obj.featured_list_3 = get_or_none(BestBrokersList, l3_id)
        settings_obj.featured_list_4 = get_or_none(BestBrokersList, l4_id)
        settings_obj.save()
        from django.contrib import messages
        messages.success(request, "Homepage configuration saved successfully! / تم حفظ إعدادات الصفحة الرئيسية بنجاح!")
        return redirect('dashboard_homepage_settings')


class DashboardSiteSettingsView(AdminRequiredMixin, View):
    def get(self, request):
        settings_obj, created = SiteSettings.objects.get_or_create(id=1)
        header_links = HeaderLink.objects.all().order_by('order')
        footer_links = FooterLink.objects.all().order_by('order')
        regulatory_badges = FooterRegulatoryBadge.objects.all().order_by('order')
        
        # Load all best brokers list pages for selection
        from best_brokers.models import BestBrokersList
        all_lists = BestBrokersList.objects.all().order_by('title')
        
        # Load all brokers for direct dropdown selection
        from brokers.models import Broker
        all_brokers = Broker.objects.all().order_by('name')
        
        context = {
            'settings': settings_obj,
            'header_links': header_links,
            'footer_links': footer_links,
            'regulatory_badges': regulatory_badges,
            'all_lists': all_lists,
            'all_brokers': all_brokers,
        }
        return render(request, 'dashboard/site_settings.html', context)
        
    def post(self, request):
        settings_obj, created = SiteSettings.objects.get_or_create(id=1)
        
        # Save SiteSettings general fields
        settings_obj.header_brand_name = request.POST.get('header_brand_name', 'Brokers Times')
        
        # Handle Logo file upload
        if request.FILES.get('header_logo'):
            settings_obj.header_logo = request.FILES.get('header_logo')
        elif request.POST.get('clear_logo') == 'true':
            settings_obj.header_logo = None
            
        settings_obj.footer_about_en = request.POST.get('footer_about_en', '')
        settings_obj.footer_risk_warning_en = request.POST.get('footer_risk_warning_en', '')
        settings_obj.footer_col2_title_en = request.POST.get('footer_col2_title_en', '')
        settings_obj.footer_col3_title_en = request.POST.get('footer_col3_title_en', '')
        settings_obj.footer_contact_text_en = request.POST.get('footer_contact_text_en', '')
        settings_obj.contact_email = request.POST.get('contact_email', '')
        settings_obj.social_share_url = request.POST.get('social_share_url', '')
        settings_obj.copyright_text_en = request.POST.get('copyright_text_en', '')
        settings_obj.save()
        
        # Save ManyToMany relations for compare & top 10 dropdowns
        top_10_broker_ids = request.POST.getlist('top_10_dropdown_brokers')
        settings_obj.top_10_dropdown_brokers.set(top_10_broker_ids)
        
        compare_ids = request.POST.getlist('compare_dropdown_lists')
        settings_obj.compare_dropdown_lists.set(compare_ids)
        
        # Save Header Links (from repeater list input arrays)
        HeaderLink.objects.all().delete()
        header_titles_en = request.POST.getlist('header_title_en')
        header_urls = request.POST.getlist('header_url')
        header_orders = request.POST.getlist('header_order')
        for i in range(len(header_titles_en)):
            if header_titles_en[i]:
                try:
                    ord_val = int(header_orders[i])
                except (ValueError, IndexError):
                    ord_val = i + 1
                HeaderLink.objects.create(
                    title_en=header_titles_en[i],
                    title_ar=header_titles_en[i],  # Map to EN for backward compatibility
                    url_or_route=header_urls[i],
                    order=ord_val
                )
                
        # Save Footer Links (from repeater list input arrays)
        FooterLink.objects.all().delete()
        footer_titles_en = request.POST.getlist('footer_title_en')
        footer_urls = request.POST.getlist('footer_url')
        footer_columns = request.POST.getlist('footer_column')
        footer_orders = request.POST.getlist('footer_order')
        for i in range(len(footer_titles_en)):
            if footer_titles_en[i]:
                try:
                    ord_val = int(footer_orders[i])
                except (ValueError, IndexError):
                    ord_val = i + 1
                col_val = footer_columns[i] if i < len(footer_columns) else 'col2'
                FooterLink.objects.create(
                    title_en=footer_titles_en[i],
                    title_ar=footer_titles_en[i],  # Map to EN for backward compatibility
                    url_or_route=footer_urls[i],
                    column=col_val,
                    order=ord_val
                )
                
        # Save Footer Regulatory Badges
        FooterRegulatoryBadge.objects.all().delete()
        badge_texts_en = request.POST.getlist('badge_text_en')
        badge_orders = request.POST.getlist('badge_order')
        for i in range(len(badge_texts_en)):
            if badge_texts_en[i]:
                try:
                    ord_val = int(badge_orders[i])
                except (ValueError, IndexError):
                    ord_val = i + 1
                FooterRegulatoryBadge.objects.create(
                    text_en=badge_texts_en[i],
                    text_ar=badge_texts_en[i],  # Map to EN for backward compatibility
                    order=ord_val
                )
                
        from django.contrib import messages
        messages.success(request, "Site settings saved successfully! / تم حفظ الإعدادات بنجاح!")
        return redirect('dashboard_site_settings')

from news.models import NewsArticle
class DashboardNewsView(LoginRequiredMixin, ListView):
    model = NewsArticle
    template_name = 'dashboard/news.html'
    context_object_name = 'news_articles'
class DashboardNewsCreateView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'is_edit': False,
            'best_brokers_lists': BestBrokersList.objects.all().order_by('title'),
        }
        return render(request, 'dashboard/news_form.html', context)
    def post(self, request):
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        content = request.POST.get('content', '')
        featured_image_alt = request.POST.get('featured_image_alt', '')
        with transaction.atomic():
            news_article = NewsArticle.objects.create(
                title=title,
                slug=slug,
                status=status,
                seo_title=seo_title,
                seo_description=seo_description,
                content=content,
                featured_image_alt=featured_image_alt,
            )
            if request.FILES.get('featured_image'):
                news_article.featured_image = request.FILES.get('featured_image')
                news_article.save()
        return redirect('dashboard_news')
class DashboardNewsUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        news_article = get_object_or_404(NewsArticle, pk=pk)
        context = {
            'news_article': news_article,
            'is_edit': True,
            'best_brokers_lists': BestBrokersList.objects.all().order_by('title'),
        }
        return render(request, 'dashboard/news_form.html', context)
    def post(self, request, pk):
        news_article = get_object_or_404(NewsArticle, pk=pk)
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        content = request.POST.get('content', '')
        featured_image_alt = request.POST.get('featured_image_alt', '')
        with transaction.atomic():
            news_article.title = title
            news_article.slug = slug
            news_article.status = status
            news_article.seo_title = seo_title
            news_article.seo_description = seo_description
            news_article.content = content
            news_article.featured_image_alt = featured_image_alt
            if request.FILES.get('featured_image'):
                news_article.featured_image = request.FILES.get('featured_image')
            elif request.POST.get('featured_image-clear') == 'on':
                news_article.featured_image = None
            news_article.save()
        return redirect('dashboard_news')

# ---------------------------------------------------------
# CATEGORIES MANAGEMENT
# ---------------------------------------------------------
from categories.models import Category, Regulator, FinancialAsset, TradingPlatform, Headquarters, DepositLimit, IslamicAccount

def get_category_model(model_name):
    models_map = {
        'category': Category,
        'regulator': Regulator,
        'financial_asset': FinancialAsset,
        'trading_platform': TradingPlatform,
        'headquarters': Headquarters,
        'deposit_limit': DepositLimit,
        'islamic_account': IslamicAccount
    }
    return models_map.get(model_name, Category)

class DashboardCategoriesView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/categories.html'
    def test_func(self):
        return self.request.user.is_superuser
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.request.GET.get('type', 'category')
        Model = get_category_model(model_name)
        context['items'] = Model.objects.all().order_by('-id')
        context['current_type'] = model_name
        return context

class DashboardCategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/category_form.html'
    def test_func(self):
        return self.request.user.is_superuser
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.request.GET.get('type', 'category')
        context['current_type'] = model_name
        context['has_icon'] = model_name in ['regulator', 'financial_asset', 'trading_platform']
        return context
    def post(self, request, *args, **kwargs):
        model_name = request.POST.get('type', 'category')
        Model = get_category_model(model_name)
        name = request.POST.get('name')
        from django.utils.text import slugify
        slug = slugify(name)
        icon = request.FILES.get('icon')
        if hasattr(Model, 'icon') and icon:
            Model.objects.create(name=name, slug=slug, icon=icon)
        else:
            Model.objects.create(name=name, slug=slug)
        return redirect(f'/dashboard/categories/?type={model_name}')

class DashboardCategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/category_form.html'
    def test_func(self):
        return self.request.user.is_superuser
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.request.GET.get('type', 'category')
        Model = get_category_model(model_name)
        context['item'] = get_object_or_404(Model, pk=self.kwargs['pk'])
        context['current_type'] = model_name
        context['has_icon'] = model_name in ['regulator', 'financial_asset', 'trading_platform']
        return context
    def post(self, request, *args, **kwargs):
        model_name = request.POST.get('type', 'category')
        Model = get_category_model(model_name)
        item = get_object_or_404(Model, pk=self.kwargs['pk'])
        item.name = request.POST.get('name')
        if hasattr(item, 'icon') and request.FILES.get('icon'):
            item.icon = request.FILES.get('icon')
        item.save()
        return redirect(f'/dashboard/categories/?type={model_name}')


class DashboardRankedBrokersView(LoginRequiredMixin, View):
    def get(self, request):
        lists = BestBrokersList.objects.all().order_by('title')

        list_id = request.GET.get('list_id')
        selected_list = None
        if list_id:
            selected_list = get_object_or_404(BestBrokersList, pk=list_id)
        elif lists.exists():
            selected_list = lists.first()

        items = selected_list.items.all().order_by('rank') if selected_list else []
        brokers = Broker.objects.all().order_by('name')
        global_list = BestBrokersList.objects.filter(is_global=True).first()

        context = {
            'lists': lists,
            'selected_list': selected_list,
            'items': items,
            'brokers': brokers,
            'global_list': global_list,
        }
        return render(request, 'dashboard/ranked_brokers.html', context)

    def post(self, request):
        action = request.POST.get('action', 'save_ranks')

        # ── تعيين قائمة كعالمية [brokers_list] ──
        if action == 'toggle_global':
            list_id = request.POST.get('list_id')
            selected_list = get_object_or_404(BestBrokersList, pk=list_id)
            # إلغاء التفعيل عن أي قائمة سابقة وتفعيل المحددة
            BestBrokersList.objects.filter(is_global=True).update(is_global=False)
            selected_list.is_global = True
            selected_list.save(update_fields=['is_global'])
            return redirect(f'/dashboard/ranked-brokers/?list_id={selected_list.id}')

        # ── الحفظ الاعتيادي للترتيب ──
        list_id = request.POST.get('list_id')
        selected_list = get_object_or_404(BestBrokersList, pk=list_id)

        with transaction.atomic():
            # Delete old rankings for this list
            selected_list.items.all().delete()

            # Save new ranked items
            broker_ids = request.POST.getlist('item_broker')
            ranks = request.POST.getlist('item_rank')
            headlines = request.POST.getlist('item_headline')
            descriptions = request.POST.getlist('item_description')
            highlights = request.POST.getlist('item_highlights')
            custom_deposits = request.POST.getlist('item_custom_deposit')

            for i in range(len(broker_ids)):
                b_id = broker_ids[i]
                if not b_id:
                    continue
                rk = ranks[i] if i < len(ranks) else (i + 1)
                hl = headlines[i].strip() if i < len(headlines) else ""
                d = descriptions[i].strip() if i < len(descriptions) else ""
                hi = highlights[i].strip() if i < len(highlights) else ""
                cd = custom_deposits[i].strip() if i < len(custom_deposits) else ""
                BestBrokersListItem.objects.create(
                    best_brokers_list=selected_list,
                    broker_id=b_id,
                    rank=rk,
                    headline=hl,
                    description=d,
                    highlights=hi,
                    custom_deposit=cd,
                )

        return redirect(f'/dashboard/ranked-brokers/?list_id={selected_list.id}')


from django.http import JsonResponse

class APIBestBrokersLookupView(LoginRequiredMixin, View):
    def get(self, request):
        list_id = request.GET.get('id')
        slug = request.GET.get('slug')
        
        if list_id:
            try:
                best_list = BestBrokersList.objects.get(pk=int(list_id))
            except (ValueError, BestBrokersList.DoesNotExist):
                return JsonResponse({'error': 'List not found'}, status=404)
        elif slug:
            try:
                best_list = BestBrokersList.objects.get(slug=slug)
            except BestBrokersList.DoesNotExist:
                return JsonResponse({'error': 'List not found'}, status=404)
        else:
            return JsonResponse({'error': 'Missing id or slug parameter'}, status=400)
            
        items = best_list.items.all().order_by('rank')
        brokers_data = []
        for item in items:
            brokers_data.append({
                'id': item.broker.id,
                'name': item.broker.name
            })
            
        return JsonResponse({
            'id': best_list.id,
            'title': best_list.title,
            'slug': best_list.slug,
            'brokers': brokers_data
        })


import requests
import re
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from decouple import config

TRADING_GLOSSARY = {
    r'\bfinancial lever\b': 'leverage',
    r'\bleverage lever\b': 'leverage',
    r'\bmultiplier lever\b': 'leverage',
    r'\bleverage multiplier\b': 'leverage',
    r'\bprice differences\b': 'spreads',
    r'\bmargins differences\b': 'spreads',
    r'\bprice spreads\b': 'spreads',
    r'\bIslamic account\b': 'Islamic/swap-free account',
    r'\bMuslim account\b': 'Islamic/swap-free account',
    r'\bdeal platforms\b': 'trading platforms',
    r'\bdeals platforms\b': 'trading platforms',
    r'\blowest deposit\b': 'minimum deposit',
    r'\bleast deposit\b': 'minimum deposit',
    r'\bpull and deposit\b': 'deposit and withdrawal methods',
    r'\bdraw and download\b': 'withdrawal and deposit',
    r'\bwithdrawal and download\b': 'withdrawal and deposit',
    r'\bpull and download\b': 'withdrawal and deposit',
    r'\blicensed company\b': 'regulated broker',
    r'\bcertified broker\b': 'regulated broker',
    r'\bforex sales\b': 'forex brokers',
    r'\bcurrency sellers\b': 'forex brokers',
    r'\bcurrency seller\b': 'forex broker',
    r'\bcurrency trading companies\b': 'forex brokers',
}

@method_decorator(csrf_exempt, name='dispatch')
def _translate_text_only(raw_text, headers):
    """Translate plain text via Google Translate, with MyMemory fallback."""
    gt_url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl=en&dt=t"
    try:
        response = requests.post(gt_url, data={'q': raw_text}, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            result = ""
            if data and data[0]:
                for segment in data[0]:
                    if segment and segment[0]:
                        result += segment[0]
            if result and result.strip() != raw_text.strip():
                return result
    except Exception:
        pass

    # Fallback: MyMemory free API (no rate limit for small texts)
    try:
        mm_url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(raw_text[:500])}&langpair=ar|en"
        mm_resp = requests.get(mm_url, timeout=10)
        if mm_resp.status_code == 200:
            mm_data = mm_resp.json()
            result = mm_data.get('responseData', {}).get('translatedText', '')
            if result and result.strip() != raw_text.strip():
                return result
    except Exception:
        pass

    return None


def _translate_html_preserving_structure(html, headers):
    """
    Split HTML into tag/text chunks, translate only text chunks,
    then reassemble — so h2/h3/strong/etc. are never touched.
    """
    parts = re.split(r'(<[^>]+>)', html)
    translated_parts = []
    for part in parts:
        if part.startswith('<') or not part.strip():
            translated_parts.append(part)
        else:
            translated = _translate_text_only(part, headers)
            if translated:
                # Apply glossary corrections
                for pattern, replacement in TRADING_GLOSSARY.items():
                    translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
                translated_parts.append(translated)
            else:
                translated_parts.append(part)
    return "".join(translated_parts)


class DashboardTranslateView(LoginRequiredMixin, View):
    def post(self, request):
        import json
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
                text = body.get('text', '').strip()
                tone = body.get('tone', 'financial').strip()
            else:
                text = request.POST.get('text', '').strip()
                tone = request.POST.get('tone', 'financial').strip()
        except Exception as e:
            return JsonResponse({'error': 'Invalid request: ' + str(e)}, status=400)

        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)

        gemini_api_key = config('GEMINI_API_KEY', default=None)
        if not gemini_api_key:
            gemini_api_key = os.environ.get('GEMINI_API_KEY')

        translated_text = ""
        method = ""
        ai_active = False

        if gemini_api_key:
            try:
                model_name = "gemini-2.5-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
                
                prompt = (
                    f"You are a professional financial translator specializing in translating online broker reviews, "
                    f"trading news, analysis, and educational trading FAQs from Arabic to English. "
                    f"Translate the following Arabic text into professional, natural, and context-accurate English. "
                    f"Tone/Style target: {tone} (formal financial and trading reviews).\n\n"
                    f"CRITICAL RULES:\n"
                    f"1. Do NOT translate financial and trading terminology literally (e.g. translate 'رافعة مالية' to 'leverage', "
                    f"'فروق الأسعار' or 'اسبريد' to 'spreads', 'حساب إسلامي' to 'Islamic/swap-free account', 'منصات التداول' to 'trading platforms', "
                    f"'تراخيص' or 'شركات مرخصة' to 'regulations' / 'regulated brokers', 'الحد الأدنى للإيداع' to 'minimum deposit', "
                    f"'طرق السحب والإيداع' to 'funding methods' or 'deposit and withdrawal methods').\n"
                    f"2. Keep any HTML tags (e.g., <p>, <strong>, <a>, <img>, <br>, <ul>, <li>, etc.) or markdown formatting exactly as they are in the source text. Do not modify, reorder, or lose any tags or their attributes (like img src, a href, class names). Place the translated text inside/between them correctly.\n"
                    f"3. Do not add any conversational remarks, introductions, markdown code blocks, or notes. Output ONLY the translated text.\n\n"
                    f"Source Text:\n{text}"
                )

                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                response = requests.post(url, json=payload, timeout=20)
                if response.status_code == 200:
                    res_json = response.json()
                    candidate = res_json.get('candidates', [{}])[0]
                    part = candidate.get('content', {}).get('parts', [{}])[0]
                    translated_text = part.get('text', '').strip()
                    if translated_text:
                        # Clean up markdown code blocks if LLM added them
                        if translated_text.startswith("```"):
                            lines = translated_text.splitlines()
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines and lines[-1].startswith("```"):
                                lines = lines[:-1]
                            translated_text = "\n".join(lines).strip()
                        ai_active = True
                        method = "Gemini AI"
                else:
                    print(f"Gemini API returned status {response.status_code}: {response.text}")
            except Exception as ex:
                print(f"Gemini API translation error: {ex}")

        # Fallback Mode: Google Translate with structure-preserving approach
        if not translated_text:
            try:
                gt_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
                translated_text = _translate_html_preserving_structure(text, gt_headers)
                if translated_text:
                    method = "Glossary-Enhanced Neural Engine"
                    ai_active = False
            except Exception as ex:
                print(f"Fallback translation error: {ex}")

        if not translated_text:
            return JsonResponse({'error': 'Translation service unavailable'}, status=503)

        # Detect rate-limit: if returned text is identical to input, translation didn't happen
        import unicodedata
        def _strip(s):
            return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()
        if _strip(translated_text) == _strip(text):
            return JsonResponse({'error': 'خدمة الترجمة مشغولة حالياً (rate limit)، انتظر ثوانٍ وحاول مجدداً.'}, status=503)

        return JsonResponse({
            'translated_text': translated_text,
            'ai_active': ai_active,
            'method': method
        })
