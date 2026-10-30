import os
import json
import asyncio
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


# --- TEST RUNNER (MAIN FUNCTION) ---
async def main():
    # 1. Dummy object history ke liye (testing purpose)
    class DummyExchange:
        def __init__(self, ai_question, candidate_transcript):
            self.ai_question = ai_question
            self.candidate_transcript = candidate_transcript

    history = [
        DummyExchange(
            ai_question="Can you explain how React hooks work under the hood?", 
            candidate_transcript="React hooks use linked lists inside fiber nodes to maintain state across renders."
        )
    ]

    job_role = "Frontend Developer"
    new_transcript = "I have 3 years of experience building scalable web apps with React and Redux."

    print("🤖 Evaluating candidate response...")
    result = await evaluate_and_generate_next(history, new_transcript, job_role)
    print("\n📦 AI Evaluation Output:")
    print(json.dumps(result, indent=2))

    # Optional: Agar aapke paas koi audio file hai toh transcription test karne ke liye yeh uncomment karein:
    # audio_path = "path_to_your_audio.mp3"
    # if os.path.exists(audio_path):
    #     print("\n🎙️ Transcribing audio...")
    #     text = await transcribe_audio(audio_path)
    #     print("Transcript:", text)

if __name__ == "__main__":
    asyncio.run(main())