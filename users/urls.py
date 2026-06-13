from django.urls import path
from .views import (
    CustomLoginView, custom_logout_view, RegisterView, ProfileView, 
    DashboardView, DashboardBrokersView, DashboardArticlesView, DashboardBestBrokersView,
    DashboardBrokerCreateView, DashboardBrokerUpdateView, DashboardImageUploadView,
    DashboardArticleCreateView, DashboardArticleUpdateView, DashboardBestBrokersCreateView, DashboardBestBrokersUpdateView
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/brokers/', DashboardBrokersView.as_view(), name='dashboard_brokers'),
    path('dashboard/brokers/add/', DashboardBrokerCreateView.as_view(), name='dashboard_brokers_add'),
    path('dashboard/brokers/<int:pk>/edit/', DashboardBrokerUpdateView.as_view(), name='dashboard_brokers_edit'),
    path('dashboard/upload-image/', DashboardImageUploadView.as_view(), name='dashboard_upload_image'),
    path('dashboard/articles/', DashboardArticlesView.as_view(), name='dashboard_articles'),
    path('dashboard/articles/add/', DashboardArticleCreateView.as_view(), name='dashboard_articles_add'),
    path('dashboard/articles/<int:pk>/edit/', DashboardArticleUpdateView.as_view(), name='dashboard_articles_edit'),
    path('dashboard/best-brokers/', DashboardBestBrokersView.as_view(), name='dashboard_best_brokers'),
    path('dashboard/best-brokers/add/', DashboardBestBrokersCreateView.as_view(), name='dashboard_best_brokers_add'),
    path('dashboard/best-brokers/<int:pk>/edit/', DashboardBestBrokersUpdateView.as_view(), name='dashboard_best_brokers_edit'),
]
