import uuid
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest
from .models import Skill
from .forms import SkillForm

# View to list all saved skills
def skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'skills/skill_list.html', {'skills': skills})

# Add skill and redirect to AI assessment
@require_http_methods(["GET", "POST"])
def add_skill(request):
    if request.method == 'POST':
        skills = request.POST.getlist('skill')
        levels = request.POST.getlist('level')

        saved_skills = []

        for name, level in zip(skills, levels):
            if name.strip():
                # Save skill to DB
                Skill.objects.create(skill=name, level=level)
                saved_skills.append({'skill': name, 'level': level})

        # Save to session for AI assessment
        request.session['saved_skills'] = saved_skills
        request.session.modified = True

        # Redirect to AI Chat assessment page
        return redirect('assessment')  # matches name in ai_chat/urls.py

    # GET request → show skill form
    form = SkillForm()
    return render(request, 'skills/add_skill.html', {'form': form})

# Submit assessment (grading)
@require_http_methods(["POST"])
def submit_assessment(request):
    session_key = request.POST.get("session_key")
    if not session_key:
        return HttpResponseBadRequest("Missing session key.")

    stored = request.session.get(session_key)
    if not stored:
        return HttpResponseBadRequest("Assessment session expired or invalid.")

    total = 0
    correct_count = 0
    detailed = []

    for qid, meta in stored.items():
        total += 1
        try:
            user_choice = int(request.POST.get(f"q_{qid}"))
        except:
            user_choice = None

        correct_index = int(meta.get("correct_index", 0))
        is_correct = (user_choice is not None and user_choice == correct_index)
        if is_correct:
            correct_count += 1

        detailed.append({
            "qid": qid,
            "question_text": meta.get("question_text"),
            "options": meta.get("options"),
            "user_choice": user_choice,
            "correct_index": correct_index,
            "is_correct": is_correct,
            "explanation": meta.get("explanation", "")
        })

    # Clear session
    try:
        del request.session[session_key]
    except KeyError:
        pass
    request.session.modified = True

    score = {"score": correct_count, "total": total, "detailed": detailed}

    return render(request, "skills/assessment_score.html", {"score_data": score})
