from django.urls import path
from .views import CheckProcessingStatusView

urlpatterns = [
    path('check-status/', CheckProcessingStatusView.as_view(), name='check-status'),
]