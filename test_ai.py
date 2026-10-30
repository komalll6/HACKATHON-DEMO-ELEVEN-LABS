import os
import json
import asyncio
from openai import AsyncOpenAI

# Safe API Client initialization
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key) if api_key else None

async def transcribe_audio(audio_file_path: str) -> str:
    if client and api_key:
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            print(f"⚠️ Whisper API Error: {e}")
    
    # Fallback transcript for demo if API fails/no credits
    return "I have experience working with MERN stack, building REST APIs, and managing databases."

async def evaluate_and_generate_next(session_history, new_transcript: str, job_role: str) -> dict:
    if client and api_key:
        try:
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
        except Exception as e:
            print(f"⚠️ OpenAI API Limit/Credit Error: {e}. Using fallback mock data.")

    # Fallback default response for hackathon demo if API fails or no credits
    return {
        "current_answer_score": 8,
        "current_answer_feedback": "Good explanation of your technical background and architecture knowledge.",
        "next_question": "Can you explain how you handle state management in large-scale React applications?"
    }

# --- TEST RUNNER (MAIN FUNCTION) ---
async def main():
    class DummyExchange:
        def __init__(self, ai_question, candidate_transcript):
            self.ai_question = ai_question
            self.candidate_transcript = candidate_transcript

    history = [
        DummyExchange(
            ai_question="Can you explain how React hooks work under the hood?", 
            candidate_transcript="React hooks use linked lists inside fiber nodes."
        )
    ]

    job_role = "Frontend Developer"
    new_transcript = "I have 3 years of experience building scalable web apps with React."

    print("🤖 Evaluating candidate response...")
    result = await evaluate_and_generate_next(history, new_transcript, job_role)
    print("\n📦 AI Evaluation Output:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())