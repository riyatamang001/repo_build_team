import json
import re
from django.shortcuts import render
from django.http import JsonResponse
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from skills.models import Skill
from .models import ChatMessage
import google.generativeai as genai

# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)


# ------------------------------
# Helper: Extract JSON array from AI output
# ------------------------------
def extract_json_array(text):
    """Extracts the first JSON array from AI output, even if wrapped in code fences."""
    if not text:
        raise ValueError("Empty AI output")

    text = text.strip()

    # Remove ```json or ``` wrapper
    if text.startswith("```"):
        text = re.sub(r"```json|```", "", text).strip()

    # Find JSON array boundaries
    first = text.find("[")
    last = text.rfind("]")

    if first == -1 or last == -1:
        raise ValueError("No JSON array found in AI output.")

    json_str = text[first:last + 1]

    return json.loads(json_str)


# ------------------------------
# Chatbot view (for chat messages)
# ------------------------------
@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()
            if not user_message:
                return JsonResponse({'response': "Please type a message."})

            # Call Gemini AI
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                ai_response = model.generate_content(user_message)
                bot_response = ai_response.text
            except Exception as e:
                print("Gemini API error:", e)
                bot_response = f"(Fallback) You said: {user_message}"

            # Save chat to database
            ChatMessage.objects.create(
                user_message=user_message,
                bot_response=bot_response
            )

            return JsonResponse({'response': bot_response})

        except Exception as e:
            return JsonResponse({'response': f"Error: {str(e)}"})

    # GET request → render page
    messages = ChatMessage.objects.all().order_by('created_at')
    return render(request, 'ai_chat/chat.html', {'messages': messages})


# ------------------------------
# AI Assessment view
# ------------------------------
def ai_assessment(request):
    """
    Generates AI-based multiple choice questions (MCQs) for skills.
    Uses session 'saved_skills' if available, otherwise all skills from DB.
    """
    # Step 1: Get skills
    saved_skills = request.session.get('saved_skills')
    if saved_skills:
        skills_to_use = saved_skills
    else:
        skills_to_use = [{'skill': s.skill, 'level': s.level} for s in Skill.objects.all()]

    results = []
    model = genai.GenerativeModel("gemini-2.5-pro")

    for s in skills_to_use:
        # Step 2: Prepare prompt
        prompt = f"""
        Generate exactly 3 multiple-choice questions.
        Skill: {s['skill']}
        Level: {s['level']}

        Return ONLY a JSON array:
        [
          {{
            "question_text": "...",
            "option_a": "A...",
            "option_b": "B...",
            "option_c": "C...",
            "option_d": "D...",
            "correct_option": "A/B/C/D"
          }}
        ]
        """
        try:
            # Step 3: Call AI
            ai_res = model.generate_content(prompt)
            raw_output = ai_res.text.strip()

            print("\nRaw AI Output:", raw_output)  # Debugging

            # Step 4: Extract JSON
            questions = extract_json_array(raw_output)

            if not isinstance(questions, list):
                raise ValueError("AI did not return a valid JSON list.")

        except Exception as e:
            print("Gemini/JSON Parsing Error:", e)

            # Step 5: Fallback questions if AI fails
            questions = [
                {
                    "question_text": f"{s['skill']} sample question {i}",
                    "option_a": "Option A",
                    "option_b": "Option B",
                    "option_c": "Option C",
                    "option_d": "Option D",
                    "correct_option": "A"
                }
                for i in range(1, 4)
            ]

        # Step 6: Normalize for template (convert letters to index)
        render_questions = []
        session_store = {}
        for idx, q in enumerate(questions, start=1):
            qid = f"q{idx}"
            options = [
                q.get("option_a", "Option A"),
                q.get("option_b", "Option B"),
                q.get("option_c", "Option C"),
                q.get("option_d", "Option D")
            ]
            correct = q.get("correct_option", "A").upper()
            correct_index = {"A":0,"B":1,"C":2,"D":3}.get(correct, 0)

            # Store for session (grading later)
            session_store[qid] = {
                "question_text": q.get("question_text", ""),
                "options": options,
                "correct_index": correct_index,
                "explanation": q.get("explanation", "")
            }

            # Render version (no correct answer)
            render_questions.append({
                "id": qid,
                "question_text": q.get("question_text", ""),
                "options": options
            })

        # Save session key
        session_key = f"mcq_{uuid.uuid4().hex}"
        request.session[session_key] = session_store
        request.session.modified = True

        results.append({
            "skill": s['skill'],
            "level": s['level'],
            "session_key": session_key,
            "questions": render_questions
        })

    # Clear saved_skills from session after use
    if 'saved_skills' in request.session:
        del request.session['saved_skills']

    return render(request, "ai_chat/assessment.html", {"results": results})
