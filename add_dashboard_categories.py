import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brokers_times.settings')
django.setup()

# 1. Update urls.py
with open('users/urls.py', 'r') as f:
    urls_content = f.read()

if 'DashboardCategoriesView' not in urls_content:
    urls_content = urls_content.replace(
        "DashboardNewsView, DashboardNewsCreateView, DashboardNewsUpdateView\n)",
        "DashboardNewsView, DashboardNewsCreateView, DashboardNewsUpdateView,\n    DashboardCategoriesView, DashboardCategoryCreateView, DashboardCategoryUpdateView\n)"
    )
    urls_content = urls_content.replace(
        "]",
        "    path('dashboard/categories/', DashboardCategoriesView.as_view(), name='dashboard_categories'),\n    path('dashboard/categories/add/', DashboardCategoryCreateView.as_view(), name='dashboard_categories_add'),\n    path('dashboard/categories/<int:pk>/edit/', DashboardCategoryUpdateView.as_view(), name='dashboard_categories_edit'),\n]"
    )
    with open('users/urls.py', 'w') as f:
        f.write(urls_content)

print("Updated URLs")

# 2. Update views.py
with open('users/views.py', 'a') as f:
    f.write('''
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
        if hasattr(Model, 'icon'):
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
        if request.FILES.get('icon') and hasattr(item, 'icon'):
            item.icon = request.FILES.get('icon')
        item.save()
        return redirect(f'/dashboard/categories/?type={model_name}')
''')

print("Updated Views")
