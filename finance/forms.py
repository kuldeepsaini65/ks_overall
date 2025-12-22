from django import forms
from .models import Expense, ExpenseCategory, Debt



class CategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})

    



class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = '__all__'
        exclude = ('user',)

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Home Loan, Bike EMI'
            }),

            'debt_type': forms.Select(attrs={
                'class': 'form-control',
            }),

           'interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Annual interest rate (%)',
                'step': '0.01',
                'min': '0'
            }),

            'lender': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank or person name'
            }),

            'principal_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total loan amount',
                'step': '0.01',
                'min': '0'
            }),

            'tenure_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total months',
                'min': '1'
            }),

            'emi_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Monthly EMI amount',
                'step': '0.01',
                'min': '0'
            }),

            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),

            'emi_already_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of EMIs already paid',
                'min': '0'
            }),

            'amount_already_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amount already paid',
                'step': '0.01',
                'min': '0'
            }),
        }





class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'
        exclude = ('user',)
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
            'category' : forms.Select(attrs={'class':'form-control'}),
            'payment_mode' : forms.Select(attrs={'class':'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control',
                'placeholder': 'Enter amount',
                'step': '0.01',
                'min': '0'
            }),
            'note': forms.Textarea(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ExpenseCategory.objects.filter(user=user)
