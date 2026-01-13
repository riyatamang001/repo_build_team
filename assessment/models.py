from django.db import models

class SkillAssessment(models.Model):
    skill_name = models.CharField(max_length=150)
    skill_level = models.CharField(max_length=50)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.skill_name} ({self.skill_level})"

class Question(models.Model):
    assessment = models.ForeignKey(SkillAssessment, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=150)
    option_b = models.CharField(max_length=150)
    option_c = models.CharField(max_length=150)
    option_d = models.CharField(max_length=150)
    correct_option = models.CharField(max_length=1)  # A/B/C/D

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)
