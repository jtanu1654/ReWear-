from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('', views.ItemListView.as_view(), name='items'),
    path('featured/', views.FeaturedItemsView.as_view(), name='featured_items'),
    path('search/', views.search_items, name='search_items'),
    path('<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    
    # User URLs
    path('create/', views.ItemCreateView.as_view(), name='item_create'),
    path('my-items/', views.UserItemsView.as_view(), name='user_items'),
    path('update/<int:pk>/', views.ItemUpdateView.as_view(), name='item_update'),
    path('delete/<int:pk>/', views.ItemDeleteView.as_view(), name='item_delete'),
    
    # Admin URLs
    path('admin/', views.AdminItemListView.as_view(), name='admin_items'),
    path('admin/<int:pk>/', views.AdminItemDetailView.as_view(), name='admin_item_detail'),
    path('admin/approve/<int:item_id>/', views.approve_item, name='approve_item'),
    path('admin/reject/<int:item_id>/', views.reject_item, name='reject_item'),
    path('admin/feature/<int:item_id>/', views.toggle_featured, name='toggle_featured'),
] 