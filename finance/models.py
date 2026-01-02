from django.db import models

from django.conf import settings
from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from homecontrol.models import LogFolder
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP

class ExpenseCategory(LogFolder):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)

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

    debt_type = models.CharField(
        max_length=30,
        choices=DEBT_TYPE_OPTIONS
    )

    lender = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    principal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Monthly interest rate (%)",
        null=True,
        blank=True
    )

    tenure_months = models.PositiveIntegerField()

    emi_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    start_date = models.DateField()

    # 🔥 OPENING BALANCE (paid before app usage)
    emi_already_paid = models.PositiveIntegerField(
        default=0,
        help_text="EMIs paid before registering on the app"
    )

    amount_already_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total amount paid before using the app"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"

    # ------------------------------------------------------------------
    # 🔹 VALIDATIONS
    # ------------------------------------------------------------------
    def clean(self):
        if self.emi_already_paid > self.tenure_months:
            raise ValidationError({
                'emi_already_paid': 'Paid EMIs cannot exceed total tenure.'
            })

        if self.emi_amount <= 0:
            raise ValidationError({
                'emi_amount': 'EMI amount must be greater than zero.'
            })

        if self.amount_already_paid < 0:
            raise ValidationError({
                'amount_already_paid': 'Already paid amount cannot be negative.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()  # ensures clean() is called
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # 🔹 DERIVED / CALCULATED PROPERTIES (SOURCE OF TRUTH = Expense)
    # ------------------------------------------------------------------


    @property
    def expense_paid_amount(self):
        """
        Total amount paid via app (Expense table)
        """
        total = (
            self.expense_debt
            .filter(category__slug='debt')
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0.00')
        )

        return total.quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
    
    @property
    def debt_status_tag(self):
        opening_emi = self.emi_already_paid
        expense_emi = self.expense_debt.filter(category__slug='debt').count()
        total_paid_emi = opening_emi + expense_emi
        if total_paid_emi < self.tenure_months:
            tag = 'Active'
        elif total_paid_emi >= self.tenure_months:
            tag = 'Closed'
        return tag
    
    @property
    def badge_status(self):
        return 'bg-warning p-2' if self.debt_status_tag == 'Active' else 'bg-success p-2'

    
    @property
    def emi_left(self):
        opening_emi = self.emi_already_paid
        expense_emi = self.expense_debt.filter(category__slug='debt').count()
        total_paid_emi = opening_emi + expense_emi
        total_pending_emi = self.tenure_months - total_paid_emi
        return total_pending_emi

    @property
    def monthly_interest(self):
        if not self.interest_rate:
            return Decimal('0.00')

        interest = (
            self.principal_amount *
            (self.interest_rate / Decimal('100'))
        )
        return interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def total_interest(self):
        return (
            self.monthly_interest *
            Decimal(self.tenure_months)
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @property
    def gross_amount(self):
        """
        Principal + total interest
        """
        total = self.principal_amount + self.total_interest
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    

    @property
    def net_paid(self):
        """
        Total amount already paid (opening + app payments)
        """
        total = self.amount_already_paid + self.expense_paid_amount
        return total.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    

    @property
    def net_remaining(self):
        """
        Gross amount minus paid amount
        """
        remaining = self.gross_amount - self.net_paid

        return max(
            remaining.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            Decimal('0.00')
        )


    

PAYMENT_CHOICES = (
    ('cash', 'Cash'),
    ('upi', 'UPI'),
    ('card', 'Card'),
    ('bank', 'Bank Transfer'),
)

EXPENSE_TYPE = (
        ('normal', 'Normal Expense'),
        ('debt_payment', 'Debt Payment'),
    )


class Expense(LogFolder):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # expense_type = models.CharField(
    #     max_length=20,
    #     choices=EXPENSE_TYPE,
    #     default='normal'
    # )

    debt = models.ForeignKey(Debt, null=True, blank=True, on_delete=models.SET_NULL, related_name='expense_debt')


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


    def clean(self):
        if self.category and self.category.slug == 'debt' and not self.debt:
            raise ValidationError("Debt must be selected for Debt category expenses.")

        if self.category and self.category.slug != 'debt' and self.debt:
            raise ValidationError("Debt can only be selected for Debt category.")

    def __str__(self):
        return f"{self.user} - {self.amount} on {self.expense_date}"
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

