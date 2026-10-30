from django.urls import path
from .views import ProcessInterviewTurnView

urlpatterns = [
    path('interview/turn/<int:session_id>/', ProcessInterviewTurnView.as_view(), name='process_interview_turn'),
]