from django import forms
from .models import Skill

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['skill', 'level']
        widgets = {
            'skill': forms.TextInput(attrs={'class': 'skill-input', 'placeholder': 'Enter skill'}),
            'level': forms.Select(attrs={'class': 'level-select'}),
        }
