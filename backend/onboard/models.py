from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class UserData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    overall_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")],
        default="pending"
    )
    current_step = models.IntegerField(default=1)  # Tracks current step (1-4)
    step_status = models.JSONField(default=dict)  # Tracks status of each step
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Initialize step_status if empty
        if not self.step_status:
            self.step_status = {
                "step1": "pending",
                "step2": "pending",
            }
        super().save(*args, **kwargs)




class CustomUser(AbstractUser):
    designation = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True, unique=False)
    website_url = models.URLField(max_length=255, blank=True, null=True)
    google_play_app_id = models.CharField(max_length=255, blank=True, null=True)
    apple_app_store_id = models.CharField(max_length=255, blank=True, null=True)
    apple_app_store_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.email  # Display email in admin panel

