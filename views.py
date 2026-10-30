import asyncio
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
        if audio_file:
            current_exchange.candidate_audio = audio_file
            current_exchange.save()

        audio_path = current_exchange.candidate_audio.path if current_exchange.candidate_audio else None

        # Helper async runner for Django sync view
        async def run_pipeline():
            # 1. Transcribe audio
            if audio_path:
                transcript = await transcribe_audio(audio_path)
            else:
                transcript = "Candidate provided text response."
            
            current_exchange.candidate_transcript = transcript
            current_exchange.save()

            # 2. Get session history and generate evaluation
            history = session.exchanges.all()
            job_role = session.job_context.title if session.job_context else "Software Engineer"
            
            ai_response = await evaluate_and_generate_next(history, transcript, job_role)
            return transcript, ai_response

        # Run the async code inside Django sync view
        transcript, ai_response = asyncio.run(run_pipeline())
        
        # Update current exchange with score and feedback
        current_exchange.score = ai_response.get("current_answer_score")
        current_exchange.feedback = ai_response.get("current_answer_feedback")
        current_exchange.save()

        # Create the next question exchange in database
        next_question = ai_response.get("next_question")
        InterviewExchange.objects.create(session=session, ai_question=next_question)

        return Response({
            "transcript": transcript,
            "feedback": current_exchange.feedback,
            "next_question": next_question
        })