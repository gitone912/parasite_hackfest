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

class Event(models.Model):
    EVENT_TYPES = (
        ('online', 'Online Event'),
        ('offline', 'Offline Event'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200, blank=True, null=True)  # For offline events
    meeting_link = models.URLField(blank=True, null=True)  # For online events
    capacity = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.CharField(max_length=200)
    feedback_data = models.JSONField()
    search_date = models.DateTimeField(auto_now_add=True)
    analyzed = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback for {self.tag} by {self.user.username}"
