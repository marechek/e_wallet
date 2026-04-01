from django.urls import path
from . import views

urlpatterns = [
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:pk>/edit/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('wallets/<int:pk>/edit/', views.wallet_update, name='wallet_update'),
    path('register/', views.register, name='register'),
    path('transactions/<int:pk>/reverse/', views.transaction_reverse, name='transaction_reverse'),
    path('types/', views.transaction_type_list, name='transaction_type_list'),
    path('types/create/', views.transaction_type_create, name='transaction_type_create'),
    path('types/<int:pk>/edit/', views.transaction_type_update, name='transaction_type_update'),
    path('types/<int:pk>/delete/', views.transaction_type_delete, name='transaction_type_delete'),
]