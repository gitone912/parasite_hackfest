"""blogapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path("register/", views.Register, name="register"),
    path("login/", views.Login, name="login"),
    path("logout/", views.Logout, name="logout"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-survey/', views.create_survey, name='create_survey'),
    path('send-survey/', views.send_survey, name='send_survey'),
    path('survey/<uuid:unique_link>/', views.fill_survey, name='fill_survey'),
    path('submit-survey/<uuid:unique_link>/', views.submit_survey, name='submit_survey'),
    path('create-event/', views.create_event, name='create_event'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('extract-feedback',views.extract_feedbacks,name='extract_feedback'),
    path('save-feedback/', views.save_feedback, name='save_feedback'),
    path('analyze-sentiment/<int:feedback_id>/', views.analyze_sentiment, name='analyze_sentiment'),
    path('perform_sentiment_analysis/<int:feedback_id>/', views.perform_sentiment_analysis, name='perform_sentiment_analysis'),

]