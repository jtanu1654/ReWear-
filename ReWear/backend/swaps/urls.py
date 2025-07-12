from django.urls import path
from . import views

urlpatterns = [
    path('', views.SwapListView.as_view(), name='swaps'),
    path('create/', views.SwapCreateView.as_view(), name='swap_create'),
    path('<int:pk>/', views.SwapDetailView.as_view(), name='swap_detail'),
    path('<int:swap_id>/action/', views.SwapActionView.as_view(), name='swap_action'),
    path('<int:swap_id>/messages/', views.SwapMessageListView.as_view(), name='swap_messages'),
    path('<int:swap_id>/messages/create/', views.SwapMessageCreateView.as_view(), name='swap_message_create'),
    path('summary/', views.user_swaps_summary, name='swaps_summary'),
    path('history/', views.swap_history, name='swap_history'),
] 