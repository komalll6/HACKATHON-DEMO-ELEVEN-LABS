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
    score = models.IntegerField(null=True, blank=True) # 1-10 rating for this answer
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


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
    score = models.IntegerField(null=True, blank=True) # 1-10 rating for this answer
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    import os
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcript.text

def evaluate_and_generate_next(session_history, new_transcript, job_role):
    system_prompt = f"""
    You are a senior technical interviewer hiring for a {job_role} position. 
    Evaluate the candidate's latest response.
    Output JSON strictly:
    {{
        "current_answer_score": <1-10>,
        "current_answer_feedback": "<brief constructive feedback>",
        "next_question": "<your next interview question>"
    }}
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    for exchange in session_history:
        messages.append({"role": "assistant", "content": exchange.ai_question})
        if exchange.candidate_transcript:
            messages.append({"role": "user", "content": exchange.candidate_transcript})
            
    messages.append({"role": "user", "content": new_transcript})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={ "type": "json_object" }
    )
    return response.choices[0].message.content




import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import MockInterviewSession, InterviewExchange
from .ai_services import transcribe_audio, evaluate_and_generate_next

class ProcessInterviewTurnView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, session_id):
        audio_file = request.FILES.get('audio')
        session = MockInterviewSession.objects.get(id=session_id)
        
        # Save the incoming audio attached to the CURRENT active exchange
        current_exchange = session.exchanges.last()
        current_exchange.candidate_audio = audio_file
        current_exchange.save()

        # Transcribe
        transcript = transcribe_audio(current_exchange.candidate_audio.path)
        current_exchange.candidate_transcript = transcript
        current_exchange.save()

        # Get session history and generate next step
        history = session.exchanges.all()
        job_role = session.job_context.title if session.job_context else "Software Engineer"
        
        ai_response_raw = evaluate_and_generate_next(history, transcript, job_role)
        ai_response = json.loads(ai_response_raw)
        
        # Update current exchange with score
        current_exchange.score = ai_response.get("current_answer_score")
        current_exchange.feedback = ai_response.get("current_answer_feedback")
        current_exchange.save()

        # Create the next question exchange
        next_question = ai_response.get("next_question")
        InterviewExchange.objects.create(session=session, ai_question=next_question)

        return Response({
            "transcript": transcript,
            "feedback": current_exchange.feedback,
            "next_question": next_question
        })