import json
from allauth.account.adapter import DefaultAccountAdapter
from .tasks import process_user_data

from .models import UserData
from allauth.headless.adapter import DefaultHeadlessAdapter


class CustomHeadlessAdapter(DefaultHeadlessAdapter):
    def serialize_user(self, user):
        # Get the default user data
        user_data = super().serialize_user(user)

        # Add custom fields
        try:
            user_data_obj = user.userdata_set.latest('created_at')
            user_data['is_onboarded'] = user_data_obj.overall_status == "completed"
            user_data['current_step'] = user_data_obj.current_step
            user_data['step_status'] = user_data_obj.step_status
        except Exception:
            user_data['is_onboarded'] = False
            user_data['current_step'] = 1
            user_data['step_status'] = {
                "step1": "pending",
                "step2": "pending"
            }

        return user_data

class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Override the default save_user method to save additional user fields.
        """

        user = super().save_user(request, user, form, False)

        data_raw = request.body.decode('utf-8')  # Decode from bytes to string
        data = json.loads(data_raw)

        user.first_name = data.get('firstName', '')
        user.last_name = data.get('lastName', '')
        user.designation = data.get('designation', '')
        user.company_name = data.get('companyName', '')
        user.mobile_number = data.get('mobileNumber', '')
        user.website_url = data.get('websiteUrl', '')
        user.google_play_app_id = data.get('googlePlayAppId', '')
        user.apple_app_store_id = data.get('appleAppStoreId', '')
        user.apple_app_store_name = data.get('appleAppStoreName', '')


        if commit:
            user.save()
            # Create UserData instance after user is saved
            user_data = UserData.objects.create(
                user=user,
                current_step=1,
                overall_status="pending",
                step_status={
                    "step1": "pending",
                    "step2": "pending",
                }
            )
            user_data.save()
        process_user_data.delay(user.id)
        return user
