from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomUserProfileForm
from .models import CustomUser

from brokers.models import Broker, BrokerFAQ
from articles.models import Article, ArticleFAQ, Tag
from best_brokers.models import BestBrokersList, BestBrokersListItem, BestBrokersListFAQ
from categories.models import Regulator, FinancialAsset, Headquarters, IslamicAccount, Category
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
        context = {
            'regulators': regulators,
            'financial_assets': financial_assets,
            'headquarters': headquarters,
            'islamic_accounts': islamic_accounts,
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
        
        hq_id = request.POST.get('headquarters')
        islamic_id = request.POST.get('islamic_account')

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
                islamic_account_id=islamic_id if islamic_id else None
            )
            
            regulator_ids = request.POST.getlist('regulators')
            if regulator_ids:
                broker.regulators.set(Regulator.objects.filter(id__in=regulator_ids))
                
            asset_ids = request.POST.getlist('financial_assets')
            if asset_ids:
                broker.financial_assets.set(FinancialAsset.objects.filter(id__in=asset_ids))
                
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
                    
        return redirect('dashboard_brokers')

class DashboardBrokerUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        broker = get_object_or_404(Broker, pk=pk)
        regulators = Regulator.objects.all()
        financial_assets = FinancialAsset.objects.all()
        headquarters = Headquarters.objects.all()
        islamic_accounts = IslamicAccount.objects.all()
        
        selected_regulators = list(broker.regulators.values_list('id', flat=True))
        selected_assets = list(broker.financial_assets.values_list('id', flat=True))
        
        context = {
            'broker': broker,
            'regulators': regulators,
            'financial_assets': financial_assets,
            'headquarters': headquarters,
            'islamic_accounts': islamic_accounts,
            'selected_regulators': selected_regulators,
            'selected_assets': selected_assets,
            'faqs': broker.faqs.all(),
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
        
        hq_id = request.POST.get('headquarters')
        islamic_id = request.POST.get('islamic_account')

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
            broker.save()
            
            regulator_ids = request.POST.getlist('regulators')
            broker.regulators.set(Regulator.objects.filter(id__in=regulator_ids))
            
            asset_ids = request.POST.getlist('financial_assets')
            broker.financial_assets.set(FinancialAsset.objects.filter(id__in=asset_ids))
            
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


class DashboardArticleCreateView(LoginRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.all()
        tags = Tag.objects.all()
        context = {
            'categories': categories,
            'tags': tags,
            'is_edit': False,
        }
        return render(request, 'dashboard/article_form.html', context)

    def post(self, request):
        title_en = request.POST.get('title_en')
        title_ar = request.POST.get('title_ar')
        slug = request.POST.get('slug')
        category_id = request.POST.get('category')
        status = request.POST.get('status', 'draft')
        seo_title_en = request.POST.get('seo_title_en', '')
        seo_title_ar = request.POST.get('seo_title_ar', '')
        seo_description_en = request.POST.get('seo_description_en', '')
        seo_description_ar = request.POST.get('seo_description_ar', '')
        content_en = request.POST.get('content_en', '')
        content_ar = request.POST.get('content_ar', '')

        with transaction.atomic():
            article = Article.objects.create(
                title_en=title_en,
                title_ar=title_ar,
                slug=slug,
                category_id=category_id if category_id else None,
                status=status,
                seo_title_en=seo_title_en,
                seo_title_ar=seo_title_ar,
                seo_description_en=seo_description_en,
                seo_description_ar=seo_description_ar,
                content_en=content_en,
                content_ar=content_ar,
            )
            if request.FILES.get('featured_image'):
                article.featured_image = request.FILES.get('featured_image')
                article.save()

            tag_ids = request.POST.getlist('tags')
            if tag_ids:
                article.tags.set(Tag.objects.filter(id__in=tag_ids))

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
        categories = Category.objects.all()
        tags = Tag.objects.all()
        selected_tags = list(article.tags.values_list('id', flat=True))
        context = {
            'article': article,
            'categories': categories,
            'tags': tags,
            'selected_tags': selected_tags,
            'faqs': article.faqs.all(),
            'is_edit': True,
        }
        return render(request, 'dashboard/article_form.html', context)

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        title_en = request.POST.get('title_en')
        title_ar = request.POST.get('title_ar')
        slug = request.POST.get('slug')
        category_id = request.POST.get('category')
        status = request.POST.get('status', 'draft')
        seo_title_en = request.POST.get('seo_title_en', '')
        seo_title_ar = request.POST.get('seo_title_ar', '')
        seo_description_en = request.POST.get('seo_description_en', '')
        seo_description_ar = request.POST.get('seo_description_ar', '')
        content_en = request.POST.get('content_en', '')
        content_ar = request.POST.get('content_ar', '')

        with transaction.atomic():
            article.title_en = title_en
            article.title_ar = title_ar
            article.slug = slug
            article.category_id = category_id if category_id else None
            article.status = status
            article.seo_title_en = seo_title_en
            article.seo_title_ar = seo_title_ar
            article.seo_description_en = seo_description_en
            article.seo_description_ar = seo_description_ar
            article.content_en = content_en
            article.content_ar = content_ar

            if request.FILES.get('featured_image'):
                article.featured_image = request.FILES.get('featured_image')
            elif request.POST.get('featured_image-clear') == 'on':
                article.featured_image = None

            article.save()

            tag_ids = request.POST.getlist('tags')
            article.tags.set(Tag.objects.filter(id__in=tag_ids))

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
