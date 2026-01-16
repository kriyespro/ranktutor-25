from django.db import models
from django.conf import settings
from django.db.models import DecimalField
from decimal import Decimal
from core.models import TimeStampedModel


class Payment(TimeStampedModel):
    """Payment records"""
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments', limit_choices_to={'role__in': ['student', 'parent']})
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_payments', limit_choices_to={'role': 'tutor'})
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),  # Payment held for cooling period
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('razorpay', 'Razorpay'),
        ('wallet', 'Wallet'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tutor_payout = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='razorpay')
    
    # Payment Gateway Details
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_gateway_response = models.JSONField(default=dict, blank=True)
    
    # Wallet and Hold System
    is_wallet_payment = models.BooleanField(default=False)
    hold_until = models.DateTimeField(null=True, blank=True, help_text='Payment will be released after this date (1 week cooling period)')
    released_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment: ₹{self.amount} for {self.booking}"
    
    def can_be_released(self):
        """Check if payment can be released (cooling period over)"""
        if self.status != 'on_hold':
            return False
        if not self.hold_until:
            return False
        from django.utils import timezone
        return timezone.now() >= self.hold_until


class Wallet(TimeStampedModel):
    """Student wallet for pre-paid balance"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        limit_choices_to={'role__in': ['student', 'parent']}
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
    
    def __str__(self):
        return f"Wallet: {self.user.username} - ₹{self.balance}"
    
    def add_balance(self, amount, transaction_type='recharge'):
        """Add balance to wallet"""
        # Convert to Decimal to match DecimalField type
        amount_decimal = Decimal(str(amount))
        self.balance += amount_decimal
        self.save()
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            amount=amount_decimal,
            transaction_type='credit',
            description=f"Wallet {transaction_type}",
            balance_after=self.balance
        )
        return self.balance
    
    def deduct_balance(self, amount, description='Payment deduction', payment=None):
        """Deduct balance from wallet"""
        # Convert to Decimal to match DecimalField type
        amount_decimal = Decimal(str(amount))
        if self.balance >= amount_decimal:
            self.balance -= amount_decimal
            self.save()
            # Create transaction record
            WalletTransaction.objects.create(
                wallet=self,
                amount=amount_decimal,
                transaction_type='debit',
                description=description,
                balance_after=self.balance,
                payment=payment
            )
            return True
        return False


class WalletTransaction(TimeStampedModel):
    """Wallet transaction history"""
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, help_text='Balance after this transaction')
    
    # Reference to payment if this is a payment transaction
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_transactions')
    
    class Meta:
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()}: ₹{self.amount} - {self.wallet.user.username}"


class Invoice(TimeStampedModel):
    """Invoice generation"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice: {self.invoice_number}"


class Commission(TimeStampedModel):
    """Commission tracking"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='commissions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    is_paid_to_platform = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Commission'
        verbose_name_plural = 'Commissions'
    
    def __str__(self):
        return f"Commission: ₹{self.amount} from {self.payment}"


class PremiumPayment(TimeStampedModel):
    """Payments for premium features"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='premium_payments')
    
    PAYMENT_TYPES = [
        ('boost', 'Profile Boost'),
        ('featured', 'Featured Listing'),
        ('premium', 'Premium Package'),
        ('subscription', 'Study Materials Subscription'),
    ]
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Payment.STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Premium Payment'
        verbose_name_plural = 'Premium Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Premium Payment: {self.get_payment_type_display()} - ₹{self.amount}"
