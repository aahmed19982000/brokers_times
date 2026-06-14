from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomUserProfileForm, DashboardUserCreateForm, DashboardUserUpdateForm
from .models import CustomUser

from brokers.models import Broker, BrokerFAQ, BrokerAccountType, BrokerPlatformTab
from articles.models import Article, ArticleFAQ
from best_brokers.models import BestBrokersList, BestBrokersListItem, BestBrokersListFAQ
from categories.models import Regulator, FinancialAsset, Headquarters, IslamicAccount, DepositLimit, TradingPlatform
from pages.models import HomepageSettings
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

class DashboardArticlesView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'dashboard/articles.html'
    context_object_name = 'articles'

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
        }
        return render(request, 'dashboard/broker_form.html', context)

    def post(self, request):
        name_en = request.POST.get('name_en')
        name_ar = request.POST.get('name_ar')
        slug = request.POST.get('slug')
        seo_title_en = request.POST.get('seo_title_en', '')
        seo_title_ar = request.POST.get('seo_title_ar', '')
        seo_description_en = request.POST.get('seo_description_en', '')
        seo_description_ar = request.POST.get('seo_description_ar', '')
        review_content_en = request.POST.get('review_content_en', '')
        review_content_ar = request.POST.get('review_content_ar', '')
        min_deposit = request.POST.get('min_deposit') or 0.00
        withdrawal_time_en = request.POST.get('withdrawal_time_en', '')
        withdrawal_time_ar = request.POST.get('withdrawal_time_ar', '')
        base_currencies = request.POST.get('base_currencies', '')
        logo_alt_en = request.POST.get('logo_alt_en', '')
        logo_alt_ar = request.POST.get('logo_alt_ar', '')
        
        hq_id = request.POST.get('headquarters')
        islamic_id = request.POST.get('islamic_account')
        
        # New detailed review fields
        rating = request.POST.get('rating') or 4.5
        execution_speed = request.POST.get('execution_speed') or 90
        customer_support = request.POST.get('customer_support') or 90
        asset_variety = request.POST.get('asset_variety') or 90
        pros_en = request.POST.get('pros_en', '')
        pros_ar = request.POST.get('pros_ar', '')
        cons_en = request.POST.get('cons_en', '')
        cons_ar = request.POST.get('cons_ar', '')
        
        custom_terminal_title_en = request.POST.get('custom_terminal_title_en', '')
        custom_terminal_title_ar = request.POST.get('custom_terminal_title_ar', '')
        custom_terminal_description_en = request.POST.get('custom_terminal_description_en', '')
        custom_terminal_description_ar = request.POST.get('custom_terminal_description_ar', '')
        
        verdict_quote_en = request.POST.get('verdict_quote_en', '')
        verdict_quote_ar = request.POST.get('verdict_quote_ar', '')
        verdict_text_en = request.POST.get('verdict_text_en', '')
        verdict_text_ar = request.POST.get('verdict_text_ar', '')

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
                name_en=name_en,
                name_ar=name_ar,
                slug=slug,
                seo_title_en=seo_title_en,
                seo_title_ar=seo_title_ar,
                seo_description_en=seo_description_en,
                seo_description_ar=seo_description_ar,
                review_content_en=review_content_en,
                review_content_ar=review_content_ar,
                min_deposit=min_deposit,
                withdrawal_time_en=withdrawal_time_en,
                withdrawal_time_ar=withdrawal_time_ar,
                base_currencies=base_currencies,
                headquarters_id=hq_id if hq_id else None,
                islamic_account_id=islamic_id if islamic_id else None,
                deposit_limit=dep_limit,
                logo=request.FILES.get('logo'),
                logo_alt_en=logo_alt_en,
                logo_alt_ar=logo_alt_ar,
                
                # New fields mapping
                rating=rating,
                execution_speed=execution_speed,
                customer_support=customer_support,
                asset_variety=asset_variety,
                pros_en=pros_en,
                pros_ar=pros_ar,
                cons_en=cons_en,
                cons_ar=cons_ar,
                custom_terminal_title_en=custom_terminal_title_en,
                custom_terminal_title_ar=custom_terminal_title_ar,
                custom_terminal_description_en=custom_terminal_description_en,
                custom_terminal_description_ar=custom_terminal_description_ar,
                custom_terminal_image=request.FILES.get('custom_terminal_image'),
                verdict_quote_en=verdict_quote_en,
                verdict_quote_ar=verdict_quote_ar,
                verdict_text_en=verdict_text_en,
                verdict_text_ar=verdict_text_ar
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
            faq_questions_en = request.POST.getlist('faq_question_en')
            faq_questions_ar = request.POST.getlist('faq_question_ar')
            faq_answers_en = request.POST.getlist('faq_answer_en')
            faq_answers_ar = request.POST.getlist('faq_answer_ar')
            
            for i in range(max(len(faq_questions_en), len(faq_questions_ar))):
                q_en = faq_questions_en[i].strip() if i < len(faq_questions_en) else ""
                q_ar = faq_questions_ar[i].strip() if i < len(faq_questions_ar) else ""
                a_en = faq_answers_en[i].strip() if i < len(faq_answers_en) else ""
                a_ar = faq_answers_ar[i].strip() if i < len(faq_answers_ar) else ""
                
                if q_en or q_ar or a_en or a_ar:
                    BrokerFAQ.objects.create(
                        broker=broker,
                        question_en=q_en,
                        question_ar=q_ar,
                        answer_en=a_en,
                        answer_ar=a_ar,
                        order=i
                    )
            
            # Create Account Types
            account_names_en = request.POST.getlist('account_name_en')
            account_names_ar = request.POST.getlist('account_name_ar')
            account_min_deposits_en = request.POST.getlist('account_min_deposit_en')
            account_min_deposits_ar = request.POST.getlist('account_min_deposit_ar')
            account_spread_froms_en = request.POST.getlist('account_spread_from_en')
            account_spread_froms_ar = request.POST.getlist('account_spread_from_ar')
            account_commissions_en = request.POST.getlist('account_commission_en')
            account_commissions_ar = request.POST.getlist('account_commission_ar')
            account_leverages_en = request.POST.getlist('account_leverage_en')
            account_leverages_ar = request.POST.getlist('account_leverage_ar')
            
            for i in range(max(len(account_names_en), len(account_names_ar))):
                acc_name_en = account_names_en[i].strip() if i < len(account_names_en) else ""
                acc_name_ar = account_names_ar[i].strip() if i < len(account_names_ar) else ""
                acc_min_dep_en = account_min_deposits_en[i].strip() if i < len(account_min_deposits_en) else ""
                acc_min_dep_ar = account_min_deposits_ar[i].strip() if i < len(account_min_deposits_ar) else ""
                acc_spread_en = account_spread_froms_en[i].strip() if i < len(account_spread_froms_en) else ""
                acc_spread_ar = account_spread_froms_ar[i].strip() if i < len(account_spread_froms_ar) else ""
                acc_comm_en = account_commissions_en[i].strip() if i < len(account_commissions_en) else ""
                acc_comm_ar = account_commissions_ar[i].strip() if i < len(account_commissions_ar) else ""
                acc_lev_en = account_leverages_en[i].strip() if i < len(account_leverages_en) else ""
                acc_lev_ar = account_leverages_ar[i].strip() if i < len(account_leverages_ar) else ""
                
                if acc_name_en or acc_name_ar:
                    BrokerAccountType.objects.create(
                        broker=broker,
                        name_en=acc_name_en,
                        name_ar=acc_name_ar,
                        min_deposit_en=acc_min_dep_en,
                        min_deposit_ar=acc_min_dep_ar,
                        spread_from_en=acc_spread_en,
                        spread_from_ar=acc_spread_ar,
                        commission_en=acc_comm_en,
                        commission_ar=acc_comm_ar,
                        leverage_en=acc_lev_en,
                        leverage_ar=acc_lev_ar,
                        order=i
                    )
            
            # Create Platform Tabs
            platform_titles_en = request.POST.getlist('platform_title_en')
            platform_titles_ar = request.POST.getlist('platform_title_ar')
            platform_subtitles_en = request.POST.getlist('platform_subtitle_en')
            platform_subtitles_ar = request.POST.getlist('platform_subtitle_ar')
            
            for i in range(max(len(platform_titles_en), len(platform_titles_ar))):
                plat_title_en = platform_titles_en[i].strip() if i < len(platform_titles_en) else ""
                plat_title_ar = platform_titles_ar[i].strip() if i < len(platform_titles_ar) else ""
                plat_sub_en = platform_subtitles_en[i].strip() if i < len(platform_subtitles_en) else ""
                plat_sub_ar = platform_subtitles_ar[i].strip() if i < len(platform_subtitles_ar) else ""
                
                if plat_title_en or plat_title_ar:
                    BrokerPlatformTab.objects.create(
                        broker=broker,
                        title_en=plat_title_en,
                        title_ar=plat_title_ar,
                        subtitle_en=plat_sub_en,
                        subtitle_ar=plat_sub_ar,
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
        }
        return render(request, 'dashboard/broker_form.html', context)

    def post(self, request, pk):
        broker = get_object_or_404(Broker, pk=pk)
        
        name_en = request.POST.get('name_en')
        name_ar = request.POST.get('name_ar')
        slug = request.POST.get('slug')
        seo_title_en = request.POST.get('seo_title_en', '')
        seo_title_ar = request.POST.get('seo_title_ar', '')
        seo_description_en = request.POST.get('seo_description_en', '')
        seo_description_ar = request.POST.get('seo_description_ar', '')
        review_content_en = request.POST.get('review_content_en', '')
        review_content_ar = request.POST.get('review_content_ar', '')
        min_deposit = request.POST.get('min_deposit') or 0.00
        withdrawal_time_en = request.POST.get('withdrawal_time_en', '')
        withdrawal_time_ar = request.POST.get('withdrawal_time_ar', '')
        base_currencies = request.POST.get('base_currencies', '')
        logo_alt_en = request.POST.get('logo_alt_en', '')
        logo_alt_ar = request.POST.get('logo_alt_ar', '')
        
        hq_id = request.POST.get('headquarters')
        islamic_id = request.POST.get('islamic_account')

        # New detailed review fields
        rating = request.POST.get('rating') or 4.5
        execution_speed = request.POST.get('execution_speed') or 90
        customer_support = request.POST.get('customer_support') or 90
        asset_variety = request.POST.get('asset_variety') or 90
        pros_en = request.POST.get('pros_en', '')
        pros_ar = request.POST.get('pros_ar', '')
        cons_en = request.POST.get('cons_en', '')
        cons_ar = request.POST.get('cons_ar', '')
        
        custom_terminal_title_en = request.POST.get('custom_terminal_title_en', '')
        custom_terminal_title_ar = request.POST.get('custom_terminal_title_ar', '')
        custom_terminal_description_en = request.POST.get('custom_terminal_description_en', '')
        custom_terminal_description_ar = request.POST.get('custom_terminal_description_ar', '')
        
        verdict_quote_en = request.POST.get('verdict_quote_en', '')
        verdict_quote_ar = request.POST.get('verdict_quote_ar', '')
        verdict_text_en = request.POST.get('verdict_text_en', '')
        verdict_text_ar = request.POST.get('verdict_text_ar', '')

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
            broker.name_en = name_en
            broker.name_ar = name_ar
            broker.slug = slug
            broker.seo_title_en = seo_title_en
            broker.seo_title_ar = seo_title_ar
            broker.seo_description_en = seo_description_en
            broker.seo_description_ar = seo_description_ar
            broker.review_content_en = review_content_en
            broker.review_content_ar = review_content_ar
            broker.min_deposit = min_deposit
            broker.withdrawal_time_en = withdrawal_time_en
            broker.withdrawal_time_ar = withdrawal_time_ar
            broker.base_currencies = base_currencies
            broker.headquarters_id = hq_id if hq_id else None
            broker.islamic_account_id = islamic_id if islamic_id else None
            broker.deposit_limit = dep_limit
            broker.logo_alt_en = logo_alt_en
            broker.logo_alt_ar = logo_alt_ar
            
            # Update review detail fields
            broker.rating = rating
            broker.execution_speed = execution_speed
            broker.customer_support = customer_support
            broker.asset_variety = asset_variety
            broker.pros_en = pros_en
            broker.pros_ar = pros_ar
            broker.cons_en = cons_en
            broker.cons_ar = cons_ar
            broker.custom_terminal_title_en = custom_terminal_title_en
            broker.custom_terminal_title_ar = custom_terminal_title_ar
            broker.custom_terminal_description_en = custom_terminal_description_en
            broker.custom_terminal_description_ar = custom_terminal_description_ar
            broker.verdict_quote_en = verdict_quote_en
            broker.verdict_quote_ar = verdict_quote_ar
            broker.verdict_text_en = verdict_text_en
            broker.verdict_text_ar = verdict_text_ar
            
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
            faq_questions_en = request.POST.getlist('faq_question_en')
            faq_questions_ar = request.POST.getlist('faq_question_ar')
            faq_answers_en = request.POST.getlist('faq_answer_en')
            faq_answers_ar = request.POST.getlist('faq_answer_ar')
            
            for i in range(max(len(faq_questions_en), len(faq_questions_ar))):
                q_en = faq_questions_en[i].strip() if i < len(faq_questions_en) else ""
                q_ar = faq_questions_ar[i].strip() if i < len(faq_questions_ar) else ""
                a_en = faq_answers_en[i].strip() if i < len(faq_answers_en) else ""
                a_ar = faq_answers_ar[i].strip() if i < len(faq_answers_ar) else ""
                
                if q_en or q_ar or a_en or a_ar:
                    BrokerFAQ.objects.create(
                        broker=broker,
                        question_en=q_en,
                        question_ar=q_ar,
                        answer_en=a_en,
                        answer_ar=a_ar,
                        order=i
                    )
            
            # Recreate Account Types
            broker.account_types.all().delete()
            account_names_en = request.POST.getlist('account_name_en')
            account_names_ar = request.POST.getlist('account_name_ar')
            account_min_deposits_en = request.POST.getlist('account_min_deposit_en')
            account_min_deposits_ar = request.POST.getlist('account_min_deposit_ar')
            account_spread_froms_en = request.POST.getlist('account_spread_from_en')
            account_spread_froms_ar = request.POST.getlist('account_spread_from_ar')
            account_commissions_en = request.POST.getlist('account_commission_en')
            account_commissions_ar = request.POST.getlist('account_commission_ar')
            account_leverages_en = request.POST.getlist('account_leverage_en')
            account_leverages_ar = request.POST.getlist('account_leverage_ar')
            
            for i in range(max(len(account_names_en), len(account_names_ar), 1) if (account_names_en or account_names_ar) else 0):
                acc_name_en = account_names_en[i].strip() if i < len(account_names_en) else ""
                acc_name_ar = account_names_ar[i].strip() if i < len(account_names_ar) else ""
                acc_min_dep_en = account_min_deposits_en[i].strip() if i < len(account_min_deposits_en) else ""
                acc_min_dep_ar = account_min_deposits_ar[i].strip() if i < len(account_min_deposits_ar) else ""
                acc_spread_en = account_spread_froms_en[i].strip() if i < len(account_spread_froms_en) else ""
                acc_spread_ar = account_spread_froms_ar[i].strip() if i < len(account_spread_froms_ar) else ""
                acc_comm_en = account_commissions_en[i].strip() if i < len(account_commissions_en) else ""
                acc_comm_ar = account_commissions_ar[i].strip() if i < len(account_commissions_ar) else ""
                acc_lev_en = account_leverages_en[i].strip() if i < len(account_leverages_en) else ""
                acc_lev_ar = account_leverages_ar[i].strip() if i < len(account_leverages_ar) else ""
                
                if acc_name_en or acc_name_ar:
                    BrokerAccountType.objects.create(
                        broker=broker,
                        name_en=acc_name_en,
                        name_ar=acc_name_ar,
                        min_deposit_en=acc_min_dep_en,
                        min_deposit_ar=acc_min_dep_ar,
                        spread_from_en=acc_spread_en,
                        spread_from_ar=acc_spread_ar,
                        commission_en=acc_comm_en,
                        commission_ar=acc_comm_ar,
                        leverage_en=acc_lev_en,
                        leverage_ar=acc_lev_ar,
                        order=i
                    )
            
            # Recreate Platform Tabs
            broker.platform_tabs.all().delete()
            platform_titles_en = request.POST.getlist('platform_title_en')
            platform_titles_ar = request.POST.getlist('platform_title_ar')
            platform_subtitles_en = request.POST.getlist('platform_subtitle_en')
            platform_subtitles_ar = request.POST.getlist('platform_subtitle_ar')
            
            for i in range(max(len(platform_titles_en), len(platform_titles_ar), 1) if (platform_titles_en or platform_titles_ar) else 0):
                plat_title_en = platform_titles_en[i].strip() if i < len(platform_titles_en) else ""
                plat_title_ar = platform_titles_ar[i].strip() if i < len(platform_titles_ar) else ""
                plat_sub_en = platform_subtitles_en[i].strip() if i < len(platform_subtitles_en) else ""
                plat_sub_ar = platform_subtitles_ar[i].strip() if i < len(platform_subtitles_ar) else ""
                
                if plat_title_en or plat_title_ar:
                    BrokerPlatformTab.objects.create(
                        broker=broker,
                        title_en=plat_title_en,
                        title_ar=plat_title_ar,
                        subtitle_en=plat_sub_en,
                        subtitle_ar=plat_sub_ar,
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
        from categories.models import Regulator, Headquarters, IslamicAccount, DepositLimit
        
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
        }
        
        model_class = model_map.get(model_type)
        if not model_class:
            return JsonResponse({'error': 'Invalid taxonomy type'}, status=400)
            
        # Check if already exists in database (case insensitive on translated fields)
        instance = model_class.objects.filter(Q(name_en__iexact=name) | Q(name_ar__iexact=name)).first()
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
                name_en=name,
                name_ar=name,
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
        }
        return render(request, 'dashboard/article_form.html', context)

    def post(self, request):
        title_en = request.POST.get('title_en')
        title_ar = request.POST.get('title_ar')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        seo_title_en = request.POST.get('seo_title_en', '')
        seo_title_ar = request.POST.get('seo_title_ar', '')
        seo_description_en = request.POST.get('seo_description_en', '')
        seo_description_ar = request.POST.get('seo_description_ar', '')
        content_en = request.POST.get('content_en', '')
        content_ar = request.POST.get('content_ar', '')
        featured_image_alt_en = request.POST.get('featured_image_alt_en', '')
        featured_image_alt_ar = request.POST.get('featured_image_alt_ar', '')

        with transaction.atomic():
            article = Article.objects.create(
                title_en=title_en,
                title_ar=title_ar,
                slug=slug,
                status=status,
                seo_title_en=seo_title_en,
                seo_title_ar=seo_title_ar,
                seo_description_en=seo_description_en,
                seo_description_ar=seo_description_ar,
                content_en=content_en,
                content_ar=content_ar,
                featured_image_alt_en=featured_image_alt_en,
                featured_image_alt_ar=featured_image_alt_ar,
            )
            if request.FILES.get('featured_image'):
                article.featured_image = request.FILES.get('featured_image')
                article.save()

            faq_questions_en = request.POST.getlist('faq_question_en')
            faq_questions_ar = request.POST.getlist('faq_question_ar')
            faq_answers_en = request.POST.getlist('faq_answer_en')
            faq_answers_ar = request.POST.getlist('faq_answer_ar')

            for i in range(max(len(faq_questions_en), len(faq_questions_ar))):
                q_en = faq_questions_en[i].strip() if i < len(faq_questions_en) else ""
                q_ar = faq_questions_ar[i].strip() if i < len(faq_questions_ar) else ""
                a_en = faq_answers_en[i].strip() if i < len(faq_answers_en) else ""
                a_ar = faq_answers_ar[i].strip() if i < len(faq_answers_ar) else ""

                if q_en or q_ar or a_en or a_ar:
                    ArticleFAQ.objects.create(
                        article=article,
                        question_en=q_en,
                        question_ar=q_ar,
                        answer_en=a_en,
                        answer_ar=a_ar,
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
        }
        return render(request, 'dashboard/article_form.html', context)

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        title_en = request.POST.get('title_en')
        title_ar = request.POST.get('title_ar')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        seo_title_en = request.POST.get('seo_title_en', '')
        seo_title_ar = request.POST.get('seo_title_ar', '')
        seo_description_en = request.POST.get('seo_description_en', '')
        seo_description_ar = request.POST.get('seo_description_ar', '')
        content_en = request.POST.get('content_en', '')
        content_ar = request.POST.get('content_ar', '')
        featured_image_alt_en = request.POST.get('featured_image_alt_en', '')
        featured_image_alt_ar = request.POST.get('featured_image_alt_ar', '')

        with transaction.atomic():
            article.title_en = title_en
            article.title_ar = title_ar
            article.slug = slug
            article.status = status
            article.seo_title_en = seo_title_en
            article.seo_title_ar = seo_title_ar
            article.seo_description_en = seo_description_en
            article.seo_description_ar = seo_description_ar
            article.content_en = content_en
            article.content_ar = content_ar
            article.featured_image_alt_en = featured_image_alt_en
            article.featured_image_alt_ar = featured_image_alt_ar

            if request.FILES.get('featured_image'):
                article.featured_image = request.FILES.get('featured_image')
            elif request.POST.get('featured_image-clear') == 'on':
                article.featured_image = None

            article.save()

            article.faqs.all().delete()
            faq_questions_en = request.POST.getlist('faq_question_en')
            faq_questions_ar = request.POST.getlist('faq_question_ar')
            faq_answers_en = request.POST.getlist('faq_answer_en')
            faq_answers_ar = request.POST.getlist('faq_answer_ar')

            for i in range(max(len(faq_questions_en), len(faq_questions_ar))):
                q_en = faq_questions_en[i].strip() if i < len(faq_questions_en) else ""
                q_ar = faq_questions_ar[i].strip() if i < len(faq_questions_ar) else ""
                a_en = faq_answers_en[i].strip() if i < len(faq_answers_en) else ""
                a_ar = faq_answers_ar[i].strip() if i < len(faq_answers_ar) else ""

                if q_en or q_ar or a_en or a_ar:
                    ArticleFAQ.objects.create(
                        article=article,
                        question_en=q_en,
                        question_ar=q_ar,
                        answer_en=a_en,
                        answer_ar=a_ar,
                        order=i
                    )

        return redirect('dashboard_articles')


