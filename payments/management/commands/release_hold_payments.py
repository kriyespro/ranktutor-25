from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import Payment


class Command(BaseCommand):
    help = 'Release payments that are on hold after cooling period (1 week)'

    def handle(self, *args, **options):
        # Get all payments that can be released
        payments_to_release = Payment.objects.filter(
            status='on_hold',
            hold_until__lte=timezone.now()
        )
        
        count = 0
        for payment in payments_to_release:
            payment.status = 'completed'
            payment.released_at = timezone.now()
            if not payment.paid_at:
                payment.paid_at = timezone.now()
            payment.save()
            count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Released payment {payment.id} - ₹{payment.tutor_payout} for {payment.tutor.username}'
                )
            )
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No payments to release at this time.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully released {count} payment(s).')
            )

