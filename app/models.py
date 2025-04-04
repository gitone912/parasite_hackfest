from django.db import models
from django.contrib.auth.models import User
import uuid

class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('text', 'Text Input'),
        ('number', 'Number Input'),
        ('choice', 'Multiple Choice'),
        ('checkbox', 'Checkbox'),
    )
    
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    choices = models.TextField(blank=True, help_text='Comma-separated choices for multiple choice questions')
    required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text

class SurveyLink(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    email = models.EmailField()
    unique_link = models.UUIDField(default=uuid.uuid4, editable=False)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    survey_link = models.ForeignKey(SurveyLink, on_delete=models.CASCADE)
    answer = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.question.question_text}"