class DashboardBestBrokersCreateView(LoginRequiredMixin, View):
    def get(self, request):
        brokers = Broker.objects.all()
        context = {
            'brokers': brokers,
            'is_edit': False,
        }
        return render(request, 'dashboard/best_brokers_form.html', context)

    def post(self, request):
        title_en = request.POST.get('title_en')
        title_ar = request.POST.get('title_ar')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        visibility = request.POST.get('visibility', 'private')
        seo_title_en = request.POST.get('seo_title_en', '')
        seo_title_ar = request.POST.get('seo_title_ar', '')
        seo_description_en = request.POST.get('seo_description_en', '')
        seo_description_ar = request.POST.get('seo_description_ar', '')
        content_en = request.POST.get('content_en', '')
        content_ar = request.POST.get('content_ar', '')
        featured_image_alt_en = request.POST.get('featured_image_alt_en', '')
        featured_image_alt_ar = request.POST.get('featured_image_alt_ar', '')

        with transaction.atomic():
            best_list = BestBrokersList.objects.create(
                title_en=title_en,
                title_ar=title_ar,
                slug=slug,
                status=status,
                visibility=visibility,
                seo_title_en=seo_title_en,
                seo_title_ar=seo_title_ar,
                seo_description_en=seo_description_en,
                seo_description_ar=seo_description_ar,
                content_en=content_en,
                content_ar=content_ar,
                featured_image_alt_en=featured_image_alt_en,
                featured_image_alt_ar=featured_image_alt_ar,
            )
            if request.FILES.get('featured_image'):
                best_list.featured_image = request.FILES.get('featured_image')
                best_list.save()

            # Save ranked items
            broker_ids = request.POST.getlist('item_broker')
            ranks = request.POST.getlist('item_rank')
            desc_ens = request.POST.getlist('item_description_en')
            desc_ars = request.POST.getlist('item_description_ar')

            for i in range(len(broker_ids)):
                b_id = broker_ids[i]
                if not b_id:
                    continue
                rk = ranks[i] if i < len(ranks) else (i + 1)
                d_en = desc_ens[i].strip() if i < len(desc_ens) else ""
                d_ar = desc_ars[i].strip() if i < len(desc_ars) else ""

                BestBrokersListItem.objects.create(
                    best_brokers_list=best_list,
                    broker_id=b_id,
                    rank=rk,
                    description_en=d_en,
                    description_ar=d_ar
                )

            # Save FAQs
            faq_questions_en = request.POST.getlist('faq_question_en')
            faq_questions_ar = request.POST.getlist('faq_question_ar')
            faq_answers_en = request.POST.getlist('faq_answer_en')
            faq_answers_ar = request.POST.getlist('faq_answer_ar')

            for i in range(max(len(faq_questions_en), len(faq_questions_ar))):
                q_en = faq_questions_en[i].strip() if i < len(faq_questions_en) else ""
                q_ar = faq_questions_ar[i].strip() if i < len(faq_questions_ar) else ""
                a_en = faq_answers_en[i].strip() if i < len(faq_answers_en) else ""
                a_ar = faq_answers_ar[i].strip() if i < len(faq_answers_ar) else ""

                if q_en or q_ar or a_en or a_ar:
                    BestBrokersListFAQ.objects.create(
                        best_brokers_list=best_list,
                        question_en=q_en,
                        question_ar=q_ar,
                        answer_en=a_en,
                        answer_ar=a_ar,
                        order=i
                    )

        return redirect('dashboard_best_brokers')


class DashboardBestBrokersUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        best_list = get_object_or_404(BestBrokersList, pk=pk)
        brokers = Broker.objects.all()
        context = {
            'best_list': best_list,
            'brokers': brokers,
            'items': best_list.items.all(),
            'faqs': best_list.faqs.all(),
            'is_edit': True,
        }
        return render(request, 'dashboard/best_brokers_form.html', context)

    def post(self, request, pk):
        best_list = get_object_or_404(BestBrokersList, pk=pk)
        title_en = request.POST.get('title_en')
        title_ar = request.POST.get('title_ar')
        slug = request.POST.get('slug')
        status = request.POST.get('status', 'draft')
        visibility = request.POST.get('visibility', 'private')
        seo_title_en = request.POST.get('seo_title_en', '')
        seo_title_ar = request.POST.get('seo_title_ar', '')
        seo_description_en = request.POST.get('seo_description_en', '')
        seo_description_ar = request.POST.get('seo_description_ar', '')
        content_en = request.POST.get('content_en', '')
        content_ar = request.POST.get('content_ar', '')
        featured_image_alt_en = request.POST.get('featured_image_alt_en', '')
        featured_image_alt_ar = request.POST.get('featured_image_alt_ar', '')

        with transaction.atomic():
            best_list.title_en = title_en
            best_list.title_ar = title_ar
            best_list.slug = slug
            best_list.status = status
            best_list.visibility = visibility
            best_list.seo_title_en = seo_title_en
            best_list.seo_title_ar = seo_title_ar
            best_list.seo_description_en = seo_description_en
            best_list.seo_description_ar = seo_description_ar
            best_list.content_en = content_en
            best_list.content_ar = content_ar
            best_list.featured_image_alt_en = featured_image_alt_en
            best_list.featured_image_alt_ar = featured_image_alt_ar

            if request.FILES.get('featured_image'):
                best_list.featured_image = request.FILES.get('featured_image')
            elif request.POST.get('featured_image-clear') == 'on':
                best_list.featured_image = None

            best_list.save()

            # Update ranked items
            best_list.items.all().delete()
            broker_ids = request.POST.getlist('item_broker')
            ranks = request.POST.getlist('item_rank')
            desc_ens = request.POST.getlist('item_description_en')
            desc_ars = request.POST.getlist('item_description_ar')

            for i in range(len(broker_ids)):
                b_id = broker_ids[i]
                if not b_id:
                    continue
                rk = ranks[i] if i < len(ranks) else (i + 1)
                d_en = desc_ens[i].strip() if i < len(desc_ens) else ""
                d_ar = desc_ars[i].strip() if i < len(desc_ars) else ""

                BestBrokersListItem.objects.create(
                    best_brokers_list=best_list,
                    broker_id=b_id,
                    rank=rk,
                    description_en=d_en,
                    description_ar=d_ar
                )

            # Update FAQs
            best_list.faqs.all().delete()
            faq_questions_en = request.POST.getlist('faq_question_en')
            faq_questions_ar = request.POST.getlist('faq_question_ar')
            faq_answers_en = request.POST.getlist('faq_answer_en')
            faq_answers_ar = request.POST.getlist('faq_answer_ar')

            for i in range(max(len(faq_questions_en), len(faq_questions_ar))):
                q_en = faq_questions_en[i].strip() if i < len(faq_questions_en) else ""
                q_ar = faq_questions_ar[i].strip() if i < len(faq_questions_ar) else ""
                a_en = faq_answers_en[i].strip() if i < len(faq_answers_en) else ""
                a_ar = faq_answers_ar[i].strip() if i < len(faq_answers_ar) else ""

                if q_en or q_ar or a_en or a_ar:
                    BestBrokersListFAQ.objects.create(
                        best_brokers_list=best_list,
                        question_en=q_en,
                        question_ar=q_ar,
                        answer_en=a_en,
                        answer_ar=a_ar,
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
