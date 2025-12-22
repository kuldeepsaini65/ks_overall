from django.contrib import admin
from .models import *


@admin.register(ExpenseCategory)
class ExpenseCategoryList(admin.ModelAdmin):
    list_display = ['name','slug', 'user']



@admin.register(Expense)
class ExpenseTransactionsList(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount','payment_mode','expense_date']


@admin.register(Debt)
class DebtList(admin.ModelAdmin):
    list_display = ['user', 'name', 'lender','debt_type','interest_rate','principal_amount']


