from django.urls import path
from .views import HomeView, BrokerReviewDetailView, BrokerDirectoryView, ArticleDirectoryView, CompareListView, BestBrokersListDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('reviews/', BrokerDirectoryView.as_view(), name='broker_directory'),
    path('reviews/<slug:slug>/', BrokerReviewDetailView.as_view(), name='broker_review_detail'),
    path('education/', ArticleDirectoryView.as_view(), name='article_directory'),
    path('compare/', CompareListView.as_view(), name='compare_list'),
    path('compare/<slug:slug>/', BestBrokersListDetailView.as_view(), name='best_brokers_list_detail'),
]


