from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, ExpenseCategory, Debt
from .forms import ExpenseForm, CategoryForm, DebtForm
from django.db.models import Sum
from django.utils.timezone import now
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from homecontrol.utils import _add_validation_messages, _add_form_error_messages
from datetime import date
import calendar


@login_required(login_url='homecontrol:login')
def expense_dashboard(request, module):
    today = now().date()

    qs = Expense.objects.filter(user=request.user)

    month_total = qs.filter(
        expense_date__year=today.year,
        expense_date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or 0

    today_total = qs.filter(expense_date=today).aggregate(
        total=Sum('amount')
    )['total'] or 0

    expense_count = qs.count()

    # Category summary
    category_summary = (
        qs.filter(
            expense_date__year=today.year,
            expense_date__month=today.month
        )
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    # Recent expenses
    recent_expenses = qs.order_by('-expense_date', '-id')[:5]
    context = {
        'month_total': month_total,
        'today_total': today_total,
        'expense_count': expense_count,
        'category_summary': category_summary,
        'recent_expenses': recent_expenses,
        'module' : module
    }

    return render(request, 'expense_dashboard.html', context)






# Category
@login_required(login_url='homecontrol:login')
def category_create(request, module):
    if not request.user.is_superuser:
        messages.warning(request, 'Permission denided !!')
        return redirect('finance:category_list', module = module)
    
    context = {}
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        category = form.save(commit=False)
        category.user = request.user
        try:
            category.save()
            return redirect('finance:category_list', module=module)
        
        except ValidationError as e:
            form.add_error('name', e.message_dict.get('name'))
            print(e)

    context['form'] = form
    context['module'] = module

    return render(request, 'expense_category/category_form.html', context)


@login_required(login_url='homecontrol:login')
def category_list(request, module):
    
    context = {}
    data = ExpenseCategory.objects.filter(Q(user=request.user) | Q(user__is_superuser=True)
    ).filter(is_deleted = False)
    context['data'] = data
    context['module'] = module

    return render(request, 'expense_category/category_list.html', context)



@login_required
def debt_add(request, module):
    form = DebtForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            debt = form.save(commit=False)
            debt.user = request.user

            try:
                debt.save()
                messages.success(request, "Debt added successfully.")
                return redirect('finance:debt_info', pk=debt.pk, module=module)

            except ValidationError as e:
                _add_validation_messages(request, e)

        else:
            _add_form_error_messages(request, form)

    return render(
        request,
        'debt/debt_form.html',
        {
            'form': form,
            'module': module
        }
    )

@login_required
def debt_info(request, module, pk):
    context = {}

    debt = get_object_or_404(Debt, pk=pk, user=request.user)

    debt_payments = Expense.objects.filter(debt__id = pk).filter(user = request.user)

    context['debt'] = debt
    context['debt_payments'] = debt_payments
    context['module'] = module

    return render(request, 'debt/debt_info.html', context)

def debt_list(request, module):
    debts = Debt.objects.filter(user=request.user).filter(is_deleted=False)

    total_debt = sum(d.principal_amount for d in debts)
    total_interest = sum(d.total_interest for d in debts)
    gross_amount = total_debt + total_interest


    # total Paid
    total_paid = Expense.objects.filter(user=request.user).filter(category__name__iexact = 'Debt').aggregate(total_amount_paid = Sum('amount'))
    print(total_paid)
    # total_debt = sum(d.principal_amount for d in debts)


    return render(request, 'debt/debt_list.html', {
        'debts': debts,
        'total_debt': total_debt,
        'total_interest': total_interest,
        'gross_amount': gross_amount,
        'total_paid': 0,
        'total_remaining': 0,
        'module': module,
    })

@login_required
def debt_edit(request, module, pk):
    context = {}

    debt = get_object_or_404(Debt, pk=pk, user=request.user)
    form = DebtForm(request.POST or None, instance=debt)

    if form.is_valid():
        form.save()
        messages.success(request, 'Debt has been updated')
        return redirect('finance:debt_info', pk=debt.pk, module=module)

    elif form.errors:
        messages.error(request, form.errors.as_text())
        return redirect('finance:debt_info', pk=debt.pk, module=module)


    
    context['form'] = form
    context['module'] = module
    context['debt'] = debt
    context['is_edit'] = True

    return render(request, 'debt/debt_form.html',context)


@login_required
def debt_delete(request, module, pk):
    context = {}

    debt = get_object_or_404(Debt, pk=pk, user=request.user)

    if debt.expenses.exists():
        messages.error(
            request,
            "Debt cannot be deleted because EMI expenses are linked."
        )
        return redirect('finance:debt_info', pk=debt.pk)

    if request.method == "POST":
        debt.delete()
        messages.success(request, "Debt deleted successfully.")
        return redirect('finance:debt_list')
    
    context['debt'] = debt
    context['module'] = module

    return render(request, 'debt/debt_confirm_delete.html', context)



# Transactions

@login_required(login_url='homecontrol:login')
def expense_list(request, module):
    context = {}
    expenses = Expense.objects.filter(user=request.user)


    current_date = date.today()
    current_month_days = calendar.monthrange(current_date.year, current_date.month)[1]

    # from_date = current_date.replace(current_date.year, current_date.month, 1)
    # to_date = current_date.replace(current_date.year, current_date.month, current_month_days)
  
    from_date = current_date.replace(day=1)
    to_date = current_date.replace(day=current_month_days)
    


    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        expenses = expenses.filter(expense_date__lte = to_date).filter(expense_date__gte = from_date)

    else:
        expenses = expenses.filter(expense_date__range = [from_date, to_date])



    total = sum(e.amount for e in expenses)

    context['module'] = module
    context['expenses'] = expenses
    context['total'] = total
    context['from_date'] = from_date
    context['to_date'] = to_date


    return render(request, 'expenses/expense_list.html', context)


@login_required(login_url='homecontrol:login')
def expense_create(request, module):
    context = {}

    form = ExpenseForm(request.POST or None, user=request.user)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        return redirect('finance:exp_list', module=module)
    elif form.errors:
        print(form.errors.as_data())

    context['module'] = module
    context['form'] = form

    return render(request, 'expenses/expense_form.html', context)


@login_required(login_url='homecontrol:login')
def expense_update(request, module, pk):
    context = {}

    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.POST or None, instance=expense, user=request.user)

    if form.is_valid():
        form.instance.user = request.user
        form.save()
        return redirect('finance:exp_list', module=module)
    elif form.errors:
        print(form.errors.as_data())
        messages.error(request, form.errors.as_text())
        return redirect('finance:exp_edit', module=module, pk=pk)

    context['module'] = module
    context['form'] = form

    return render(request, 'expenses/expense_form.html',context)


@login_required(login_url='homecontrol:login')
def expense_delete(request, module, pk):
    context = {}

    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()

    context['module'] = module

    return redirect('finance:exp_list', module = module)

