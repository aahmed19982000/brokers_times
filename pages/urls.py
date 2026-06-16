from django.urls import path
from .views import (
    HomeView, BrokerReviewDetailView, BrokerDirectoryView, ArticleDirectoryView,
    CompareListView, BestBrokersListDetailView, AboutUsView,
    PrivacyPolicyView, TermsOfServiceView, DisclaimerView, CookiePolicyView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('reviews/', BrokerDirectoryView.as_view(), name='broker_directory'),
    path('reviews/<slug:slug>/', BrokerReviewDetailView.as_view(), name='broker_review_detail'),
    path('education/', ArticleDirectoryView.as_view(), name='article_directory'),
    path('compare/', CompareListView.as_view(), name='compare_list'),
    path('compare/<slug:slug>/', BestBrokersListDetailView.as_view(), name='best_brokers_list_detail'),
    path('about/', AboutUsView.as_view(), name='about_us'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-of-service/', TermsOfServiceView.as_view(), name='terms_of_service'),
    path('disclaimer/', DisclaimerView.as_view(), name='disclaimer'),
    path('cookie-policy/', CookiePolicyView.as_view(), name='cookie_policy'),
]


