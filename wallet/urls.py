from django.urls import path
from . import views

urlpatterns = [
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/', views.transaction_list, name='transaction_list'),
]