from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Feedback, Survey, Question, SurveyLink, Response, Event
import pandas as pd
from django.core.mail import send_mail
from django.conf import settings
import json
import requests

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request,'homepage.html')

def homepage(request):
    return render(request,'homepage.html')

@login_required(login_url='/login')
def dashboard(request):
    surveys = Survey.objects.filter(created_by=request.user).order_by('-created_at')
    events = Event.objects.filter(created_by=request.user).order_by('-date', '-time')
    return render(request, "dashboard.html", {'surveys': surveys, 'events': events})

@login_required(login_url='/login')
def create_survey(request):
    if request.method == 'POST':
        try:
            # Create the survey
            survey = Survey.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                created_by=request.user
            )

            # Parse the questions data from the form
            questions_data = {}
            for key, value in request.POST.items():
                if key.startswith('questions['):
                    # Extract question number and field from the name
                    parts = key.rstrip(']').split('[')
                    q_num = parts[1]
                    field = parts[2]
                    
                    if q_num not in questions_data:
                        questions_data[q_num] = {}
                    questions_data[q_num][field] = value

            # Create questions
            for q_data in questions_data.values():
                Question.objects.create(
                    survey=survey,
                    question_text=q_data['text'],
                    question_type=q_data['type'],
                    choices=q_data.get('choices', ''),
                    required=bool(q_data.get('required', False))
                )

            messages.success(request, 'Survey created successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error creating survey: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return render(request, "create_survey.html")

@login_required(login_url='/login')
def send_survey(request):
    if request.method == 'POST':
        try:
            survey_id = request.POST.get('survey_id')
            survey = get_object_or_404(Survey, id=survey_id, created_by=request.user)
            emails = []

            if 'email_file' in request.FILES:
                # Handle file upload
                email_file = request.FILES['email_file']
                if email_file.name.endswith('.csv'):
                    df = pd.read_csv(email_file)
                else:
                    df = pd.read_excel(email_file)
                email_column = df.columns[0]  # Assuming first column contains emails
                emails = df[email_column].tolist()
            else:
                # Handle manual email entries
                emails_json = request.POST.get('emails')
                if emails_json:
                    emails = json.loads(emails_json)

            if not emails:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No email addresses provided'
                }, status=400)

            # Create unique links and send emails
            successful_sends = 0
            failed_sends = 0

            for email in emails:
                try:
                    # Create unique link
                    survey_link = SurveyLink.objects.create(
                        survey=survey,
                        email=email.strip()
                    )
                    
                    # Send email
                    survey_url = request.build_absolute_uri(f'/survey/{survey_link.unique_link}/')
                    send_mail(
                        subject=f'Survey: {survey.title}',
                        message=f'Please complete this survey by clicking the following link: {survey_url}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email.strip()],
                        fail_silently=False,
                    )
                    successful_sends += 1
                except Exception as e:
                    failed_sends += 1
                    print(f"Error sending to {email}: {str(e)}")

            message = f'Survey sent successfully to {successful_sends} recipient(s).'
            if failed_sends > 0:
                message += f' Failed to send to {failed_sends} recipient(s).'

            return JsonResponse({
                'status': 'success',
                'message': message
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error sending survey: {str(e)}'
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

def fill_survey(request, unique_link):
    survey_link = get_object_or_404(SurveyLink, unique_link=unique_link)
    if survey_link.completed:
        messages.info(request, 'This survey has already been completed.')
        return render(request, 'survey_completed.html')

    survey = survey_link.survey
    questions = survey.questions.all().order_by('order')
    return render(request, 'fill_survey.html', {
        'survey': survey,
        'questions': questions,
        'survey_link': survey_link
    })

def submit_survey(request, unique_link):
    if request.method == 'POST':
        survey_link = get_object_or_404(SurveyLink, unique_link=unique_link)
        if survey_link.completed:
            return JsonResponse({'status': 'error', 'message': 'Survey already completed'})

        try:
            for question_id, answer in request.POST.items():
                if question_id.startswith('question_'):
                    question = Question.objects.get(id=question_id.replace('question_', ''))
                    Response.objects.create(
                        survey=survey_link.survey,
                        question=question,
                        survey_link=survey_link,
                        answer=answer
                    )
            
            survey_link.completed = True
            survey_link.save()
            
            messages.success(request, 'Thank you for completing the survey!')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required(login_url='/login')
def create_event(request):
    if request.method == 'POST':
        try:
            event = Event.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                event_type=request.POST['event_type'],
                date=request.POST['date'],
                time=request.POST['time'],
                capacity=request.POST['capacity'],
                bot=request.POST['bot'],
                created_by=request.user
            )
            
            # Add location or meeting link based on event type
            if request.POST['event_type'] == 'offline':
                event.location = request.POST['location']
            else:
                event.meeting_link = request.POST['meeting_link']
            
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
            return render(request, "create_event.html")

    return render(request, "create_event.html")

@login_required(login_url='/login')
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    
    if request.method == 'POST':
        try:
            event.title = request.POST['title']
            event.description = request.POST['description']
            event.event_type = request.POST['event_type']
            event.date = request.POST['date']
            event.time = request.POST['time']
            event.capacity = request.POST['capacity']
            
            if request.POST['event_type'] == 'offline':
                event.location = request.POST['location']
                event.meeting_link = None
            else:
                event.meeting_link = request.POST['meeting_link']
                event.location = None
            
            event.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    
    return render(request, "edit_event.html", {'event': event})

@login_required(login_url='/login')
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    event.delete()
    messages.success(request, 'Event deleted successfully!')
    return redirect('dashboard')

def Register(request):
    if request.method != "POST":
        return render(request, "register.html")
    username = request.POST['username']
    email = request.POST['email']
    first_name=request.POST['first_name']
    last_name=request.POST['last_name']
    password1 = request.POST['password1']
    password2 = request.POST['password2']

    if password1 != password2:
        messages.error(request, "Passwords do not match.")
        return redirect('/register')

    user = User.objects.create_user(username, email, password1)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    return render(request, 'login.html')

def Login(request):
    if request.method != "POST":
        return render(request, "login.html")
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        messages.success(request, "Successfully Logged In")
        return redirect('create_event')
    else:
        messages.error(request, "Invalid Credentials")
    return render(request, 'login.html')

def Logout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('/login')

@login_required(login_url='/login')
def extract_feedbacks(request):
    events = Event.objects.filter(created_by=request.user)
    
    if request.method == 'POST':
        search_term = request.POST.get('search_term', '@openai')
        max_tweets = int(request.POST.get('max_tweets', 10))
        event_id = request.POST.get('event_id')
        
        event = None
        if event_id:
            event = get_object_or_404(Event, id=event_id, created_by=request.user)
        
        # API endpoint
        api_url = 'http://192.168.92.100:8080/dummytweets'
        
        # Prepare payload
        payload = {
            "search_term": search_term,
            "max_tweets": max_tweets,
            "username": "Gamma231192",
            "password": "sachin03.k"   
        }
        
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            response_data = response.json()
            tweets = response_data.get('tweets', [])  # 
            
            # Save all tweets as a single feedback entry
            Feedback.objects.create(
                event=event,
                user=request.user,
                tag=search_term,
                feedback_data=tweets
            )
            
            messages.success(request, f'Successfully saved {len(tweets)} feedback items')
            return render(request, 'extract_feedback.html', {
    'tweets': tweets,
    'search_term': search_term,
    'tweets_json': json.dumps(response_data, indent=2),  # Keep the original structure for JSON display
    'events': events,
    'event_id': event_id
})
        except requests.exceptions.RequestException as e:
            messages.error(request, f"API Error: {str(e)}")
            return render(request, 'extract_feedback.html', {'error': str(e), 'events': events})
            
    return render(request, 'extract_feedback.html', {'events': events})

@login_required(login_url='/login')
def save_feedback(request):
    if request.method == 'POST':
        tweets_data = request.POST.get('tweets_data')
        search_term = request.POST.get('search_term')
        event_id = request.POST.get('event_id')
        
        event = None
        if event_id and event_id.isdigit():  # Check if event_id is valid
            event = get_object_or_404(Event, id=int(event_id), created_by=request.user)
        
        try:
            # Save feedback
            feedback = Feedback.objects.create(
                event=event,
                user=request.user,
                tag=search_term,
                feedback_data=json.loads(tweets_data)
            )
            
            return redirect('analyze_sentiment', feedback_id=feedback.id)
        except Exception as e:
            messages.error(request, f"Error saving feedback: {str(e)}")
            return redirect('extract_feedback')
    
    return redirect('extract_feedbacks')

@login_required(login_url='/login')
def analyze_sentiment(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    tweets = feedback.feedback_data
    
    # Check if 'tweets' is a dictionary with a 'tweets' key (based on your data structure)
    if isinstance(tweets, dict) and 'tweets' in tweets:
        tweets = tweets['tweets']
    
    # The actual sentiment analysis will be done via AJAX to show loading screen
    # Just pass the raw tweets to the template
    
    return render(request, 'analyse_sentiment.html', {
        'feedback': feedback,
        'tweets': tweets,
        'feedback_id': feedback_id
    })

@login_required(login_url='/login')
def perform_sentiment_analysis(request, feedback_id):
    """API endpoint that performs the actual sentiment analysis"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    feedback = get_object_or_404(Feedback, id=feedback_id, user=request.user)
    tweets_data = feedback.feedback_data
    
    # Check if 'tweets' is a dictionary with a 'tweets' key (based on your data structure)
    if isinstance(tweets_data, dict) and 'tweets' in tweets_data:
        tweets = tweets_data['tweets']
    else:
        tweets = tweets_data
    
    try:
        # Import required libraries
        import pickle
        import re
        import os
        from tensorflow.keras.models import load_model
        from tensorflow.keras.preprocessing.sequence import pad_sequences
        import numpy as np
        
        # Get the absolute path to the model files
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(BASE_DIR, 'ml_models', 'sentiment_model.h5')
        tokenizer_path = os.path.join(BASE_DIR, 'ml_models', 'tokenizer.pkl')
        
        # Load the saved model and tokenizer
        model = load_model(model_path)
        with open(tokenizer_path, "rb") as f:
            tokenizer = pickle.load(f)
        
        # Define cleaning function
        def clean_tweet(tweet):
            tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
            tweet = re.sub(r'\@\w+|\#','', tweet)
            tweet = re.sub(r'\W', ' ', tweet)
            tweet = re.sub(r'\d', ' ', tweet)
            tweet = re.sub(r'\s+', ' ', tweet)
            tweet = tweet.strip()
            return tweet
        
        # Extract content from tweets
        tweet_contents = [tweet['content'] for tweet in tweets]
        
        # Clean and preprocess
        cleaned_tweets = [clean_tweet(tweet.lower()) for tweet in tweet_contents]
        sequences = tokenizer.texts_to_sequences(cleaned_tweets)
        
        # Use the same maxlen from training
        maxlen = 56  # Replace with your actual maxlen value if different
        padded_sequences = pad_sequences(sequences, maxlen=maxlen, padding='post')
        
        # Predict
        predictions = model.predict(padded_sequences)
        
        # Decode predictions
        label_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive', 3: 'Irrelevant', 4: 'Mixed'}
        
        # Combine predictions with original tweets
        results = []
        for i, tweet in enumerate(tweets):
            sentiment = label_map[np.argmax(predictions[i])]
            confidence = float(np.max(predictions[i]))  # Convert numpy float to Python float for JSON serialization
            
            tweet_with_sentiment = tweet.copy()
            tweet_with_sentiment['sentiment'] = sentiment
            tweet_with_sentiment['confidence'] = confidence
            results.append(tweet_with_sentiment)
        
        # Update the feedback object with analysis results
        feedback.analyzed_data = results
        feedback.is_analyzed = True
        feedback.save()
        
        return JsonResponse({'status': 'success', 'results': results})
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required(login_url='/login')
def crowdDetection(request):
    return render(request, 'crowdDetection.html')



