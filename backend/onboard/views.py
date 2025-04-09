from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserData

class CheckProcessingStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            user_data = UserData.objects.get(user=user)
            return Response({
                "overall_status": user_data.overall_status,
                "current_step": user_data.current_step,
                "step_status": user_data.step_status,
                "review_count": user_data.reviews.count()  # Optional: Show progress
            })
        except UserData.DoesNotExist:
            return Response({"overall_status": "not_started"}, status=404)