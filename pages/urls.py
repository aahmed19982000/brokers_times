from django.urls import path
from .views import (
    HomeView, BrokerReviewDetailView, BrokerDirectoryView, ArticleDirectoryView,
    ArticleDetailView, CompareListView, BestBrokersListDetailView, AboutUsView,
    PrivacyPolicyView, TermsOfServiceView, DisclaimerView, CookiePolicyView,
    ContactUsView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('brokers-reviews/', BrokerDirectoryView.as_view(), name='broker_directory'),
    path('brokers-reviews/<slug:slug>/', BrokerReviewDetailView.as_view(), name='broker_review_detail'),
    path('trading-articles/', ArticleDirectoryView.as_view(), name='article_directory'),
    path('trading-articles/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('best-broker/', CompareListView.as_view(), name='compare_list'),
    path('best-broker/<slug:slug>/', BestBrokersListDetailView.as_view(), name='best_brokers_list_detail'),
    path('about/', AboutUsView.as_view(), name='about_us'),
    path('contact/', ContactUsView.as_view(), name='contact_us'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', TermsOfServiceView.as_view(), name='terms_of_service'),
    path('disclaimer/', DisclaimerView.as_view(), name='disclaimer'),
    path('cookie-policy/', CookiePolicyView.as_view(), name='cookie_policy'),
]


