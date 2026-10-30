from django.db import models
from candidates.models import CandidateProfile
from jobs.models import Job

class MockInterviewSession(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    job_context = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    overall_score = models.FloatField(null=True, blank=True)
    feedback_summary = models.TextField(blank=True)

class InterviewExchange(models.Model):
    session = models.ForeignKey(MockInterviewSession, related_name='exchanges', on_delete=models.CASCADE)
    ai_question = models.TextField()
    candidate_audio = models.FileField(upload_to='interviews/audio/', null=True, blank=True)
    candidate_transcript = models.TextField(blank=True)
    score = models.IntegerField(null=True, blank=True)  # 1-10 rating for this answer
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)