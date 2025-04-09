# Get total feedback
# average sentiment
# top feedback score
# and % up since last mont
#
# trending topics (Categories)
# number of mentions or incidents
# overall sentiment for that category
#
#
#
# Each API should support time range. 7D 14D 4W 3M 6M 12M Custom
# recent feedback
# feedback sources
# Sentiment distribution
# sentiment trends
# sentiment score by platform type
#
# Product feedback category based sentiment
# Top feedback category
# category specific sentiment
#
# source distribution by percentage
#

# urls.py
from django.urls import path
from .views import (
    ReviewStatsView, LastSixMonthsStatsView, 
    TrendingTopicsView, TrendAnalysisView, 
    RecentFeedbackView, FeedbackSourcesView, SentimentDistributionView,
    SentimentTrendsView, SentimentBySourceView, ProductFeedbackCategoriesView, TopFeedbackTopicsView,
    FeatureSpecificFeedbackView, FeedbackSourcesDetailedView, FeedbackDetailsView, GenerateReportView
)

urlpatterns = [
    path('review-stats/<str:time_range>/', ReviewStatsView.as_view(), name='review-stats'),
    path('last-6-months/<str:time>/', LastSixMonthsStatsView.as_view(), name='last-6-months-stats'),
    path('trending-topics/<str:time>/', TrendingTopicsView.as_view(), name='trending-topics'),
    path('stats/<str:time_range>/', ReviewStatsView.as_view(), name='review-stats'),
    path('monthly-stats/', LastSixMonthsStatsView.as_view(), name='monthly-stats'),
    path('trending-topics/', TrendingTopicsView.as_view(), name='trending-topics'),
    path('trends/analysis/', TrendAnalysisView.as_view(), name='trend-analysis'),
    path('recent-feedback/<str:time>/', RecentFeedbackView.as_view(), name='recent-feedback'),
    path('feedback-sources/<str:time>/', FeedbackSourcesView.as_view(), name='feedback-sources'),
    path('sentiment-distribution/', SentimentDistributionView.as_view(), name='sentiment-distribution'),
    path('sentiment-trends/', SentimentTrendsView.as_view(), name='sentiment-trends'),
    path('sentiments-by-source/', SentimentBySourceView.as_view(), name='sentiment-by-source'),
    path('product-feedback-categories/', ProductFeedbackCategoriesView.as_view(), name='product-feedback-categories'),
    path('top-feedback-topics/', TopFeedbackTopicsView.as_view(), name='top-feedback-topics'),
    path('feature-specific-feedback/', FeatureSpecificFeedbackView.as_view(), name='feature-specific-feedback'),
    path('feedback-detailed-sources/', FeedbackSourcesDetailedView.as_view(), name='feedback_sources'),
    path('feedback-detail/', FeedbackDetailsView.as_view(), name='feedback-details'),
    path('reports/generate/', GenerateReportView.as_view(), name='generate-report'),
]
