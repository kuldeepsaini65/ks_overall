from django.db import models

from django.conf import settings
from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from homecontrol.models import LogFolder
from django.core.exceptions import ValidationError
from django.db.models import Q


class ExpenseCategory(LogFolder):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def clean(self):
        if not self.user_id or not self.name:
            return

        name = self.name.strip().lower()

        qs = ExpenseCategory.objects.filter(name__iexact=name)

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        # 🔒 Superuser rules
        if self.user.is_superuser:
            if qs.filter(user=self.user).exists():
                raise ValidationError({
                    'name': "This Global category already exists."
                })

        # 🔒 Normal user rules
        else:
            if qs.filter(user__is_superuser=True).exists():
                raise ValidationError({
                    'name': "This category name is reserved by system and Already Exists."
                })

            if qs.filter(user=self.user).exists():
                raise ValidationError({
                    'name': "This category already Created By you."
                })

        self.name = name

    def save(self, *args, **kwargs):
        self.full_clean()  # safe now
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name.title()



DEBT_TYPE_OPTIONS = (
    ('LOAN','LOAN'),
    ('EMI','EMI'),
    ('BORROW','BORROW'),
    ('OTHER','OTHER'),
)
class Debt(LogFolder):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    debt_type = models.CharField(max_length=30, choices=DEBT_TYPE_OPTIONS)

    lender = models.CharField(max_length=100, blank=True, null=True)

    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)

    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Annual interest rate (%)",
        null=True, blank=True
    )

    tenure_months = models.PositiveIntegerField()

    emi_amount = models.DecimalField(max_digits=10, decimal_places=2)

    start_date = models.DateField()

    # For Already Paid EMI's 
    emi_already_paid = models.PositiveIntegerField(default=0)
    amount_already_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )

    is_active = models.BooleanField(default=True)
    

    @property
    def emi_left(self):
        return max(self.tenure_months - self.emi_already_paid, 0)

    @property
    def estimated_total_payable(self):
        """
        Estimated total payable using simple interest.
        This is an approximation, not bank-grade amortization.
        """
        if not self.interest_rate:
            return None

        years = self.tenure_months / 12
        interest = (
            self.principal_amount *
            (self.interest_rate / 100) *
            years
        )
        return self.principal_amount + interest


    def clean(self):
        # Basic validations
        if self.emi_already_paid > self.tenure_months:
            raise ValidationError({
                'emi_already_paid': 'Paid EMIs cannot exceed total tenure.'
            })

        if self.emi_amount < 0:
            raise ValidationError({
                'emi_amount': 'EMI amount cannot be negative.'
            })

        # 🔥 AUTO-CALCULATE already paid amount
        if self.emi_already_paid and self.emi_amount:
            self.amount_already_paid = (
                self.emi_already_paid * self.emi_amount
            )

        if self.emi_already_paid > self.tenure_months:
            raise ValidationError({
                'emi_already_paid': 'Paid EMIs cannot exceed total tenure.'
            })

        
    def save(self, *args, **kwargs):
        self.full_clean()   # calls clean()
        super().save(*args, **kwargs)



class Expense(LogFolder):
    PAYMENT_CHOICES = (
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Expense amount"
    )
    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES
    )
    expense_date = models.DateField(db_index=True)
    note = models.TextField(blank=True)



    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.user} - {self.amount} on {self.expense_date}"

