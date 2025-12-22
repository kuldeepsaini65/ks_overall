from django.urls import path
from finance import views

app_name = 'finance'

urlpatterns = [
    path('<module>', views.expense_dashboard, name='finance_dashboard'),

    # Expenses Category
    path('<module>/categories/add/', views.category_create, name='category_add'),
    path('<module>/categories/list/', views.category_list, name='category_list'),


    # Debt 
    path('<module>/debts/add/', views.debt_add, name='debt_add'),
    path('<module>/debts/<int:pk>/', views.debt_info, name='debt_info'),
    path('<module>/debts/lists/', views.debt_list, name='debt_list'),
    path('<module>/debts/<int:pk>/edit/', views.debt_edit, name='debt_edit'),
    path('<module>/debts/<int:pk>/delete/', views.debt_delete, name='debt_delete'),


    # Expenses Transactions
    path('<module>/transactions/lists', views.expense_list, name='exp_list'),
    path('<module>/transactions/add/', views.expense_create, name='exp_add'),
    path('<module>/transactions/<int:pk>/edit/', views.expense_update, name='exp_edit'),
    path('<module>/transactions/<int:pk>/delete/', views.expense_delete, name='exp_delete'),



]
