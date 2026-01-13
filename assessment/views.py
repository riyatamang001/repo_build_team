from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import SkillAssessment, Question, Answer
import json

def assessment_home(request):
    assessments = SkillAssessment.objects.all()
    return render(request, 'assessment/home.html', {'assessments': assessments})

def take_assessment(request, assessment_id):
    assessment = SkillAssessment.objects.get(id=assessment_id)
    questions = Question.objects.filter(assessment=assessment)

    if request.method == "POST":
        for q in questions:
            selected = request.POST.get(str(q.id))
            Answer.objects.create(
                question=q,
                selected_option=selected,
                is_correct=(selected == q.correct_option)
            )
        assessment.verified = True
        assessment.save()
        return redirect('assessment_home')

    return render(request, 'assessment/take_assessment.html', {'assessment': assessment, 'questions': questions})

@csrf_exempt
def create_assessment_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        skill_name = data.get("skill")
        skill_level = data.get("level")
        questions = data.get("questions", [])

        assessment = SkillAssessment.objects.create(
            skill_name=skill_name,
            skill_level=skill_level
        )

        for q in questions:
            Question.objects.create(
                assessment=assessment,
                question_text=q['question_text'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_option=q['correct_option']
            )

        return JsonResponse({"status": "success", "assessment_id": assessment.id})
