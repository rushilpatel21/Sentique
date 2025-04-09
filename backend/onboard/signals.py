from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .tasks import process_user_data

@receiver(user_signed_up)
def start_data_processing(sender, request, user, **kwargs):
    # Trigger the task after user signs up
    process_user_data.delay(user.id)