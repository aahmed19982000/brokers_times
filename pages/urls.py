from django.urls import path
from .views import HomeView, BrokerReviewDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('reviews/<slug:slug>/', BrokerReviewDetailView.as_view(), name='broker_review_detail'),
]

