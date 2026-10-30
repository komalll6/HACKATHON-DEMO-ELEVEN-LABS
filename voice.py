import os
import json
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def transcribe_audio(audio_file_path: str) -> str:
    with open(audio_file_path, "rb") as audio_file:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcript.text

async def evaluate_and_generate_next(session_history, new_transcript: str, job_role: str) -> dict:
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

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)